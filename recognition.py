from deepface import DeepFace
import matplotlib.pyplot as plt
import cv2
import pandas as pd
import os
import requests
import time
import json
import random

#%% Improved function for camera movement calculation with limits

# Function to adjust camera movement based on pixel coordinates
def coordinate_modification(x, y, current_pan, current_tilt):
    '''

    Parameters
    ----------
    x : x value of item to track
    y : y value of item to track
    current_pan : Epi's current pan position 
    current_tilt : Epi's current tilt position 

    Returns
    -------
    target_pan_position : Absolute horizontal degrees of tracked object
    target_tilt_position : Absolute vertical degrees of tracked object

    '''
    
    # Video stream dimensions
    video_width = 640
    video_height = 480
    
    # Camera sensor field of view in degrees
    sensor_fov_width = 62.2
    sensor_fov_height = 48.8
    
    # Epi movement limitations in degrees (min, max)
    pan_limit = (-35, 40)
    tilt_limit = (-15, 30)
    
    # Calculate degrees per pixel for each axis
    horizontal_degrees_per_pixel = sensor_fov_width / video_width
    vertical_degrees_per_pixel = sensor_fov_height / video_height
    
    # Calculate pixel offset from center
    horizontal_offset = x - video_width / 2  # Positive if to the right of center
    vertical_offset = y - video_height / 2   # Positive if below the center
    
    # Convert pixel offset to degree adjustment
    pan_adjust = round(horizontal_offset * horizontal_degrees_per_pixel)
    tilt_adjust = round(vertical_offset * vertical_degrees_per_pixel)
    
    # Calculate the new target positions for pan and tilt, considering the current positions
    target_pan_position = current_pan + pan_adjust
    target_tilt_position = current_tilt + tilt_adjust
    
    # Enforce pan and tilt limits
    target_pan_position = max(pan_limit[0], min(target_pan_position, pan_limit[1]))
    target_tilt_position = max(tilt_limit[0], min(target_tilt_position, tilt_limit[1]))
    
    return target_pan_position, target_tilt_position

#%% Test coordinates
'''
# Proprioception: These are the current values for Epi's neck, saved as degrees.
epi_pan_pos = 0   # Current pan position in degrees
epi_tilt_pos = 0  # Current tilt position in degrees

# Example target pixel coordinates from the video stream
target_x = -23
target_y = 9250

# Calculate new pan and tilt positions
new_pan_pos, new_tilt_pos = coordinate_modification(target_x, target_y, epi_pan_pos, epi_tilt_pos)

# Output the movement commands for Epi
print(f"New pan position: {new_pan_pos} degrees, New tilt position: {new_tilt_pos} degrees.")

'''

#%%

#Print X and Y values of where the face is
def print_facial_coordinates(faces):
    for i, face in enumerate(faces):
        facial_area = face.get("facial_area", {})
        x = facial_area.get("x", None)
        y = facial_area.get("y", None)
        
        # Print the X and Y values
        print(f"Face {i + 1}: X = {x}, Y = {y}")


#Get X coordinate from faces we send in, does not do any own face recognition.
def get_face_x(faces):
    x_coordinates = []
    for face in faces:
        facial_area = face.get("facial_area", {})
        x = facial_area.get("x", None)
        
        # Append the X value to the list
        if x is not None:
            x_coordinates.append(x)
    
    return x_coordinates

# Get Y coordinate
def get_face_y(faces):
    y_coordinates = []
    for face in faces:
        facial_area = face.get("facial_area", {})
        y = facial_area.get("y", None)
        
        # Append the Y value to the list
        if y is not None:
            y_coordinates.append(y)
    
    return y_coordinates





def extract_faces(image_path):
    try:
        faces = DeepFace.extract_faces(img_path=image_path,detector_backend="retinaface") #testar retina face
        
        # Call the function to print X and Y coordinates
        #print_facial_coordinates(faces)
        #print(faces)

        #x_values = get_face_x(faces)
        #return x_values

        return faces

   
    except Exception as e:
        print("Error occured during face extraction")
        return None
   
   


def show_faces(faces):
    if faces:


        for i, face in enumerate(faces):
            plt.imshow(face['face'])
            plt.axis('off')
            plt.show() #vad gör detta?




    else:
        print("no faces to display:( ")




#From folder
def extract_faces_from_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            detected_faces = DeepFace.extract_faces(img_path=file_path, detector_backend="retinaface")
           
            if detected_faces:
                print(f"Face detected in {filename}")
            else:
                print(f"No face detected in {filename}")
               
        except Exception as e:
            print(f"Error extracting faces from {filename}: {e}")








#There are plenty of Models to choose from under model_name


models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace",
          "DeepFace", "DeepID", "ArcFace", "Dlib", "SFace"]


def verify_faces():
   
    result = DeepFace.verify(img1_path= "face-db/ruben-tapptorp/ruben1.jpg",
                            img2_path= "face-db/ruben-tapptorp/ruben3.jpg",
                            model_name= models[1])
   
   
   #This is to plot the faces, doesnt quite work, but isn't important either.
  #  fig, axs = plt.subplots(1,2, figsize=(15,5))
   # axs[0].imshow(plt.imread('face-db/ruben-tapptorp/ruben1.jpg'))
    #axs[1].imshow(plt.imread('face-db/ruben-tapptorp/ruben2.jpg'))
    #fig.suptitle(f"Verified {result['verified']} - Distance {result['distance']:0.4}") #tror 0.4 är hur säker den är
    #plt.show


    print ("Verified: ", result["verified"],
            "Distance: ", result["distance"],
            "Similarity_metric: ", result["similarity_metric"],
            "Threshold: ", result["threshold"],
            "Model: ", result["model"],
            "Detector backend: ", result["detector_backend"])
   


def find_faces():
    result = DeepFace.find(img_path='face-db/ruben-tapptorp/ruben4.jpg', db_path= 'face-db/')
   
    print(result)



#action specifierar vilken sak man analysar. Man kan strunta helt i denna parameter och analyseras allt.
def analyze_faces():
    result = DeepFace.analyze(img_path='face-db/ruben-tapptorp/ruben1.jpg', actions=['emotion']) 
    print(result)
    first_face = result[0]
    #race = first_face["race"]
    emotion = first_face["emotion"]
    print("Emotion analysis:", emotion)
    #pd.DataFrame(race, index=[0]).T.plot(kind="bar") #Index verkar bara förklara vad den blåa stapeln är?
    #plt.show()

def streaming():
    DeepFace.stream(db_path='face-db/', source= 0)  #source='http://righteye.local:8080/stream/video.mjpeg' för epi

# Send HTTP GET requests to control Epi


def control_epi():
    urls = [
        "http://localhost:8000/control/SR.positions/0/0/20",
        "http://localhost:8000/control/SR.positions/1/0/10",
        "http://localhost:8000/control/SR.positions/4/0/15",
        "http://localhost:8000/control/SR.positions/5/0/15"
    ]
    
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Response received from {url}: {response.json()}")
        else:
            print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")


def control_epi2(id, position, value):
    url = f"http://localhost:8000/control/SR.positions/{id}/{position}/{value}"
    response = requests.get(url)
    
    if response.status_code == 200:
        print(f"Response received from {url}: {response.json()}")
    else:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")






def temp_main ():
    camera_url='http://righteye.local:8080/stream/video.mjpeg'
    try:
        # Initialize video capture with the camera stream URL
        cap = cv2.VideoCapture(camera_url)
        x_values_list = []
        y_values_list = []

        # Set up the timer for a 5-second interval
        last_capture_time = time.time()

        #EPI KOLLAR KONSTANT, därav detta borde vara main?
        while True: 
            # Capture each frame from the live stream
            ret, frame = cap.read()
            if not ret:
                print("Failed to retrieve frame from the stream.")
                break

            # Check if 5 seconds have passed since the last capture
            current_time = time.time()
            if current_time - last_capture_time >= 5:
                # Process the frame to detect faces every 5 seconds
                # gammalt från faces = DeepFace.extract_faces(img_path=frame, detector_backend="retinaface")
                faces = extract_faces(frame)

                # Extract the X coordinates using the get_face_x function
                x_values = get_face_x(faces)
                y_values = get_face_y(faces)

                x_values_list.append(x_values)
                y_values_list.append(y_values)

                #X values for each processed frame
                print("x_values ",x_values[0])
                #temporärt, senare skickar vi in Simons metod här, ex 
                # actual_movement = coordiante_modification(x, x_values[0])
                control_epi2(1,0, (x_values[0]/50)) #ska vara actual_movement istället för x_values[0]/50

                
                #Y values for each processed frame
                print ("y_value", y_values[0])
                #temporärt, senare skickar vi in Simons metod här, ex 
                # actual_movement = coordiante_modification(y, y_values[0])

                control_epi2(0,0, (y_values[0]/50))  #ska vara actual_movement istället för y_values[0]/50

            

                # Update the last capture time
                last_capture_time = current_time

            # Optional: Display the frame in real-time (press 'q' to quit)
            cv2.imshow('Live Stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the video capture and close windows when done
        cap.release()
        cv2.destroyAllWindows()

        # Return all collected X coordinates
        #return x_values_list

    except Exception as e:
        print("An error occurred during live streaming:", e)
        return None
    


def write_to_json(file_path, people_data):
    """
    Appends face emotion analysis data to a JSON file.

    Args:
        file_path (str): The path to the JSON file.
        people_data (list): A list of dictionaries containing the analysis data.
    """
    try:
        # Load existing data if the file exists, or initialize an empty structure
        try:
            with open(file_path, "r") as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = {"people": []}

        # Append new data
        data["people"].extend(people_data)

        # Write updated data back to the file
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
    except Exception as e:
        print(f"An error occurred while writing to the JSON file: {e}")

def analyze_emotion_live(source='stream'):
    """
    Analyzes emotions live from a video source and writes the results to a JSON file.

    Args:
        source (str): 'stream' for camera URL or 'webcam' for webcam feed.
    """
    camera_url = 'http://righteye.local:8080/stream/video.mjpeg'
    video_source = 0 if source == 'webcam' else camera_url  # 0 for the default webcam
    output_file = "people.json"  # File to store JSON data

    try:
        # Initialize video capture with the chosen source
        cap = cv2.VideoCapture(video_source)

        # Set up the timer for an interval
        last_capture_time = time.time()

        while True:
            # Capture each frame from the video source
            ret, frame = cap.read()
            if not ret:
                print("Failed to retrieve frame from the video source.")
                break

            # Check if X seconds have passed since the last analysis
            current_time = time.time()
            if current_time - last_capture_time >= 1:  # Interval in seconds
                try:
                    # Analyze the frame for emotion
                    result = DeepFace.analyze(img_path=frame, actions=['emotion'], enforce_detection=False)
                
                    if result:
                        # Prepare data for each detected face
                        people_data = []
                        for idx, face in enumerate(result):
                            emotion_scores = face['emotion']
                            dominant_emotion = face['dominant_emotion']
                            # Placeholder positions (you can update this with actual face coordinates later)
                            face_position_x = face['region']['x']  # Replace with actual data if available
                            face_position_y = face['region']['y']  # Replace with actual data if available

                            # Build the data structure for this face
                            people_data.append({
                                "Name": str(idx),  # Placeholder name
                                "Dominant Emotion": dominant_emotion,
                                "Emotion Scores": emotion_scores,
                                "Face Position X": face_position_x,
                                "Face Position Y": face_position_y
                            })

                        # Write to the JSON file
                        write_to_json(output_file, people_data)

                except Exception as e:
                    print(f"An error occurred while analyzing the frame: {e}")

                # Update the last capture time
                last_capture_time = current_time

            # Optional: Display the frame in real-time (press 'q' to quit)
            cv2.imshow('Live Stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the video capture and close windows when done
        cap.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print("An error occurred during live streaming:", e)



    # Exempel json
    '''
    Alternativ 1, Sortera efter emotions:
    emotions.json
    [
    {
    "Dominant emotions": ["Happy", "Sad"], (alternativt en siffra och sen allocatar vi varje känsla till en siffra)
    "Emotion scores": [{
        "angry": 0.1, 
        "sad": 0.1,
        "happy": 0.8
        },
        {
        "angry": 0.1,
        "sad": 0.8,
        "happy": 0.1
        }],
    "Face position X": [120, 300],
    "Face Position Y": [180, 54],
    "People": ["Ruben", "Simon"]
    }
    ]

    Alternativ 2, sortera efter personer:
    people.json
    
    
    {"people":
    [
    {
    "Name": "Ruben",
    "Dominant Emotion": "Happy",
    "Emotion Scores": {
        "angry": 0.1, 
        "sad": 0.1,
        "happy": 0.8
        },
    "Face Position X": 120,
    "Face Position Y": 180
    },

    {
    "Name": "Simon",
    "Dominant Emotion": "Sad",
    "Emotion Scores": {
        "angry": 0.1, 
        "sad": 0.8,
        "happy": 0.1
        },
    "Face Position X": 300,
    "Face Position Y": 54
    }
    ]
    }
      



    '''


def demo_mode(source='stream', detector_backend='mtcnn'):
    """
    Demonstrates real-time emotion analysis with bounding boxes and overlays.
    Adds toggles for motion (m) and speech (s).
    Press 'q' to exit the demo.
    """

    # URL for Epi's camera
    camera_url = 'http://righteye.local:8080/stream/video.mjpeg'
    video_source = 0 if source == 'webcam' else camera_url  # 0 uses default webcam

    # Motion mappings for recognized emotions
    motion_map = {
        'happy':    [12, 15],
        'angry':    [7, 16],
        'surprise': [8, 14],
        'sad':      [6, 13],
        'neutral':  [5, 9, 10, 11]
    }
    # If no emotions for 10 seconds => random idle from this list:
    idle_motions = [2, 3, 4, 17, 18, 19]

    try:
        # Initialize video capture
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"Could not open video source: {video_source}")
            return

        # Timers and toggles
        last_capture_time = time.time()      # For DeepFace analysis
        faces_current_analysis = None        # Latest deepface result

        motion_enabled = False
        speech_enabled = False

        time_last_motion = 0.0      # Last time we triggered ANY motion
        time_last_emotion = time.time()  # Last time we detected at least one face's emotion
        motion_cooldown = 10.0      # 10-second cooldown after triggering motion

        time_last_speech = 0.0      # Last time we triggered speech
        speech_cooldown = 10.0      # 10-second cooldown after speaking

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to retrieve frame from the video source.")
                break

            current_time = time.time()

            # 1) PERIODIC EMOTION ANALYSIS (like before)
            if current_time - last_capture_time >= 1:  # Adjust interval if needed
                try:
                    result = DeepFace.analyze(
                        img_path=frame,
                        actions=['emotion'],
                        detector_backend=detector_backend,
                        enforce_detection=False  # set True if you want strict detection
                    )
                    faces_current_analysis = result
                except Exception as e:
                    # Keep the old faces_current_analysis if an error occurs
                    print(f"An error occurred during DeepFace analysis: {e}")
                last_capture_time = current_time

            # 2) OVERLAY RESULTS IF AVAILABLE
            distinct_emotions_in_frame = set()
            if faces_current_analysis:
                # DeepFace might return a single dict or a list of dicts
                if isinstance(faces_current_analysis, dict):
                    faces_to_draw = [faces_current_analysis]
                else:
                    faces_to_draw = faces_current_analysis

                for idx, face_data in enumerate(faces_to_draw):
                    # -- 2a) Draw bounding box
                    region = face_data.get('region', {})
                    x = region.get('x', 0)
                    y = region.get('y', 0)
                    w = region.get('w', 0)
                    h = region.get('h', 0)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # -- 2b) Label above face box
                    label_text = f"Person {idx}"
                    cv2.putText(frame, label_text, (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                    # -- 2c) Emotions
                    dom_emotion = face_data.get('dominant_emotion', '').lower()
                    if dom_emotion:
                        distinct_emotions_in_frame.add(dom_emotion)

                    emotions = face_data.get('emotion', {})

                    # -- 2d) Draw overlay box
                    overlay_x1 = x + w + 10
                    overlay_y1 = y
                    overlay_width = 210
                    overlay_height = 240
                    overlay_x2 = overlay_x1 + overlay_width
                    overlay_y2 = overlay_y1 + overlay_height

                    overlay = frame.copy()
                    cv2.rectangle(overlay, (overlay_x1, overlay_y1),
                                  (overlay_x2, overlay_y2), (0, 0, 0), -1)
                    alpha = 0.5
                    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

                    # Dominant emotion text
                    cv2.putText(frame, f"Dominant: {dom_emotion}",
                                (overlay_x1 + 5, overlay_y1 + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    # Draw bar chart for known emotions
                    bar_left = overlay_x1 + 80
                    bar_top_start = overlay_y1 + 40
                    bar_height = 12
                    gap = 15
                    emotion_order = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

                    for i, emo_name in enumerate(emotion_order):
                        emo_val = emotions.get(emo_name, 0.0)
                        bar_length = int(min(emo_val, 100) / 100 * 100)

                        top_y = bar_top_start + i * (bar_height + gap)
                        if dom_emotion == emo_name:
                            bar_color = (0, 255, 255)
                        else:
                            bar_color = (255, 255, 255)

                        cv2.putText(frame, f"{emo_name}",
                                    (overlay_x1 + 5, top_y + bar_height - 2),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                        cv2.rectangle(frame, (bar_left, top_y),
                                      (bar_left + bar_length, top_y + bar_height),
                                      bar_color, -1)

            # 3) MOTION LOGIC (if motion_enabled)
            # If at least one face/emotion is found, update `time_last_emotion`
            if len(distinct_emotions_in_frame) > 0:
                time_last_emotion = current_time

            if motion_enabled:
                # Check if we are outside the motion cooldown
                if (current_time - time_last_motion) >= motion_cooldown:
                    # If we have at least one recognized emotion, trigger the mapped motion
                    if distinct_emotions_in_frame:
                        # Build a combined list of possible motions
                        possible_motions = []
                        for emo in distinct_emotions_in_frame:
                            if emo in motion_map:
                                possible_motions.extend(motion_map[emo])
                        # If we found at least one possible motion, pick one randomly
                        if possible_motions:
                            chosen = random.choice(possible_motions)
                            trigger_motion(chosen)
                            time_last_motion = current_time
                    else:
                        # If NO emotion for 10 seconds => random idle motion
                        # Check how long it's been since we last saw any emotion
                        if (current_time - time_last_emotion) >= 10.0:
                            chosen = random.choice(idle_motions)
                            trigger_motion(chosen)
                            # Reset both motion and "last emotion" timers
                            time_last_motion = current_time
                            time_last_emotion = current_time

            # 4) SPEECH LOGIC (if speech_enabled)
            # Every 10s, speak the distinct emotions if we see any faces
            if speech_enabled:
                if (current_time - time_last_speech) >= speech_cooldown:
                    if len(distinct_emotions_in_frame) > 0:
                        # Build a phrase from distinct emotions, e.g. "happy, sad"
                        # Convert spaces to underscores
                        # (DeepFace often has "fear" / "angry" etc. which are single words, but let's be safe)
                        phrase = ", ".join(distinct_emotions_in_frame)
                        phrase = phrase.replace(" ", "_")
                        trigger_speech(phrase)
                        time_last_speech = current_time

            # 5) DISPLAY FRAME
            cv2.imshow('Demo Mode Stream', frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                # Quit
                break
            elif key == ord('m'):
                # Toggle motion
                motion_enabled = not motion_enabled
                print(f"Motion enabled: {motion_enabled}")
            elif key == ord('s'):
                # Toggle speech
                speech_enabled = not speech_enabled
                print(f"Speech enabled: {speech_enabled}")

        # Cleanup
        cap.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"An error occurred in demo_mode: {e}")


def trigger_motion(sequence_number):
    """
    Sends an HTTP request to trigger a motion in Ikaros via:
    http://127.0.0.1:8000/command/SR.trig/{sequence_number}/0/0
    """
    url = f"http://127.0.0.1:8000/command/SR.trig/{sequence_number}/0/0"
    try:
        requests.get(url, timeout=1.0)  # 1-second timeout just to be safe
        print(f"Triggered motion: {sequence_number}")
    except Exception as ex:
        print(f"Error triggering motion ({sequence_number}): {ex}")


def trigger_speech(text):
    """
    Sends an HTTP request for Epi to speak the given text:
    http://127.0.0.1:8000/command/EpiSpeech.say/0/0/...
    Spaces should be replaced with underscores or properly URL-encoded.
    """
    # Replace any spaces with underscores, if still present
    text = text.replace(" ", "_")
    url = f"http://127.0.0.1:8000/command/EpiSpeech.say/0/0/{text}"
    try:
        requests.get(url, timeout=2.0)
        print(f"Epi says: {text}")
    except Exception as ex:
        print(f"Error triggering speech ({text}): {ex}")