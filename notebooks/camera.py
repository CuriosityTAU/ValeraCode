import cv2
from global_definitions import LEAN_SETUP, SHOW_CAMERA
if not LEAN_SETUP:
    from deepface import DeepFace

print("Setting camera ...")

if LEAN_SETUP:
    camera_processes = {
        "face": False,
        "emotion": False
    }
else:
    camera_processes = {
        "face": True,
        "emotion": True
    }

def start_camera(update_user=None):
    # initialize camera
    try:
        camera = cv2.VideoCapture(0)
        camera_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        print('Camera width:', camera_width)
        if camera_width < 1.0:
            print('Camera not connected!')    
    except:
        print('Camera not connected!')
    try:
        while True:
            ret, frame = camera.read()
    
            if not ret:
                break

            if camera_processes["face"]:
                detections = DeepFace.extract_faces(frame, enforce_detection=False)
                for d, detection in enumerate(detections):
                    user = {'face': detection}
                    x, y, w, h = detection['facial_area']['x'], detection['facial_area']['y'], detection['facial_area']['w'], detection['facial_area']['h']
                    if SHOW_CAMERA:
                        cv2.rectangle(frame, (x,y), (x+w, y+h), (255, 0, 0), 2)

                    if camera_processes["emotion"]:
                        try:
                            analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                            emotion = analysis[d]['emotion']
                            dominant_emotion = max(emotion, key=emotion.get)
                            user['emotion'] = dominant_emotion
                            if SHOW_CAMERA:
                                cv2.putText(frame, dominant_emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (366, 255, 12), 2)
                        except Exception as e:
                            print(e)
                    if update_user:
                        update_user(user)
            if SHOW_CAMERA:
                cv2.imshow('Live Face Detection', frame)
        
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        camera.release()
        if SHOW_CAMERA:
            cv2.destroyAllWindows()