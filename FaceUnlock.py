import face_recognition
import cv2
import os
import dlib
from imutils import face_utils
import imutils
import subprocess
import re

# True = Unlocked
# False = Locked

POWER_MGMT_RE = re.compile(r'IOPowerManagement.*{(.*)}')

def display_status():
    output = subprocess.check_output(
        'ioreg -w 0 -c IODisplayWrangler -r IODisplayWrangler'.split())
    status = POWER_MGMT_RE.search(output).group(1)
    x = dict(("power", v) for (k, v) in (x.split('=') for x in status.split(',')))
    return(x["power"])


path = "/facedata"
known_face_encodings = []
known_face_names = []

def getImages(path):

    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]

    for imagePath in imagePaths:
        if imagePath == 'facedata/.DS_Store':
            continue  # ignores the .DS_Store file (hidden by default)
        name = os.path.split(imagePath)[-1].split(".")[0]
        known_face_names.append(name)
        known_face_encodings.append(
            face_recognition.face_encodings(face_recognition.load_image_file(imagePath))[0])


def faceUnlock():
    passwordstr = "password"
    while True:
        if display_status() == '1':
            video_capture = cv2.VideoCapture(0)

            face_locations = []
            face_encodings = []
            face_names = []
            process_this_frame = True

            getImages(path)
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
                    # If a match was found in known_face_encodings, just use the first one.
                    if True in matches:
                        first_match_index = matches.index(True)
                        os.system("""osascript -e 'tell application "system events" to key code 123'\nosascript -e 'tell application "system events" to keystroke """ + '"' + passwordstr + '"' + """'\nosascript -e 'tell application "system events" to keystroke return'""")
                        os.system("""caffeinate  -u -t 2""")
                        break
                        
            process_this_frame = not process_this_frame

                # Hit 'q' on the keyboard to quit!

            # Release handle to the webcam
            video_capture.release()
            cv2.destroyAllWindows()
        else:
            print(display_status())

faceUnlock()
