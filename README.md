# HR_REPLACEMENT
This is a web-based AI-HR system that helps in managing the candidates interview scheduling efficiently.
The project includes functionalities for user registration, profile management, and email sending( user login credentia) and MCQ based online test.

#Before running the project, make sure you have the following installed:

(requirement.txt file)
Install python and create an env

Steps to set up and run this project:

1. Clone the repository
cd HR_REPLACEMENT/hr_replacement

2. Install Dependencies
pip install -r requirements.txt

3. Change the dataset path and other paths accordingly 

4. Set Up Redis (For Windows Users)
Download Redis from this GitHub page or use a package manager like Chocolatey to install Redis on Windows.
[Resource: https://naveenrenji.medium.com/install-redis-on-windows-b80880dc2a36]
run command redis: redis-server --port 6380

5. Set Up the Database:
 Make Migrations (python manage.py makemigrations)
 Apply Migrations (python manage.py migrate)

6. create an account at mailjet
reource: https://app.mailjet.com/signup?lang=en_US
change creds in settings.py as well

7. Start the development server using this command:
   (daphne hr_replacement.asgi:application) in the same directory

8. Ready to go
