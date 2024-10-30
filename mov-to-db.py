"""
Created on Tue Oct 29 23:53:38 2024

@author: simon
"""

import os
import cv2
import csv
import uuid
from datetime import datetime
import sys

#%%

# Path to save the database
DB_PATH = "./db"
CSV_FILE = "./contacts.csv"

#%%

# Create database directory if it doesn't exist
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

# Create CSV file if it doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row to the CSV file
        writer.writerow(["id", "name", "creation_time"])
        
#%% 

def generate_unique_id():
    """
    Generate a unique 4-character ID.
    The function will keep generating until it finds an ID that is not already in use.
    """
    while True:
        new_id = str(uuid.uuid4().hex[:4])  # Generate a 4-character unique ID
        if not is_id_in_csv(new_id):  # Ensure the ID is unique
            return new_id

def is_id_in_csv(contact_id):
    """
    Check if a given contact ID already exists in the CSV file.
    :param contact_id: The ID to check for existence.
    :return: True if the ID exists, False otherwise.
    """
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            if row[0] == contact_id:  # Check if the ID matches
                return True
    return False

def add_contact_to_csv(contact_id, name):
    """
    Add a new contact to the CSV file with the current timestamp.
    :param contact_id: The unique ID of the contact.
    :param name: The name of the contact.
    """
    creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current date and time
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([contact_id, name, creation_time])  # Write the contact information to the CSV file

def extract_frames_from_video(video_path, output_folder, num_frames=10):
    """
    Extract a specified number of frames from a video file.
    :param video_path: Path to the video file.
    :param output_folder: Folder where the frames will be saved.
    :param num_frames: Number of frames to extract from the video.
    """
    cap = cv2.VideoCapture(video_path)  # Open the video file
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Get the total number of frames in the video
    frame_interval = max(1, total_frames // num_frames)  # Calculate the interval between frames to extract

    frame_count = 0
    extracted_count = 0

    while cap.isOpened() and extracted_count < num_frames:
        ret, frame = cap.read()  # Read the next frame from the video
        if not ret:  # If no frame is returned, end of video is reached
            break

        # Save the frame if it matches the extraction interval
        if frame_count % frame_interval == 0:
            frame_filename = f"{output_folder}_{extracted_count+1:02d}.jpg"  # Generate filename for the frame
            cv2.imwrite(frame_filename, frame)  # Save the frame as a JPEG image
            extracted_count += 1  # Increment the count of extracted frames

        frame_count += 1  # Increment the total frame count

    cap.release()  # Release the video capture object

def process_video(video_path, name):
    """
    Process a video by extracting frames and updating the database with contact information.
    :param video_path: Path to the video file.
    :param name: Name of the person in the video.
    """
    # Generate a unique ID for the new contact
    contact_id = generate_unique_id()

    # Create a directory for the contact
    contact_dir = os.path.join(DB_PATH, contact_id)
    if not os.path.exists(contact_dir):
        os.makedirs(contact_dir)

    # Extract frames from the video and save them to the contact's folder
    extract_frames_from_video(video_path, os.path.join(contact_dir, contact_id))

    # Add contact details to the CSV file
    add_contact_to_csv(contact_id, name)
  
def main():
    # Check if command-line arguments are provided
    if len(sys.argv) > 2:
        # Get arguments from the command line
        video_path = sys.argv[1]
        name = sys.argv[2]
    else:
        # Prompt user for inputs if no command-line arguments
        video_path = input("Enter the video path: ")  # Prompt for video path
        name = input("Enter the name: ")  # Prompt for contact name

    # Process the video with the given inputs
    process_video(video_path, name)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
