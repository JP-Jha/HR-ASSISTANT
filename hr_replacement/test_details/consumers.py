import cv2
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.decorators import login_required
import os

# Load face detection model
face_cascade = cv2.CascadeClassifier('D:/HR_Project/HR_REPLACEMENT/hr_replacement/static/Harcascadefile/haarcascade_frontalface_default.xml')

# @login_required
# class VideoStreamConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         self.email = self.scope['user'].email
#         self.recognizer = None
        
#         # Load the model for the specific user (if it exists)
#         model_path = os.path.join('/home/anupam/HR_FINAL/HR_REPLACEMENT/hr_replacement/static/models', self.email, f'{self.email}_trainer.yml')
#         if os.path.exists(model_path):
#             self.recognizer = cv2.face.LBPHFaceRecognizer_create()
#             self.recognizer.read(model_path)
#         else:
#             print("Model for user not found.")
#             await self.send(text_data="Model not found for user.")
        
#         # Accept the WebSocket connection
#         await self.accept()
#         print(f"WebSocket connection established for {self.email}.")

#     async def disconnect(self, close_code):
#         print(f"WebSocket connection closed for {self.email}.")

#     async def receive(self, text_data=None, bytes_data=None):
#         if bytes_data:
#             video_frame = np.frombuffer(bytes_data, np.uint8)
#             frame = cv2.imdecode(video_frame, cv2.IMREAD_COLOR)

#             # Convert to grayscale for face detection
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

#             # Draw face rectangles and process for recognition
#             if len(faces) > 0:
#                 for (x, y, w, h) in faces:
#                     # Draw a rectangle around the detected face
#                     cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
#                     roi_gray = gray[y:y + h, x:x + w]

#                     # Recognize face if the recognizer is available
#                     if self.recognizer is not None:
#                         label, confidence = self.recognizer.predict(roi_gray)
#                         if confidence > 60:
#                             cv2.putText(frame, f"Label: {label}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
#                         else:
#                             cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
#                     else:
#                         cv2.putText(frame, "Model not loaded", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

#             # Send processed frame back to WebSocket client
#             _, buffer = cv2.imencode('.jpg', frame)
#             frame_data = buffer.tobytes()
#             await self.send(bytes_data=frame_data)


# consumers.py
import cv2
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
import os

# Load face detection model
face_cascade = cv2.CascadeClassifier('D:/HR_Project/HR_REPLACEMENT/hr_replacement/static/Harcascadefile/haarcascade_frontalface_default.xml')

class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.email = self.scope['user'].email
        self.recognizer = None
        self.count = 0 
        # self.total_count = self.count  # Initialize count at the start of each WebSocket connection

        # Load the model for the specific user (if it exists)
        model_path = os.path.join('D:/HR_Project/HR_REPLACEMENT/hr_replacement/face_recognition/templates/models', self.email, f'{self.email}_trainer.yml')
        print(model_path)

        # Load model if it exists, otherwise inform the user and exit
        if os.path.exists(model_path):
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.recognizer.read(model_path)
        else:
            print("Model for user not found.")
            await self.accept()  # Accept the WebSocket connection before sending message
            await self.send(text_data="Model not found for user.")
            return  # Exit the connection if model is not found

        # Accept the WebSocket connection after loading the model
        await self.accept()
        print(f"WebSocket connection established for {self.email}.")

    async def disconnect(self, close_code):
        print(f"WebSocket connection closed for {self.email}.")
        # Print the total count of faces out of bounds when the connection is closed
        print(f"Total faces out of bounds: {self.count}")

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            video_frame = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(video_frame, cv2.IMREAD_COLOR)

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            height, width, channels = frame.shape

            # Face detection
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            cv2.rectangle(frame, (0, 0), (width, height), (255, 0, 0), 2)

            # Detect faces and process out-of-bounds logic
            buffer = 10  # Buffer to check boundaries
            if len(faces) == 0:
                cv2.putText(frame, "Warning: No face detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                print("No face detected")

            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    # Draw a rectangle around the detected face
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    # Check if the face rectangle is within the frame boundaries
                    if x < buffer or y < buffer or x + w > width - buffer or y + h > height - buffer:
                        # If the rectangle is out of bounds, show a warning and increment the count
                        self.count += 1
                        print("Warning: Face rectangle is out of bounds.")
                        cv2.putText(frame, "Face out of bounds!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    roi_gray = gray[y:y + h, x:x + w]

                    # Recognize face if the recognizer is available
                    if self.recognizer is not None:
                        label, confidence = self.recognizer.predict(roi_gray)
                        if confidence > 70:
                            cv2.putText(frame, f"{self.email}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        else:
                            cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    else:
                        cv2.putText(frame, "Model not loaded", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Send processed frame back to WebSocket client
            _, buffer = cv2.imencode('.jpeg', frame)
            frame_data = buffer.tobytes()
            await self.send(bytes_data=frame_data)
