<h2 align="center">Using Discrete Event Simulation to Design and Assess an AI-aided Workflow for Same-day Diagnostic Testing of Women Undergoing Breast Screening

## AMIA 2024 Informatics Summit Paper
  
Yannan Lin, MD, MPH, PhD1, Anne C. Hoyt, MD2, Vladimir G. Manuel, MD3,4, Moira Inkelas, MPH, PhD4,5, William Hsu, PhD1,6

1 Medical & Imaging Informatics, Department of Radiological Sciences, David Geffen School of Medicine at UCLA, Los Angeles, CA, USA; 
2 Department of Radiological Sciences, David Geffen School of Medicine at UCLA, Los Angeles, CA, USA; 
3 Department of Family Medicine, David Geffen School of Medicine at UCLA, Los Angeles, CA, USA; 
4 UCLA Clinical and Translational Science Institute, Los Angeles, CA, USA; 
5 Department of Health Policy and Management, UCLA Fielding School of Public Health, Los Angeles, CA, USA;
6 Department of Bioengineering, University of California, Los Angeles, CA, USA

## Introduction
The process of patients waiting for diagnostic examinations after an abnormal screening mammogram is inefficient and anxiety-inducing. Artificial intelligence (AI)-aided interpretation of screening mammography could reduce the number of recalls after screening. We proposed a same-day diagnostic workup to alleviate patient anxiety by employing an AI-aided interpretation to reduce unnecessary diagnostic testing after an abnormal screening mammogram. However, the potential unintended consequences of introducing this workflow in a high-volume breast imaging center are unknown. This repo allows the users to explore different scenarios of the proposed same-day diagnostic workup by changing the number of mammography and ultrasound machines and imaging center operating hours. This enables us to further determine potential changes on patient waiting times or lenght of stay in the clinia. The supplemental materials of the paper is titled AMIA_supplemental materials.docx in this repo. 

Link to the paper: https://pubmed.ncbi.nlm.nih.gov/38827101/ 

Please cite: Lin Y, Hoyt AC, Manuel VG, Inkelas M, Hsu W. Using Discrete Event Simulation to Design and Assess an AI-aided Workflow for Same-day Diagnostic Testing of Women Undergoing Breast Screening. AMIA Jt Summits Transl Sci Proc. 2024;2024:314-323. Published 2024 May 31.

The baseline and same-day diagnostic workup workflow is illustrated as follows.
![2241f1](https://github.com/user-attachments/assets/41eb5223-42db-49a8-a6c0-f44ee47369d7)

## Steps to run the simulation models

### Step 1 - Code download
Download the ./DES_Screen_Mammo folder to your local machine.

### Step 2 - Requirements
Install all required packages listed in ./code/requirements.txt file

### Step 3 - Command Line Commands for baseline workflow
Locate the ./DES_Screen_Mammo folder and run the following command.

`python run_simulation.py`

By default, the simulation runs the baseline workflow (no_1ss=True) with num_interation=10, num_scanner=3, num_us_machine=2, and stoptime=10.

### Step 4 - Command Line Commands for AI-aided same-day diagnostic workflow

An example of the same-day diagnostic workflow with 3 mammography machines, 3 ulstrasound machines, 8.5 hours of imaging center operating time, and 100 iterations. 

`python run_simulation.py --no_1ss False --num_scanncer 3 --num_us_machine 3 --stoptime 8.5 --num_iteration 100`

The following is a list of parameters to explore.

> no_1ss: Specify 'True' to use baseline simulation or 'False' to enable same-day diagnostic simulation, default is 'True'
> 
> num_scanner: Number of mammography scanners in the imaging center, defalut is 3
> 
> num_us_machine: Number of ultarsound scanners in the imaging center, defualt is 2
> 
> stoptime: Time to stop the simulation in hours (i.e., the imaging center operating hours), default is 8.5
>
> num_iteration: Number of clinic days of the simulation

### Step 4 - Output and post-simulation analysis
The output of the simulation will be saved in the ./DES_Screen_Mammo/Output_1ss/ or ./DES_Screen_Mammo/Output_no_1ss/ folder. Each patient and the timestamp of each step are logged for post-simuluation analysis. The two workflows are logged separately. An example of the output file is as follows. The columns in the output file logs the timestamp for each step and waiting times inbetween steps. The lengty of stay in the clinic can be calculdated using (exit_system_ts-arrival_ts). Each output file stores inforamation of one simulated clinic day. 

<img width="863" alt="Screenshot 2024-11-03 at 10 19 48 AM" src="https://github.com/user-attachments/assets/d41f987e-8dcb-4097-ba76-c79513a2847a">




