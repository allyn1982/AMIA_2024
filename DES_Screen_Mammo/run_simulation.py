import argparse
import random
import pandas as pd
import simpy
from numpy.random._generator import default_rng
from utils import MammoClinic, compute_durations
from clinic_wf_no_1ss import get_exam_no_1ss, run_clinic_no_1ss
from clinic_wf_1ss import get_exam_1ss, run_clinic_1ss


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run mammography clinic simulation with flexible parameters.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--no_1ss", choices=["True", "False"], default="True",
                        help="Specify 'True' to use no 1-step simulation or 'False' to enable 1-step simulation (default is 'True')")
    parser.add_argument("--num_scanner", type=int, default=3, help="Number of mammography scanners")
    parser.add_argument("--num_us_machine", type=int, default=2, help="Number of ultrasound machines")
    parser.add_argument("--stoptime", type=float, default=8.5, help="Time to stop the simulation in hours")
    parser.add_argument("--num_iteration", type=int, default=10, help="Number of simulation iterations")
    return parser.parse_args()


def main(seed, no_1ss, num_scanner, num_us_machine, stoptime):
    no_1ss = no_1ss == "True"  # Convert to boolean
    rg = default_rng(seed=seed)

    # specify clinic parameters
    patients_per_hour = 6
    mean_interarrival_time = 1.0 / patients_per_hour
    num_checkin_staff = 3
    num_public_wait_room = 20
    num_consent_staff = 1
    num_change_room = 3
    num_gowned_wait_room = 5

    # specify prob of each exam
    pct_screen_mammo_scheduled = 0.503
    pct_dx_mammo_us_scheduled = 0.863
    pct_dx_mammo_scheduled = 0.908
    pct_dx_us_scheduled = 0.953
    pct_us_guided_bx_scheduled = 0.993

    if not no_1ss:
        pct_dx_after_ai = rg.normal(0.12, 0.05)
        pct_screen_mammo_scheduled *= (1 - pct_dx_after_ai)
        pct_screen_mammo_after_ai_dx_mammo_us_scheduled = pct_screen_mammo_scheduled + pct_screen_mammo_scheduled * pct_dx_after_ai * 0.8
        pct_screen_mammo_after_ai_dx_mammo_scheduled = pct_screen_mammo_after_ai_dx_mammo_us_scheduled + pct_screen_mammo_scheduled * pct_dx_after_ai * 0.1
        pct_screen_mammo_after_ai_us_scheduled = pct_screen_mammo_scheduled

    # initialize simpy environment
    env = simpy.Environment()

    clinic = MammoClinic(env, num_checkin_staff, num_public_wait_room, num_consent_staff,
                         num_change_room, num_gowned_wait_room,
                         num_scanner, num_us_machine, rg)

    if no_1ss:
        env.process(run_clinic_no_1ss(env, clinic, mean_interarrival_time,
                                      rg, pct_dx_mammo_scheduled,
                                      pct_screen_mammo_scheduled, pct_dx_mammo_us_scheduled,
                                      pct_dx_us_scheduled, pct_us_guided_bx_scheduled, stoptime=stoptime))
    else:
        env.process(run_clinic_1ss(env, clinic, mean_interarrival_time,
                                   rg, pct_screen_mammo_scheduled,
                                   pct_screen_mammo_after_ai_dx_mammo_us_scheduled,
                                   pct_screen_mammo_after_ai_dx_mammo_scheduled,
                                   pct_screen_mammo_after_ai_us_scheduled,
                                   pct_dx_mammo_us_scheduled,
                                   pct_dx_mammo_scheduled,
                                   pct_dx_us_scheduled, pct_us_guided_bx_scheduled,
                                   stoptime=stoptime))

    env.run()

    # create output files
    clinic_patient_log_df = pd.DataFrame(clinic.timestamps_list)
    output_folder = './Output_no_1ss/' if no_1ss else './Output_1ss/'
    output_filename = f'clinic_patient_log_df_{"no_1ss" if no_1ss else "1ss"}_seed_{seed}.csv'
    clinic_patient_log_df.to_csv(output_folder + output_filename, index=False)

    # Note simulation end time
    end_time = env.now
    print(f"Simulation ended at time {end_time}")
    return end_time


if __name__ == "__main__":
    args = parse_arguments()

    random.seed(args.seed)
    count = 0
    count_num_skipped = 0
    seed_list = []

    while count < args.num_iteration:
        seed = random.randint(1, 500)
        if seed not in seed_list:
            try:
                clinic_end_time = main(seed=seed, no_1ss=args.no_1ss,
                                       num_scanner=args.num_scanner,
                                       num_us_machine=args.num_us_machine,
                                       stoptime=args.stoptime)

                # Load and compute durations
                output_folder = './Output_no_1ss/' if args.no_1ss == "True" else './Output_1ss/'
                output_filename = f'clinic_patient_log_df_{"no_1ss" if args.no_1ss == "True" else "1ss"}_seed_{seed}.csv'
                clinic_patient_log_df = pd.read_csv(output_folder + output_filename)
                clinic_patient_log_df = compute_durations(clinic_patient_log_df, no_1ss=(args.no_1ss == "True"))
                clinic_patient_log_df.to_csv(output_folder + output_filename, index=False)

                print('No pts per day for baseline workflow: ', clinic_patient_log_df.shape[0])
                count += 1
            except Exception as e:
                print(f'Model skipped for seed {seed}: {e}')
                count_num_skipped += 1
            seed_list.append(seed)

    print('--------------------------------------------------')
    print('Num of skipped simulations: ', count_num_skipped)
