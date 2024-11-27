# offline-emotion-analyzer.py
'''
@author:Simon
'''
#%%
import cv2
from deepface import DeepFace
import pandas as pd
import argparse
import os

#%%
def analyze_video(video_path, output_csv, frame_skip=10):
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

    results = []

    try:
        while cap.isOpened():
            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Ensure the current frame is within bounds and skip frames accordingly
            if current_frame >= total_frames:
                break

            if (current_frame % frame_skip != 0) and (current_frame + frame_skip < total_frames):
                cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame + frame_skip - 1)
                continue

            ret, frame = cap.read()
            if not ret:
                break

            print(f"Analyzing frame {current_frame} of {total_frames}", end='\r')

            try:
                # Use RetinaFace for analysis
                analysis = DeepFace.analyze(frame, actions=['emotion'], detector_backend='retinaface', enforce_detection=False)
                for face in analysis:
                    results.append({
                        "frame": current_frame,
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
    print(f"Analysis complete. Results saved to {output_csv}")

#%%
# Run the analysis
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze emotions in video frames.")
    parser.add_argument("--video", type=str, help="Path to the video file.")
    parser.add_argument("--frame_skip", type=int, default=6, help="Number of frames to skip between analyses.")
    args = parser.parse_args()

    # If arguments are not provided, prompt the user for inputs
    if args.video:
        video_path = args.video
        frame_skip = args.frame_skip
    else:
        video_path = input("Enter the path to the video file: ")
        frame_skip = int(input("Enter the number of frames to skip: "))

    output_csv = f"{video_path[:-4]}.csv"
    analyze_video(video_path, output_csv, frame_skip=frame_skip)
