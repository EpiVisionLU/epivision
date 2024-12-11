# experiment-program.py

#%% imports
import requests # För http-requests
import csv # skriv csv
import time 


#%% 
timestamps = [] # Lista med timestamps

#%% 
starttime = time.perf_counter()
r = requests.get('http://localhost:8000/command/EpiSpeech.say/0/0/hello_there._what_time_is_it_today')
time.sleep(2)
r = requests.get('http://127.0.0.1:8000/command/SR.trig/1/0/0')
y = requests.get('http://localhost:8000/command/EpiSpeech.say/0/0/hello_there_again')
time.sleep(1)
y = requests.get('http://localhost:8000/command/EpiSpeech.say/0/0/more_seconds_have_passed')
endtime = time.perf_counter()
print(starttime, endtime)
print(f"runtime: {endtime-starttime}")
y = requests.get(f'http://localhost:8000/command/EpiSpeech.say/0/0/runtime_{round(endtime-starttime)}')
# %%
