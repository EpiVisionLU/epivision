import argparse
import csv
import cv2
import os

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Overlay face and emotion data on video.")
    parser.add_argument("--video", required=True, help="Path to the input video file.")
    parser.add_argument("--csv", required=True, help="Path to the CSV file with face and emotion data.")
    parser.add_argument("--name", default=None, help="Name to overlay above the face. If not provided, the ID from the CSV will be used.")
    parser.add_argument("--output", default="video_overlay.mp4", help="Name of the output video file.")
    return parser.parse_args()

# Function to parse the CSV data with metadata
def parse_csv(csv_path):
    video_data = []
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        # Read metadata line
        first_line = f.readline().rstrip('\n')
        # Skipping parsing metadata for now but could add a function like parse_metadata_line(first_line)

        # Read the header line
        header_line = f.readline().rstrip('\n')
        header = header_line.split(',')  # Split on commas manually

        # Prepare indices for relevant columns
        frame_idx = header.index('frame')
        time_code_idx = header.index('time_code')
        id_idx = header.index('id')
        dominant_emotion_idx = header.index('dominant_emotion')
        angry_idx = header.index('angry')
        disgust_idx = header.index('disgust')
        fear_idx = header.index('fear')
        happy_idx = header.index('happy')
        sad_idx = header.index('sad')
        surprise_idx = header.index('surprise')
        neutral_idx = header.index('neutral')
        face_y_idx = header.index('face_y')
        face_x_idx = header.index('face_x')
        face_height_idx = header.index('face_height')
        face_width_idx = header.index('face_width')

        # Read remaining rows
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue

            try:
                video_data.append({
                    "frame_idx": int(row[frame_idx]),
                    "time_code": float(row[time_code_idx]),
                    "id": row[id_idx],
                    "dominant_emotion": row[dominant_emotion_idx],
                    "angry": float(row[angry_idx]),
                    "disgust": float(row[disgust_idx]),
                    "fear": float(row[fear_idx]),
                    "happy": float(row[happy_idx]),
                    "sad": float(row[sad_idx]),
                    "surprise": float(row[surprise_idx]),
                    "neutral": float(row[neutral_idx]),
                    "face_y": int(row[face_y_idx]),
                    "face_x": int(row[face_x_idx]),
                    "face_height": int(row[face_height_idx]),
                    "face_width": int(row[face_width_idx]),
                })
            except (ValueError, IndexError):
                # Skip malformed rows
                continue

    return video_data

# Function to process the video and overlay data
def process_video(video_path, video_data, name, output_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file:", video_path)
        exit()

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    data_by_frame = {}
    for row in video_data:
        fidx = row["frame_idx"]
        data_by_frame.setdefault(fidx, []).append(row)

    frame_index = 0
    last_overlay = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index in data_by_frame:
            last_overlay = data_by_frame[frame_index]

        if last_overlay:
            for person_data in last_overlay:
                y = person_data["face_y"]
                x = person_data["face_x"]
                h = person_data["face_height"]
                w = person_data["face_width"]

                display_name = name if name else person_data["id"]  # Use the provided name or fallback to ID

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, display_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                dom_emotion = person_data["dominant_emotion"]
                emotions = {
                    "angry": person_data["angry"],
                    "disgust": person_data["disgust"],
                    "fear": person_data["fear"],
                    "happy": person_data["happy"],
                    "sad": person_data["sad"],
                    "surprise": person_data["surprise"],
                    "neutral": person_data["neutral"],
                }

                overlay_x1 = x + w + 10
                overlay_y1 = y
                overlay_width = 210  # Increased width
                overlay_height = 240  # Increased height
                overlay_x2 = overlay_x1 + overlay_width
                overlay_y2 = overlay_y1 + overlay_height

                overlay = frame.copy()
                cv2.rectangle(overlay, (overlay_x1, overlay_y1), (overlay_x2, overlay_y2), (0, 0, 0), -1)
                frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

                cv2.putText(frame, f"Dominant: {dom_emotion}", (overlay_x1 + 5, overlay_y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                bar_left = overlay_x1 + 80  # Adjusted position for bars
                bar_top_start = overlay_y1 + 40
                bar_height = 12
                gap = 15

                for i, (emo_name, emo_val) in enumerate(emotions.items()):
                    bar_length = int(min(emo_val, 100) / 100 * 100)
                    top_y = bar_top_start + i * (bar_height + gap)
                    bar_color = (255, 255, 255) if emo_name != dom_emotion.lower() else (0, 255, 255)

                    cv2.putText(frame, f"{emo_name}", (overlay_x1 + 5, top_y + bar_height - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                    cv2.rectangle(frame, (bar_left, top_y), (bar_left + bar_length, top_y + bar_height), bar_color, -1)

        out.write(frame)
        frame_index += 1

    cap.release()
    out.release()
    print(f"Done! Output saved to {output_path}")

# Main entry point
if __name__ == "__main__":
    args = parse_arguments()
    video_data = parse_csv(args.csv)
    process_video(args.video, video_data, args.name, args.output)
