import face_recognition
import cv2
from datetime import datetime, timedelta
import numpy as np
import pickle
import os
from monitor_upload_v2 import load_data

known_face_encodings = []
known_face_names = []

facial_encodings_folder = 'data_SmartDoorbell/'


def load_facial_encodings_and_names_from_memory():
    for filename in os.listdir(facial_encodings_folder):
        known_face_names.append(filename[:-4])
        with open(facial_encodings_folder + filename, 'rb') as fp:
            known_face_encodings.append(pickle.load(fp)[0])

def run_recognition():
    video_capture = cv2.VideoCapture(1)
    count_notification = 0
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)
                print(face_names)
                count_notification +=1
                start = datetime.now()
                label = start.strftime("%Y-%m-%d_%H-%M-%S")
                if face_names != ['owner'] and count_notification > 100:
                    cv2.imwrite('image/' + str(label) + "_image.jpg", frame)
                    load_data()
                    count_notification =0
        process_this_frame = not process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    load_facial_encodings_and_names_from_memory()
    run_recognition()