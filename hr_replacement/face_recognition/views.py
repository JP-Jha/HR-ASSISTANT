import base64
import json
import cv2
import os
import shutil
import numpy as np
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from deepface import DeepFace
from django.contrib.auth.decorators import login_required
import logging
from scipy.spatial.distance import cosine
import base64
import cv2
import numpy as np
# Logger setup
logger = logging.getLogger(__name__)

# Ensure CUDA is disabled if you are not using GPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Disables GPU


@login_required
def capture_faces(request):
    if request.method == "POST":
        data = json.loads(request.body)
        image_data = data.get("image")# Remove data URL prefix
        if not image_data:
            return JsonResponse({"message": "No image data provided"}, status=400)
    


        image_bytes = base64.b64decode(image_data.split(",")[1])
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        email = request.user.email
        base_path = "/home/anupam/HR_FINAL/HR_REPLACEMENT/hr_replacement/static/clicked_images"
        model_path = "/home/anupam/HR_FINAL/HR_REPLACEMENT/hr_replacement/face_recognition/templates/models"
        person_img_dir = os.path.join(base_path, email)
        print(f'*********************************person image diredctory***********{person_img_dir}')

        # Create user-specific directory for saving images
        try:
            os.makedirs(person_img_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directory for user {email}: {str(e)}")
            return HttpResponse("Error creating directory. Please try again.")

        # Load face cascade
        try:
            face_cascade = cv2.CascadeClassifier(
                'D:/HR_Project/HR_REPLACEMENT/hr_replacement/static/Harcascadefile/haarcascade_frontalface_default.xml'
            )
            if face_cascade.empty():
                raise Exception("Failed to load the face cascade.")
        except Exception as e:
            logger.error(f"Error loading face cascade: {str(e)}")
            return HttpResponse("Face detection setup failed. Please try again.")

        # # Initialize video capture
        # try:
        #     cap = cv2.VideoCapture(0)
        #     if not cap.isOpened():
        #         raise Exception("Camera not accessible.")
        # except Exception as e:
        #     logger.error(f"Error initializing camera: {str(e)}")
        #     return HttpResponse(f"Error initializing camera: {str(e)}")

        count = 0

        # Capture 5 images
        while count < 5:
            # # ret, frame = cap.read()
            # if not ret:
            #     logger.warning("Failed to capture frame from camera.")
            #     break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            print(f"frame is initilized")
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                count += 1
                face_img = frame[y:y + h, x:x + w]
                face_img = cv2.resize(face_img, (200, 200))
                filename = os.path.join(person_img_dir, f"{email}{count}.jpeg")
                cv2.imwrite(filename, face_img, [cv2.IMWRITE_JPEG_QUALITY, 90])

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # cv2.destroyAllWindows()

        # Verify and compare images
        clicked_images = verify_images(base_path, email)
        print(f'******************************************clicked images*****************************{clicked_images}')
        if not clicked_images:
            return HttpResponse("Failed to load clicked images. Please try again.")

        profile_image = verify_images('/home/anupam/HR_FINAL/HR_REPLACEMENT/hr_replacement/static/upload_images/profile_images', email)
        print(f'******************************************profile image **************************************8{profile_image}')

        if not profile_image:
            return HttpResponse("Failed to load profile image. Please try again.")

        verification=face_match(clicked_images, profile_image)
        # print(verification)
        print(verification)
        if verification:
            train=train_model(person_img_dir, face_cascade, count, email, model_path=model_path)
            print(train)
            return redirect('rules')
        else:
            shutil.rmtree(person_img_dir, ignore_errors=True)
            return redirect('/face/capture_faces/')

    return render(request, "face_recognition.html")

def verify_images(path, email):
    img_path = os.path.join(path, email)
    filetype = '.jpeg'
    images = []
    for root, dirs, files in os.walk(img_path):
        for file in files:
            if file.lower().endswith(filetype.lower()):
                images.append(os.path.join(root, file))
    
    # Ensure there's at least one image
    if not images:
        return None
    return images[0]  # Return the first image found


def face_match(clicked_images, profile_image):
    try:
        # Ensure clicked_images and profile_image are not empty
        if not clicked_images or not profile_image:
            raise ValueError("One or both images are missing.")

        verification = DeepFace.verify(
            img1_path=clicked_images,  # Single image path
            img2_path=profile_image    # Single image path
        )
        return verification["verified"]
    except Exception as e:
        logger.error(f"Error during face match: {str(e)}")
        return False



def train_model(person_img_dir, face_cascade, count, email, model_path):
    images = []
    labels = []

    try:
        for filename in os.listdir(person_img_dir):
            if filename.endswith(".jpeg"):
                img_path = os.path.join(person_img_dir, filename)
                img = cv2.imread(img_path)
                if img is None:
                    logger.warning(f"Error loading image: {img_path}")
                    continue

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20))

                for (x, y, w, h) in faces:
                    face_img = gray[y:y + h, x:x + w]
                    face_img = cv2.resize(face_img, (100, 100))
                    images.append(face_img)
                    labels.append(count)

        if not images:
            logger.warning(f"No faces to train on for {email}.")
            return HttpResponse("No faces found for training. Please try again.")

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(images, np.array(labels))

        user_model_path = os.path.join(model_path, email)
        os.makedirs(user_model_path, exist_ok=True)
        recognizer.save(os.path.join(user_model_path, f'{email}_trainer.yml'))
        logger.info(f"Model saved for {email}")
    except Exception as e:
        logger.error(f"Error during model training for {email}: {str(e)}")
