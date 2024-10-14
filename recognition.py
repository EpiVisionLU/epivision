from deepface import DeepFace
import matplotlib.pyplot as plt
import cv2
import pandas as pd
import os




#Print X and Y values of where the face is
def print_facial_coordinates(faces):
    for i, face in enumerate(faces):
        facial_area = face.get("facial_area", {})
        x = facial_area.get("x", None)
        y = facial_area.get("y", None)
        
        # Print the X and Y values
        print(f"Face {i + 1}: X = {x}, Y = {y}")




def extract_faces(image_path):
    try:
        faces = DeepFace.extract_faces(img_path=image_path,detector_backend="retinaface") #testar retina face
        
        # Call the function to print X and Y coordinates
        print_facial_coordinates(faces)

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
    DeepFace.stream(db_path='face-db/', source=0)
