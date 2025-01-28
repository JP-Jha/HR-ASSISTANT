from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from test_details.models import Candidate
from datetime import datetime, timedelta
from .utils import send_email_to_client
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
import json
import random
import os
import ast


# Path to your dataset folder
DATASET_PATH = r"/home/anupam/HR_FINAL/HR_REPLACEMENT/hr_replacement/Question_final_dataset"
GENERAL_SKILLS = ['data structures', 'object oriented programming']


def condidate_register(request):
    if request.method == "POST":
        # Get form data
        first_name = request.POST.get('c_first_name')
        last_name = request.POST.get('c_last_name')
        c_father_name = request.POST.get('c_father_name')
        c_mother_name = request.POST.get('c_mother_name')
        c_email = request.POST.get('c_email')
        c_contact_number = request.POST.get('c_contact_number')
        c_dob = request.POST.get('c_dob')
        c_sex = request.POST.get('c_sex')  # Getting gender from form
        c_city = request.POST.get('c_city')
        c_state = request.POST.get('c_state')
        country = request.POST.get('country')
        c_pic = request.FILES.get('c_pic')  # File upload handling
        c_resume = request.FILES.get('c_resume')  # File upload handling
        user_skills = request.POST.get("c_skills").split(",")
        c_skills = [skill.strip().lower() for skill in user_skills] + GENERAL_SKILLS
        time_slot = request.POST.get('time_slot')

        # Check if the email already exists in the database
        if Candidate.objects.filter(c_email=c_email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, "register.html")

        # Convert time_slot to datetime if present
        time_slot = request.POST.get('time_slot')
        if time_slot:
            try:
                time_slot = datetime.strptime(time_slot, "%Y-%m-%dT%H:%M")  # Adjusted format
                time_slot = timezone.make_aware(time_slot)
            except ValueError:
                messages.error(request, "Invalid time format for the time slot.")
                return render(request, "register.html")

        # Create and save candidate
        candidate = Candidate.objects.create(
            c_first_name=first_name,
            c_last_name=last_name,
            c_father_name=c_father_name,
            c_mother_name=c_mother_name,
            c_email=c_email,
            c_contact_number=c_contact_number,
            c_dob=c_dob,
            c_sex=c_sex,
            c_city=c_city,
            c_state=c_state,
            country=country,
            c_pic=c_pic,
            c_resume=c_resume,
            c_skills=c_skills,
            time_slot=time_slot
        )
        candidate.save()
        messages.success(request, "Candidate registered successfully.")

        # Call fake_account function and handle error or success
        result = fake_account(c_email)
        if "error" in result:
            messages.error(request, result["error"])
        else:
            messages.success(request, result["success"])

        # return redirect('/custom_login/')  # Replace with your actual success page URL
        # Redirect to the congratulations page
        return redirect('congratulations')  # 'congratulations' is the name of your URL for the success page

    return render(request, "register.html")


def fake_account(email):
    # Ensure there is at least one Candidate
    User = get_user_model()
    last_candidate = Candidate.objects.filter(c_email=email).first()
    
    if not last_candidate:
        return {"error": "No candidates found."}

    # Generate a fake password using the correct method
    fake_password = get_random_string(
        length=12,
        allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789@#*'
    )
    
    # Create a User for the Candidate
    new_user = User.objects.create_user(  # Use create_user to ensure proper password hashing
        username=last_candidate.c_id,  # Use c_id (UUID) as the username
        email=last_candidate.c_email,  # Optional: Use the candidate's email
    )
    new_user.set_password(fake_password)  # Set the generated password
    new_user.is_active = True
    new_user.save()

    # Send email to the Candidate
    send_email_to_client(last_candidate.c_email, last_candidate.c_id, fake_password)

    return {"success": f"Fake account created for {last_candidate.c_id}"}

# Creating a Congratulations views for rendering reference:
def congratulations(request):
    return render(request, "congratulations.html")

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Fetch the Candidate object
            candidate = Candidate.objects.filter(c_id=username).first()
            if not candidate:
                return HttpResponse("Candidate not found.")

            # Validate the time slot
            current_time = now()
            start_time = candidate.time_slot
            end_time = candidate.time_slot + timedelta(minutes=30)
            if start_time.date() == current_time.date() and start_time.time() <= current_time.time() <= end_time.time():
                login(request, user)
                return redirect('/face/capture_faces/')
            else:
                return HttpResponse("You can only log in during your assigned time slot.")
        else:
            return HttpResponse("Invalid username or password.")

    return render(request, "login.html")


@login_required
def test_rules(request):
    if request.method == "POST":
        # Check if the confirmation checkbox was selected
        if request.POST.get("confirm_rules") == "on":
            user1 = Candidate.objects.filter(c_email=request.user.email)
            print(user1)

            questions = filter_questions(user1.first().c_skills)

            # Proceed to the test screen or next step
            request.session["user_name"] = user1.first().c_first_name
            request.session["questions"] = questions

            return render(request, "test.html", {"questions": questions})  # Replace with a redirect to the test screen
        else:
            # Return the rules page with an error message
            return render(request, "rules.html", {"error": "You must confirm the rules to proceed."})

    # Render the rules page for GET requests
    return render(request, "rules.html")


def filter_questions(skills):
    """Filters questions based on skills."""
    questions = []
    skills = ast.literal_eval(skills)
    # Loop over files in the dataset folder
    for file in os.listdir(DATASET_PATH):
        # Check if the file name contains any of the skills (case insensitive)
        if any(skill in file.lower() for skill in skills):
            # Open and read the file if it matches
            with open(os.path.join(DATASET_PATH, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                for question in data:
                    # Preprocess options
                    question["Options"] = [
                        {
                            "display": option,
                            "value": option.split(")")[0]
                        }
                        for option in question["Options"]
                    ]
                questions.extend(data)
    # If no questions matched, return an empty list
    if not questions:
        print("No questions found for the given skills.")
    # Return a random sample
    return random.sample(questions, min(len(questions), 10))

@login_required
def result(request):
    if request.method == "POST":
        user_answers = request.POST
        questions = request.session.get("questions", [])
        correct_count = 0

        # Check user answers
        for question in questions:
            question_id = str(question["id"])
            correct_answer = question["Answer"].split("Explanation")[0].strip().lower()
            correct_answer = correct_answer.split(':')[1].strip().lower()
            user_answer = user_answers.get(question_id, "").strip().lower()

            if user_answer == correct_answer:
                correct_count += 1

        incorrect_count = len(questions) - correct_count
        user_name = request.session.get("user_name", "User")

        return render(request, "result.html", {
            "user_name": user_name,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "total_questions": len(questions),
        })

    return JsonResponse({"error": "Invalid request method"}, status=400)