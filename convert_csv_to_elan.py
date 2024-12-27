import csv
import re
import math
import os
import json

def hhmmss_milli(total_seconds):
    """
    Convert float seconds to a string HH:MM:SS.mmm (3 decimals).
    E.g. 9.211 -> "00:00:09.211"
    """
    hours = int(total_seconds // 3600)
    remainder = total_seconds % 3600
    minutes = int(remainder // 60)
    seconds = remainder % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

def parse_metadata_line(line):
    line = line.strip()
    if line.startswith('#'):
        # remove the leading '#'
        line = line[1:].strip()
    # now it's valid JSON, so parse directly
    metadata_dict = json.loads(line)
    
    video_path = metadata_dict.get('video_path', '')
    frame_skip = metadata_dict.get('frame_skip', 1)
    video_fps  = metadata_dict.get('video_fps', 25)
    return video_path, frame_skip, video_fps

def read_csv_and_group_by_id(csv_path):
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        # 1) Read metadata line RAW (not via csv.reader)
        first_line = f.readline().rstrip('\n')
        video_path, frame_skip, video_fps = parse_metadata_line(first_line)
        
        # 2) Read the next line as header
        header_line = f.readline().rstrip('\n')
        header = header_line.split(',')  # now we split on commas ourselves
        time_idx = header.index('time_code')
        id_idx   = header.index('id')
        emotion_idx = header.index('dominant_emotion')
        
        # 3) Now create a CSV reader for the *remaining* lines only
        reader = csv.reader(f)
        
        rows_by_id = {}
        for row in reader:
            if not row:
                continue
            # parse time, id, emotion
            try:
                t        = float(row[time_idx])
                face_id  = int(row[id_idx])
                emotion  = row[emotion_idx]
            except ValueError:
                # skip any malformed rows
                continue
            
            rows_by_id.setdefault(face_id, []).append({
                'time_code': t,
                'emotion': emotion
            })
        
        # Sort each ID's rows by time_code
        for face_id in rows_by_id:
            rows_by_id[face_id].sort(key=lambda r: r['time_code'])
        
        metadata = {
            'video_path': video_path,
            'frame_skip': frame_skip,
            'video_fps': video_fps
        }
        
        return metadata, rows_by_id

def chunk_rows_for_id(rows, frame_skip, fps):
    """
    Given a list of dicts: [{'time_code': x, 'emotion': y}, ...] sorted by time_code,
    produce a list of chunks. Each chunk = (start, end, emotion).

    We consider two frames "adjacent" if their time_code difference
    is close to (frame_skip / fps), within a small epsilon.
    """
    if not rows:
        return []
    
    frame_duration = frame_skip / fps
    epsilon = frame_duration * 0.5  # tolerance for floating artifacts, tweak if needed

    chunks = []
    
    # Start first chunk
    current_emotion = rows[0]['emotion']
    chunk_start_time = rows[0]['time_code']
    last_time = rows[0]['time_code']
    
    for i in range(1, len(rows)):
        this_time = rows[i]['time_code']
        this_emotion = rows[i]['emotion']
        
        # Check if same emotion AND is "consecutive" in time:
        if (this_emotion == current_emotion
            and abs(this_time - (last_time + frame_duration)) <= epsilon):
            # We continue the chunk
            last_time = this_time
        else:
            # Close out the previous chunk
            chunk_end_time = last_time + frame_duration
            chunks.append((chunk_start_time, chunk_end_time, current_emotion))
            
            # Start a new chunk
            current_emotion = this_emotion
            chunk_start_time = this_time
            last_time = this_time
    
    # Close the final chunk
    final_end_time = last_time + frame_duration
    chunks.append((chunk_start_time, final_end_time, current_emotion))
    
    return chunks

def build_elan_header(video_path, max_time, frame_skip, fps):
    """
    Build the #file:///... line, with:
      - offset: 0
      - duration in HH:MM:SS.mmm and in plain seconds, plus ms
      - ms per sample
    """
    # Round total duration to 3 decimals
    duration_rounded = round(max_time, 3)
    
    # Convert to HH:MM:SS.mmm
    duration_str = hhmmss_milli(duration_rounded)
    
    # Also as milliseconds
    duration_ms = int(round(duration_rounded * 1000))
    
    # ms per sample
    ms_per_sample = (1000.0 * frame_skip / fps)
    ms_per_sample_str = f"{ms_per_sample:.3f}"
    
    # Possibly convert video_path to a "file:///..." URL format
    # If it's not already "file://", let's do a naive transform:
    if not video_path.startswith("file:///"):
        # Escape spaces if needed, etc. For simplicity:
        video_path_url = "file://" + video_path
    else:
        video_path_url = video_path
    
    header = (
        f"#{video_path_url} -- offset: 0, "
        f"duration: {duration_str} / {duration_rounded} / {duration_ms}, "
        f"ms per sample: {ms_per_sample_str}"
    )
    return header

def write_elan_output(txt_path, metadata, all_chunks):
    """
    Write to a .txt file:
    1) The header line
    2) Then lines for each chunk:
         {ID}-EMOTION-AutoLabel   ID   start   end   duration   emotion
    """
    # all_chunks is a list of (id, chunk_start, chunk_end, emotion)
    # We first find the max end time so we can compute the overall duration
    max_time = 0.0
    for c in all_chunks:
        # c = (face_id, start, end, emotion)
        _, start, end, _ = c
        if end > max_time:
            max_time = end
    
    header_line = build_elan_header(
        metadata['video_path'],
        max_time,
        metadata['frame_skip'],
        metadata['video_fps']
    )
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(header_line + "\n\n")
        
        # Write each chunk
        for c in all_chunks:
            face_id, start, end, emotion = c
            start_rounded = round(start, 3)
            end_rounded = round(end, 3)
            duration_rounded = round(end_rounded - start_rounded, 3)
            
            # Format them with at most 3 decimals
            # e.g. 1.200 is okay if we do f"{val:.3f}"
            f.write(f"{face_id}-EMOTION-AutoLabel\t"
                    f"{face_id}\t"
                    f"{start_rounded:.3f}\t"
                    f"{end_rounded:.3f}\t"
                    f"{duration_rounded:.3f}\t"
                    f"{emotion}\n")

def convert_csv_to_elan(csv_path):
    """
    High-level function to coordinate everything.
    """
    # 1) Read CSV
    metadata, rows_by_id = read_csv_and_group_by_id(csv_path)
    
    # 2) For each ID, chunk up rows
    all_chunks = []
    for face_id, rows in rows_by_id.items():
        chunks_for_id = chunk_rows_for_id(rows, metadata['frame_skip'], metadata['video_fps'])
        # Each chunk is (start, end, emotion)
        # We need to store ID too
        for (st, en, em) in chunks_for_id:
            all_chunks.append((face_id, st, en, em))
    
    # 3) Sort all_chunks by face_id, then by start time
    all_chunks.sort(key=lambda c: (c[0], c[1]))
    
    # 4) Build output path
    base, _ = os.path.splitext(csv_path)
    txt_path = base + ".txt"
    
    # 5) Write out
    write_elan_output(txt_path, metadata, all_chunks)

#
# If you want to run this from command line:
#
if __name__ == "__main__":
    # Example usage:
    # python convert_csv_to_elan.py /path/to/myfile.csv
    import sys
    if len(sys.argv) < 2:
        print("Usage: python convert_csv_to_elan.py <csv_path>")
        sys.exit(1)
    csv_path = sys.argv[1]
    convert_csv_to_elan(csv_path)
    print(f"Done! Created {os.path.splitext(csv_path)[0] + '.txt'}")
