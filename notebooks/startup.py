from init_system import *
import cv2
from pyzbar.pyzbar import decode
from run_valera import *
from init_system import *

print("Runnning startup ...")

def read_qr_code():
    lesson_number = None
    # Initialize the camera
    cap = cv2.VideoCapture(0)  # 0 is typically the default camera
    print(cap)
    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Decode QR codes in the frame
            qr_codes = decode(frame)

            for qr_code in qr_codes:
                # Extract the bounding box location and the decoded data
                (x, y, w, h) = qr_code.rect
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                qr_data = qr_code.data.decode('utf-8')
                print(f"QR Code detected: {qr_data}")
                print(qr_data)
                if "lesson" in qr_data:
                    lesson_number = qr_data.split(" ")[-1]
                    break
            if lesson_number:
                break
            # Display the resulting frame
            cv2.imshow('Frame', frame)

            # Break the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()
    return lesson_number

# Run the QR code reader
lesson_number = read_qr_code()
print(lesson_number)
script = "assets/scripts/lesson_%s.txt" % lesson_number
print(script)
initialize()
beep(540)
full_run(script)
