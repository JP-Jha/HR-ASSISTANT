from django.urls import path
from face_recognition import views

urlpatterns = [
    path("capture_faces/", views.capture_faces, name="capture_faces"),
]
