# EpiVision

## How to install
1. If you don't already have python installed, install python.
2. Copy the repository.
3. in the folder which you copied the repo to, do 'pip install deepface'.
4. Try python app.py in your terminal, if it works great (it probably doesn't). The terminal should now prompt you to download tf-keras. do that. write 'pip install tf-keras' in the terminal.
5. Try python app.py again. Now it should hopefully work.
6. If it doesnt work try 'pip install -r requirements.txt'.

EpiVision is a project aimed at enhancing [Epi](https://github.com/birgerjohansson/Epi), the educational robot, by equipping it with facial recognition capabilities. Our goal is to enable Epi to recognize individuals as they enter a room and greet them personally by name, thereby creating a more engaging and interactive educational experience.

## Project Overview

EpiVision focuses on developing a real-time face recognition system that processes video feeds from Epi’s dual cameras by leveraging machine learning and computer vision techniques. She system aims to detects and identifiy familiar faces, and directs Epi to greet recognized individuals verbally.

## Objectives

- Real-Time Face Detection and Recognition: Implement a robust system capable of detecting multiple faces in various lighting conditions and recognizing known individuals with high accuracy.
- Natural Interaction: Enable Epi to turn its gaze toward recognized persons and greet them by name using speech synthesis, enhancing the human-robot interaction experience.
- Integration with Main System: Output recognition results in a predefined HTTP request schema compatible with Epi’s main control system [Ikaros](https://github.com/birgerjohansson/ikaros) for seamless integration.
- Scalability and Performance: Optimize the system for real-time performance on available hardware resources, ensuring minimal latency and high reliability.

## Key Features

- Stereo Vision Processing: Utilizes Epi’s dual cameras to enhance face detection accuracy and estimate the position of individuals for gaze direction.
- Customizable Recognition Database: Supports adding new individuals to the recognition database with proper consent and data handling practices.
- Adaptive to Environmental Conditions: Implements algorithms to handle varying lighting conditions and dynamic backgrounds.
   Ethical Data Handling: Adheres to privacy regulations and ethical guidelines for biometric data collection and usage.

## Technologies Used

***Preliminary information***

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

## mov-to-db.py

Either run the mov-to-db.py file from the terminal and use <path to video> <Name> as args (`python mov-to-db.py /Users/epi/Downloads/movie.mov John`), or run the program without args and add video path and name as inputs when prompted.

## offline-emotion-analyzer.py
Program to analyze video frames for emotions using DeepFace.

Usage:
    python offline-emotion-analyzer.py --video <video_path> --frame_skip <number> --detector_backend <backend>

Arguments:
    --video: Path to the video file to be analyzed.
    --frame_skip: Number of frames to skip between analyses (default is 10). To analyze every frame, frame_skip = 1.
    --detector_backend: Face detection model to use ('opencv', 'retinaface', 'mtcnn', etc.).
                       Default is 'retinaface'.

If no arguments are provided, the program will prompt the user for video path and frame skip values.
