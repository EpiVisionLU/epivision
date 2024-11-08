from deepface import DeepFace
import matplotlib.pyplot as plt
import cv2
import pandas as pd
import os
import requests
import time


#Simons funktion
# def coordinate_modification(coordinate, value): 
#   Code code code...
#   .....
#   return actual_movement           
# 
# Coordinate är om det är X eller Y, value är värdet på koordinaten
# actual_movement är värdet som vi skickar till Epi i hur mycket den ska röra sig. det som brukar vara mellan -30 och 30


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




def analyze_faces():
    result = DeepFace.analyze(img_path='face-db/ruben-tapptorp/ruben3.jpg')
    #print(result)
    first_face = result[0]
    race = first_face["race"]
    pd.DataFrame(race, index=[0]).T.plot(kind="bar")
    plt.show()

def streaming():
    DeepFace.stream(db_path='face-db/', source='http://righteye.local:8080/stream/video.mjpeg') 

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






#Ska snyggas till 
"""
def live_movement():
    camera_url='http://righteye.local:8080/stream/video.mjpeg'
    try:
        # Initialize video capture with the camera stream URL
        cap = cv2.VideoCapture(camera_url)
        x_values_list = []
        y_values_list = []

        # Set up the timer for a 5-second interval
        last_capture_time = time.time()

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
                faces = DeepFace.extract_faces(img_path=frame, detector_backend="retinaface")

                # Extract the X coordinates using the get_face_x function
                x_values = get_face_x(faces)
                x_values_list.append(x_values)

                #Extract the Y coordinate using get_face_y
        


                # Print or log the X values for each processed frame
                print("X coordinates of faces:", x_values)
                #control_epi2(1,0,10)
                print("x_values ",x_values[0])
                control_epi2(1,0, (x_values[0]/50))
                #control_epi2(1,0,0)

            

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
        return x_values_list

    except Exception as e:
        print("An error occurred during live streaming:", e)
        return None

# Example usage:
# x_coordinates_over_time = get_x_live()
# print("Collected X coordinates:", x_coordinates_over_time)

"""


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
    

