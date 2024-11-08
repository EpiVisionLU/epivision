from deepface import DeepFace
from recognition import extract_faces, show_faces, verify_faces, find_faces, analyze_faces, streaming, extract_faces_from_folder, control_epi, control_epi2, get_x_live
import matplotlib.pyplot as plt
import cv2




def main():
   
    #Extract and show face from one image
    image_path = 'Epi-bilder/color2955.jpg'
    #faces = extract_faces(image_path)
    #show_faces(faces)


    #Find multiple faces in a folder
    #folder_path = 'flerabilder'
    #faces = extract_faces_from_folder(folder_path)
   


    #Face Verification
    #verify_faces()




    #Find Faces
    #find_faces()


    #Analyze Faces
    #analyze_faces()


    #Streaming
    #streaming()

    #Motor control
    #control_epi()

    #control_epi2(1,0,0)
   
    get_x_live()

    






if __name__ == "__main__": #tror detta kör main
    main()