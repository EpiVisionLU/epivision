# EpiVision

#How to install
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

- Programming Language: Python
- Computer Vision Libraries: TBD
- Deep Learning Frameworks: TBD
- Face Recognition Models: TBD
- Text-to-Speech: TBD

## Team

- Ruben Täpptorp (Information & Communications Engineering)
- Alexander Vatamidis Norrstam (Cognitive Science)
- Marcus Lindelöf (Cognitive Science)
-  Simon Högborg Rosengren (Cognitive Science)
