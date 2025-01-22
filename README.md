# EpiVision

EpiVision is a student project from Lund University and LTH. 

## How to install
1. If you don't already have python installed, install python.
2. Copy the repository.
3. in the folder which you copied the repo to, do 'pip install deepface'.
4. Try python app.py in your terminal, if it works great (it probably doesn't). The terminal should now prompt you to download tf-keras. do that. write 'pip install tf-keras' in the terminal.
5. Try python app.py again. Now it should hopefully work.
6. If it doesnt work try 'pip install -r requirements.txt'.

EpiVision is a project aimed at enhancing [Epi](https://github.com/birgerjohansson/Epi), the educational robot, by equipping it with facial recognition capabilities. 

## Project Overview

EpiVision focuses on developing a real-time face recognition system that processes video feeds from Epi’s cameras by leveraging machine learning and computer vision techniques. She system aims to detects and identifiy familiar faces and facial expressions.

## Technologies Used

- Programming Language: Python
- Face Recognition Framework: [DeepFace](https://github.com/serengil/deepface)
- Face Recognition Models:
  - Detection: [RetinaFace](https://github.com/serengil/retinaface) or [mtcnn](https://github.com/ipazc/mtcnn)
  - Identification: [facenet](https://github.com/davidsandberg/facenet)

- Text-to-Speech:[ Ikaros EpiSpeech](https://github.com/ikaros-project/ikaros)

## Team

- Ruben Täpptorp (Information & Communications Engineering)
- Alexander Vatamidis Norrstam (Cognitive Science)
- Marcus Lindelöf (Cognitive Science)
-  Simon Högborg Rosengren (Cognitive Science)

# How-to

### app.py

Change `main()` based on what you want to do.

`analyze_emotion_live(source='webcam')` Facial attribute analysis. Change `source` to `source='stream'` to use Epi's camera.

`demo_mode()` For live demo

### mov-to-db.py

Either run the mov-to-db.py file from the terminal and use <path to video> <Name> as args (`python mov-to-db.py /Users/epi/Downloads/movie.mov John`), or run the program without args and add video path and name as inputs when prompted.

## /Offline analysis

### offline-emotion-analyzer.py

Program to analyze video frames for emotions using DeepFace.

Usage:
    `python offline-emotion-analyzer.py --video <video_path> --frame_skip <number> --detector_backend <backend>`

Arguments:
   `--video`: Path to the video file to be analyzed.
    `--frame_skip`: Number of frames to skip between analyses (default is 10). To analyze every frame, `frame_skip = 1`.
    `--detector_backend`: Face detection model to use ('opencv', 'retinaface', 'mtcnn', etc.).
                       Default is 'retinaface'.

If no arguments are provided, the program will prompt the user for video path and frame skip values.

### convert_csv_to_elan.py

This program exports the `dominant_emotion` from a `offline-emotion-analyzer.py` csv to a `.txt` which can be imported into [ELAN](https://archive.mpi.nl/tla/elan). Import as tab separated values.

### video-overlay.py

Overlay face and emotion data on video. Useful for creating video content and trouble shooting.

Usage: python video-overlay.py --video /path/to/video.mp4 --csv /path/to/video.csv`

- `--video` Path to video. **Required**.
- `--csv` Path to csv from `offline-emotion-analyzer.py`. **Required**.
- `--name` Hardcoded name placed on top of found faces.
- `--output` Name the output file. Default: "video_overlay.mp4"

## /ESEP program

### esep.json

The `esep.json` file contains the associated animations to the script in `esep.csv`. You need to put `esep.json in `/users/epi/Ikaros-2/Robots/code/` (or something like that). Or you can create your own animations.  `4` in the script refers to the fifth animation in Ikaros, etc.

### esep_program.py

Program to run the *Emotion and Stress Evoking Protocol* (ESEP) paradigm for exploring human-robot-interaction. Ikaros must be running when running the program. It loads the script from `esep.csv`. 

A log with timestamps (experiment_log.csv) will be created each time you run the experiment. 

