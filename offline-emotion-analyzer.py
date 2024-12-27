# facial_feature_analyzer.py
# @author: SRO
# Created on: 2024-11-27

"""
Program to analyze video frames for emotions using DeepFace.

Usage:
    python facial_feature_analyzer.py --video <video_path> --frame_skip <number> --detector_backend <backend>

Arguments:
    --video: Path to the video file to be analyzed.
    --frame_skip: Number of frames to skip between analyses (default is 10).
    --detector_backend: Face detection model to use ('opencv', 'retinaface', 'mtcnn', etc.).
                       Default is 'retinaface'.

If no arguments are provided, the program will prompt the user for video path and frame skip values.

"""
#%%

import cv2
from deepface import DeepFace
import pandas as pd
import argparse
import os

#%%
def analyze_video(video_path, output_csv, frame_skip=10, detector_backend='retinaface'):
    """
    Analyze video frames to detect emotions.
    - video_path: Path to the video file.
    - output_csv: Output CSV file path.
    - frame_skip: Number of frames to skip between analyses.
    """
    if not os.path.exists(video_path):
        print(f"Error: The video file '{video_path}' does not exist.")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file '{video_path}'.")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = float(cap.get(cv2.CAP_PROP_FPS))
    print(f"Video selected: {video_path}. FPS: {video_fps}. Total frames: {total_frames}. Frames to be analyzed: ~ {round(total_frames / frame_skip)}")

    results = []

    try:
        while cap.isOpened():
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

            # Ensure the current frame is within bounds and skip frames accordingly
            if current_frame >= total_frames:
                break
              
            if (current_frame > total_frames - (total_frames % frame_skip)):
                print(f"Analysis complete. Last frame analyzed: {current_frame - 1}")
                break

            # Skip frames logic using cap.grab() for better efficiency
            for _ in range(frame_skip - 1):
                cap.grab()

            ret, frame = cap.read()
            if not ret:
                break

            print(f"Analyzing frame {current_frame} of {total_frames}", end='\r')

            try:
                # Use RetinaFace for analysis
                analysis = DeepFace.analyze(frame, actions=['emotion'], detector_backend=detector_backend, enforce_detection=False)
                for person_idx, face in enumerate(analysis, start=1):
                    results.append({
                        "frame": current_frame,
                        "time_code": round(current_frame / video_fps, 4),
                        "id": int(person_idx),
                        "dominant_emotion": face["dominant_emotion"],
                        "angry": face["emotion"].get("angry", 0),
                        "disgust": face["emotion"].get("disgust", 0),
                        "fear": face["emotion"].get("fear", 0),
                        "happy": face["emotion"].get("happy", 0),
                        "sad": face["emotion"].get("sad", 0),
                        "surprise": face["emotion"].get("surprise", 0),
                        "neutral": face["emotion"].get("neutral", 0),
                        "face_y": face["region"].get("y", 0),
                        "face_x": face["region"].get("x", 0),
                        "face_height": face["region"].get("h", 0),
                        "face_width": face["region"].get("w", 0),
                        "face_confidence": face.get("face_confidence")
                    })
            except Exception as e:
                print(f"Error analyzing frame {current_frame}: {e}")
    finally:
        cap.release()

    # Write results to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)

    # Add meta data to csv 
    # Reopen the file to prepend the metadata
    file_meta = f'# {{"video_path": "{video_path}", "frame_skip": {frame_skip}, "video_fps": {video_fps}}}'

    # Read the CSV content
    with open(output_csv, 'r') as file:
        csv_content = file.read()

    # Write the metadata followed by the original CSV content
    with open(output_csv, 'w') as file:
        file.write(file_meta + '\n' + csv_content)

    print(f"Results saved to {output_csv}")

#%%
# Run the analysis
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze emotions in video frames.")
    parser.add_argument("--detector_backend", type=str, default='retinaface', help="Face detection model to use (e.g., 'opencv', 'retinaface', 'mtcnn', etc.)")
    parser.add_argument("--video", type=str, help="Path to the video file.")
    parser.add_argument("--frame_skip", type=int, default=5, help="Number of frames to skip between analyses.")
    args, unknown = parser.parse_known_args()

    # If arguments are not provided, prompt the user for inputs
    if args.video:
        video_path = args.video
        frame_skip = args.frame_skip
    else:
        video_path = input("Enter the path to the video file: ")
        frame_skip = int(input("Enter the number of frames to skip: "))

    output_csv = f"{video_path[:-4]}.csv"
    analyze_video(video_path, output_csv, frame_skip=frame_skip, detector_backend=args.detector_backend)