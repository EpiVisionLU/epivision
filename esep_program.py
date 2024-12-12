import csv
import random
import requests
import time
import curses
from urllib.parse import quote
#%%
CSV_FILE = "esep.csv"
LOG_FILE = "experiment_log.csv"
EPI_BASE_URL = "http://localhost:8000/command/EpiSpeech.say/0/0/"
#%%
def load_script(filename):
    """
    Load the script from CSV.
    Expected columns: Phase;Phase description;Line;Script
    """
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        required_cols = {"Phase", "Phase description", "Line", "Script"}
        if not required_cols.issubset(reader.fieldnames):
            raise ValueError(f"CSV file must contain the columns: {required_cols}")
        
        script_data = []
        for row in reader:
            # Convert Phase and Line to int for easier sorting
            row['Phase'] = int(row['Phase'])
            row['Line'] = int(row['Line'])
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
        phases[p]['lines'].append((row['Line'], row['Script']))
    
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

def send_to_epi(text):
    """
    Send the given text to Epi via a GET request, properly URL encoded.
    """
    safe_text = quote(text)
    url = EPI_BASE_URL + safe_text
    try:
        requests.get(url)
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to Epi: {e}")

def log_event(logfile, start_time, phase, line, text):
    """
    Log the event (timestamp, phase, line, text) to a CSV file.
    Timestamp is time since start_time in seconds.
    """
    elapsed = time.time() - start_time
    with open(logfile, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([elapsed, phase, line, text])

def main(stdscr):
    # Setup curses
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()
    
    # Load and organize script
    script_data = load_script(CSV_FILE)
    phases = organize_phases(script_data)
    
    # Randomize phases except first and last
    phases = randomize_phases(phases)
    
    # Initialize logging
    # Write header
    with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Time_since_start(s)", "Phase", "Line", "Script"])
    
    start_time = time.time()

    # Navigation state
    current_phase_index = 0
    current_line_index = 0

    def display_current_line():
        stdscr.clear()
        current_phase = phases[current_phase_index]
        line_num, line_text = current_phase['lines'][current_line_index]
        # Display the current line
        stdscr.addstr(0, 0, "Controls: SPACE/f=Forward, b=Backward, Y=Yes, N=No, Q=Quit")
        stdscr.addstr(1, 0, f"Line {line_num}: {line_text}")
        stdscr.addstr(2, 0, f"Phase {current_phase['Phase']}: {current_phase['Phase description']}")
        stdscr.refresh()
        return (current_phase['Phase'], line_num, line_text)

    # Show the first line
    phase_num, line_num, line_text = display_current_line()
    send_to_epi(line_text)
    log_event(LOG_FILE, start_time, phase_num, line_num, line_text)

    # Key loop
    while True:
        key = stdscr.getch()

        current_phase = phases[current_phase_index]
        line_count = len(current_phase['lines'])

        # Convert key to char if possible
        if key == curses.KEY_RESIZE:
            # Just redraw on resize
            phase_num, line_num, line_text = display_current_line()
            continue

        ch = chr(key) if key != -1 else ''

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

            phase_num, line_num, line_text = display_current_line()
            send_to_epi(line_text)
            log_event(LOG_FILE, start_time, phase_num, line_num, line_text)

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

            phase_num, line_num, line_text = display_current_line()
            send_to_epi(line_text)
            log_event(LOG_FILE, start_time, phase_num, line_num, line_text)

        elif ch in ['Y', 'y']:
            # Send "yes"
            send_to_epi("yes")
            log_event(LOG_FILE, start_time, phase_num, line_num, "[Shortcut] yes")

        elif ch in ['N', 'n']:
            # Send "no"
            send_to_epi("no")
            log_event(LOG_FILE, start_time, phase_num, line_num, "[Shortcut] no")

        elif ch in ['T', 't']:
            # Send free text
            freetext_input = input("What should Epi say?")
            send_to_epi(freetext_input)
            log_event(LOG_FILE, start_time, phase_num, line_num, f"[Custom text] {freetext_input}")

        elif ch in ['Q', 'q']:
            # Quit
            break

    # End of experiment
    stdscr.addstr(5, 0, "Experiment finished. Press any key to exit.")
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)