import pandas as pd
import simpy

def get_exam_no_1ss(env, patient, clinic, rg, pct_screen_mammo_scheduled, pct_dx_mammo_us_scheduled,
              pct_dx_mammo_scheduled, pct_dx_us_scheduled, pct_us_guided_bx_scheduled):
    # patient arrives to clinic
    arrival_ts = env.now

    # generate a random number
    number = rg.random()

    # initiate time stamp logs
    got_screen_scanner_ts = pd.NA
    got_dx_scanner_ts, got_us_machine_ts, got_us_machine_after_dx_scanner_ts = pd.NA, pd.NA, pd.NA
    got_us_machine_bx_ts, got_scanner_bx_ts = pd.NA, pd.NA
    got_scanner_after_us_bx_ts, got_dx_scanner_before_us_ts = pd.NA, pd.NA

    release_screen_scanner_ts = pd.NA
    release_dx_scanner_us_machine_ts, release_dx_scanner_ts, release_us_machine_ts = pd.NA, pd.NA, pd.NA
    release_us_machine_after_bx_ts, release_scanner_after_bx_ts = pd.NA, pd.NA
    release_scanner_after_post_bx_mammo_ts, release_dx_scanner_before_us_ts = pd.NA, pd.NA

    # request a checkin staff
    with clinic.checkin_staff.request() as request:
        yield request
        got_checkin_staff_ts = env.now
        yield env.process(clinic.pt_checkin(patient))
        release_checkin_staff_ts = env.now

    # request a public wait room
    with clinic.public_wait_room.request() as request:
        yield request
        got_public_wait_room_ts = env.now
        yield env.process(clinic.use_public_wait_room(patient))
        release_public_wait_room_ts = env.now

    # request consent room (bx only)
    if number > pct_dx_us_scheduled:
        with clinic.consent_staff.request() as request:
            yield request
            got_consent_staff_ts = env.now
            yield env.process(clinic.consent_patient(patient))
            release_consent_staff_ts = env.now
    else:
        got_consent_staff_ts = pd.NA
        release_consent_staff_ts = pd.NA

    # request change room
    with clinic.change_room.request() as request:
        yield request
        got_change_room_ts = env.now
        yield env.process(clinic.use_change_room(patient))
        release_change_room_ts = env.now

    # request gowned wait room
    with clinic.gowned_wait_room.request() as request:
        yield request
        got_gowned_wait_room_ts = env.now
        yield env.process(clinic.use_gowned_wait_room((patient)))
        release_gowned_wait_room_ts = env.now

    # 1.screen mammo
    if number <= pct_screen_mammo_scheduled:
        patient_type = 'screen'
        with clinic.scanner.request() as request:
            yield request
            got_screen_scanner_ts = env.now
            yield env.process(clinic.get_screen_mammo(patient))
            release_screen_scanner_ts = env.now

    # 2. dx mammo + dx us
    if pct_screen_mammo_scheduled < number <= pct_dx_mammo_us_scheduled:
        patient_type = 'dx mammo us'
        with clinic.scanner.request() as request:
            yield request
            got_dx_scanner_before_us_ts = env.now
            yield env.process(clinic.get_dx_mammo(patient))
            release_dx_scanner_before_us_ts = env.now
        with clinic.us_machine.request() as request:
            yield request
            got_us_machine_after_dx_scanner_ts = env.now
            yield env.process(clinic.get_dx_us(patient))
            release_dx_scanner_us_machine_ts = env.now

    # 3. dx mammo
    if pct_dx_mammo_us_scheduled < number <= pct_dx_mammo_scheduled:
        patient_type = 'dx mammo'
        with clinic.scanner.request() as request:
            yield request
            got_dx_scanner_ts = env.now
            yield env.process(clinic.get_dx_mammo(patient))
            release_dx_scanner_ts = env.now

    # 4. dx us
    if pct_dx_mammo_scheduled < number <= pct_dx_us_scheduled:
        patient_type = 'dx us'
        with clinic.us_machine.request() as request:
            yield request
            got_us_machine_ts = env.now
            yield env.process(clinic.get_dx_us(patient))
            release_us_machine_ts = env.now

    # 5. us-guided bx
    if pct_dx_us_scheduled < number <= pct_us_guided_bx_scheduled:
        patient_type = 'us bx'
        with clinic.us_machine.request() as request:
            yield request
            got_us_machine_bx_ts = env.now
            yield env.process(clinic.get_us_guided_bx(patient))
            release_us_machine_after_bx_ts = env.now

        # post bx mammo
        with clinic.scanner.request() as request:
            yield request
            got_scanner_after_us_bx_ts = env.now
            yield env.process(clinic.get_dx_mammo(patient))
            release_scanner_after_post_bx_mammo_ts = env.now

    # 6. mammo-guided bx
    if number > pct_us_guided_bx_scheduled:
        patient_type = 'mammo bx'
        with clinic.scanner.request() as request:
            yield request
            got_scanner_bx_ts = env.now
            yield env.process(clinic.get_mammo_guided_bx(patient))
            yield env.process(clinic.get_dx_mammo(patient)) # post bx mammo
            release_scanner_after_post_bx_mammo_ts = env.now

    # request a change room
    with clinic.change_room.request() as request:
        yield request
        got_checkout_change_room_ts = env.now
        yield env.process(clinic.use_change_room(patient))
        release_checkout_change_room_ts = env.now

    exit_system_ts = env.now

    # create dict of timestamps
    timestamps = {'patient_id': patient,
                  'patient_type': patient_type,
                  'arrival_ts': arrival_ts,
                  'got_checkin_staff_ts': got_checkin_staff_ts,
                  'release_checkin_staff_ts': release_checkin_staff_ts,
                  'got_public_wait_room_ts': got_public_wait_room_ts,
                  'release_public_wait_room_ts': release_public_wait_room_ts,
                  'got_consent_staff_ts': got_consent_staff_ts,
                  'release_consent_staff_ts': release_consent_staff_ts,
                  'got_change_room_ts': got_change_room_ts,
                  'release_change_room_ts': release_change_room_ts,
                  'got_gowned_wait_room_ts': got_gowned_wait_room_ts,
                  'release_gowned_wait_room_ts': release_gowned_wait_room_ts,
                  'got_screen_scanner_ts': got_screen_scanner_ts,
                  'release_screen_scanner_ts': release_screen_scanner_ts,
                  'got_dx_scanner_ts': got_dx_scanner_ts,
                  'release_dx_scanner_ts': release_dx_scanner_ts,
                  'got_us_machine_ts': got_us_machine_ts,
                  'release_us_machine_ts': release_us_machine_ts,
                  'got_dx_scanner_before_us_ts': got_dx_scanner_before_us_ts,
                  'release_dx_scanner_before_us_ts': release_dx_scanner_before_us_ts,
                  'got_us_machine_after_dx_scanner_ts': got_us_machine_after_dx_scanner_ts,
                  'release_dx_scanner_us_machine_ts': release_dx_scanner_us_machine_ts,
                  'got_us_machine_bx_ts': got_us_machine_bx_ts,
                  'release_us_machine_after_bx_ts': release_us_machine_after_bx_ts,
                  'got_scanner_bx_ts': got_scanner_bx_ts,
                  'got_scanner_after_us_bx_ts': got_scanner_after_us_bx_ts,
                  'release_scanner_after_post_bx_mammo_ts': release_scanner_after_post_bx_mammo_ts,
                  'got_checkout_change_room_ts': got_checkout_change_room_ts,
                  'release_checkout_change_room_ts': release_checkout_change_room_ts,
                  'exit_system_ts': exit_system_ts}
    clinic.timestamps_list.append(timestamps)

def run_clinic_no_1ss(env, clinic, mean_interarrival_time, rg, pct_dx_mammo_scheduled,
               pct_screen_mammo_scheduled, pct_dx_mammo_us_scheduled,
                pct_dx_us_scheduled, pct_us_guided_bx_scheduled, seed=None,
               stoptime=simpy.core.Infinity, max_arrivals=simpy.core.Infinity):
    # create a counter to keep track of num of pts
    # serve as unique pt id
    patient = 0

    # loop for generating patients
    while env.now < stoptime and patient < max_arrivals:
        # generate next interarrival time
        iat = rg.exponential(mean_interarrival_time)

        yield env.timeout(iat)

        patient += 1

        env.process(get_exam_no_1ss(env, patient, clinic, rg, pct_screen_mammo_scheduled, pct_dx_mammo_us_scheduled,
              pct_dx_mammo_scheduled, pct_dx_us_scheduled, pct_us_guided_bx_scheduled))
