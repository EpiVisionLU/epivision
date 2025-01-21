'''
Emotion and Stress Evoking Protocoll
Group 4b, KOGP10/MAMN15
LU
Created 2024-12-10
@author: SRO
'''
import csv
import random
import requests
import time
import curses
from urllib.parse import quote
import datetime
import subprocess

CSV_FILE = "esep.csv"
EPI_BASE_URL_SPEECH = "http://localhost:8000/command/EpiSpeech.say/0/0/"
EPI_BASE_URL_MOTION = "http://localhost:8000/command/SR.trig/"
VIDEO_STREAM_URL = "http://righteye.local:8080/stream/video.mjpeg"

def record_video(video_file):
    """
    Start recording the MJPEG stream at a reduced frame rate.
    Returns the subprocess.Popen object so we can stop it later.
    """
    process = subprocess.Popen([
        "ffmpeg",
        "-loglevel", "quiet",
        "-i", VIDEO_STREAM_URL,
        "-r", "12",
        "-c:v", "mjpeg",
        "-q:v", "5",
        video_file
    ])
    return process

def load_script(filename):
    """
    Load the script from CSV.
    Expected columns: Phase;Phase description;Line;Script;Motion
    Motion may be empty.
    """
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        required_cols = {"Phase", "Phase description", "Line", "Script", "Motion"}
        if not required_cols.issubset(reader.fieldnames):
            raise ValueError(f"CSV file must contain the columns: {required_cols}")
        
        script_data = []
        for row in reader:
            # Convert Phase and Line to int for easier sorting
            row['Phase'] = int(row['Phase'])
            row['Line'] = int(row['Line'])
            
            # Handle motion column
            motion_str = row.get('Motion', '').strip()
            if motion_str.isdigit():
                row['Motion'] = int(motion_str)
            else:
                # If empty or non-digit, set None
                row['Motion'] = None
            
            script_data.append(row)
    return script_data

def organize_phases(script_data):
    """
    Organize the script by phase.
    Returns a list of dicts, each representing a phase.
    """
    phases = {}
    for row in script_data:
        p = row['Phase']
        if p not in phases:
            phases[p] = {
                'Phase': p,
                'Phase description': row['Phase description'],
                'lines': []
            }
        # We'll store tuples with (line_num, script_text, motion)
        phases[p]['lines'].append((row['Line'], row['Script'], row['Motion']))
    
    # Sort lines within each phase
    for p in phases:
        phases[p]['lines'].sort(key=lambda x: x[0])
    
    # Sort phases by their phase number
    ordered_phases = [phases[i] for i in sorted(phases.keys())]
    return ordered_phases

def randomize_phases(phases):
    """
    Randomize all but the first and last phases.
    """
    if len(phases) <= 2:
        # Nothing to randomize if we have less or equal to 2 phases
        return phases
    middle = phases[1:-1]
    random.shuffle(middle)
    return [phases[0]] + middle + [phases[-1]]

def send_speech_to_epi(text):
    """
    Send the given speech text to Epi via a GET request, properly URL encoded.
    """
    safe_text = quote(text)
    url = EPI_BASE_URL_SPEECH + safe_text
    try:
        requests.get(url)
    except requests.exceptions.RequestException as e:
        print(f"Error sending speech request to Epi: {e}")

def send_motion_to_epi(motion_cmd):
    """
    Send the given motion command (int) to Epi.
    Example: motion_cmd = 0 -> http://localhost:8000/command/SR.trig/0/0/0
    """
    url = f"{EPI_BASE_URL_MOTION}{motion_cmd}/0/0"
    try:
        requests.get(url)
    except requests.exceptions.RequestException as e:
        print(f"Error sending motion request to Epi: {e}")

def create_log_file_name():
    """
    Generates a timestamped log file name.
    """
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d_%H%M")
    return f"experiment_log_{timestamp}.csv"

def create_video_file_name():
    """
    Generates a timestamped video file name.
    """
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d_%H%M")
    return f"experiment_log_{timestamp}.mkv"

def log_event(logfile, start_time, phase, line, text):
    """
    Log the event (timestamp, phase, line, text) to a CSV file.
    Timestamp is time since start_time in seconds.
    """
    elapsed = time.time() - start_time
    elapsed = round(elapsed, 2)
    with open(logfile, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([elapsed, phase, line, text])

def main(stdscr, log_file):
    # Setup curses
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()
    
    # Load and organize script
    script_data = load_script(CSV_FILE)
    phases = organize_phases(script_data)
    
    # Randomize phases except first and last
    # phases = randomize_phases(phases) # Comment out if script should be read in order
    
    # Initialize logging
    with open(log_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Time_since_start(s)", "Phase", "Line", "Script"])
    
    start_time = time.time()

    # Navigation state
    current_phase_index = 0
    current_line_index = 0

    def display_current_line():
        stdscr.clear()
        current_phase = phases[current_phase_index]
        line_num, line_text, motion_cmd = current_phase['lines'][current_line_index]
        # Display the current line
        stdscr.addstr(0, 0, f"Phase {current_phase['Phase']}: {current_phase['Phase description']}")
        stdscr.addstr(1, 0, f"Line {line_num}: {line_text}")
        stdscr.addstr(5, 0, "Controls: SPACE/f=Forward, b=Backward, Y=Yes, N=No, P=Please try again, R=Re-read instructions, t=Custom message, Q=Quit")
        stdscr.refresh()
        return (current_phase['Phase'], line_num, line_text, motion_cmd)

    def send_line_actions(phase_num, line_num, line_text, motion_cmd):
        # If there's a motion command, send it after speech
        if motion_cmd is not None:
            send_motion_to_epi(motion_cmd)
            # Log the motion command
            log_event(log_file, start_time, phase_num, line_num, f"[Motion] {motion_cmd}")

        # If there's a script line, send it
        if line_text.strip():
            send_speech_to_epi(line_text)
            log_event(log_file, start_time, phase_num, line_num, line_text)

    phase_num, line_num, line_text, motion_cmd = display_current_line()
    send_line_actions(phase_num, line_num, line_text, motion_cmd)

    # Key loop
    while True:
        key = stdscr.getch()
        ch = chr(key) if key != -1 else ''

        current_phase = phases[current_phase_index]
        line_count = len(current_phase['lines'])

        if ch in [' ', 'f']:
            # Move to next line
            current_line_index += 1
            if current_line_index >= line_count:
                # Move to next phase
                current_phase_index += 1
                current_line_index = 0
                if current_phase_index >= len(phases):
                    # No more phases, end the experiment
                    break

            phase_num, line_num, line_text, motion_cmd = display_current_line()
            send_line_actions(phase_num, line_num, line_text, motion_cmd)

        elif ch == 'b':
            # Move to previous line
            current_line_index -= 1
            if current_line_index < 0:
                # Go to previous phase if possible
                current_phase_index -= 1
                if current_phase_index < 0:
                    # Can't go back, stay at start
                    current_phase_index = 0
                    current_line_index = 0
                else:
                    current_line_index = len(phases[current_phase_index]['lines']) - 1

            phase_num, line_num, line_text, motion_cmd = display_current_line()
            send_line_actions(phase_num, line_num, line_text, motion_cmd)

        elif ch in ['Y', 'y']:
            # Send "yes"
            send_motion_to_epi(0)
            send_speech_to_epi("yes")
            log_event(log_file, start_time, phase_num, line_num, "[Shortcut] yes")
            phase_num, line_num, line_text, motion_cmd = display_current_line()

        elif ch in ['N', 'n']:
            # Send "no"
            send_motion_to_epi(1)
            send_speech_to_epi("no")
            log_event(log_file, start_time, phase_num, line_num, "[Shortcut] no")
            phase_num, line_num, line_text, motion_cmd = display_current_line()

        elif ch in ['P', 'p']:
            # "Please try again"
            send_speech_to_epi("please_try_again")
            log_event(log_file, start_time, phase_num, line_num, "[Shortcut] please_try_again")
            phase_num, line_num, line_text, motion_cmd = display_current_line()

        elif ch in ['R', 'r']:
            # "I repeat: {line}"
            repeat_text = f"I repeat: {line_text}"
            send_speech_to_epi(repeat_text)
            log_event(log_file, start_time, phase_num, line_num, f"[Shortcut] {repeat_text}")
            phase_num, line_num, line_text, motion_cmd = display_current_line()

        elif ch in ['T', 't']:
            # Custom message
            curses.echo()
            stdscr.addstr(5, 0, "Enter custom message: ")
            stdscr.clrtoeol()
            stdscr.refresh()
            custom_bytes = stdscr.getstr(5, 19)  # read input starting at column 19
            curses.noecho()
            custom_msg = custom_bytes.decode('utf-8')
            # Send custom message
            send_speech_to_epi(custom_msg)
            log_event(log_file, start_time, phase_num, line_num, f"[Custom] {custom_msg}")
            phase_num, line_num, line_text, motion_cmd = display_current_line()

        elif ch in ['Q', 'q']:
            # Quit
            break

    # End of experiment
    stdscr.addstr(7, 0, "Experiment finished. Press any key to exit.")
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    log_file = create_log_file_name()
    video_file = create_video_file_name()

    # Start the recording process before running your main logic
    #recording_process = record_video(video_file) #comment out to not record

    curses.wrapper(main, log_file)

    # After main() completes, stop the recording
    recording_process.terminate()
    recording_process.wait()
