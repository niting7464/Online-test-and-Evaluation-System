🚀 Mindsprint — Online Test & Evaluation System
Mindsprint is a robust, full-stack examination platform designed to streamline the creation, management, and evaluation of online assessments. Built with Django and Django REST Framework, it features secure JWT authentication, automated grading, and a production-ready deployment pipeline.

✨ Core Features
Secure Authentication: User registration, login, and stateless session management using JWT (SimpleJWT).

Timed Assessments: Categorized MCQ-based tests with real-time attempt tracking.

Automated Evaluation: Instant score calculation with pass/fail logic and detailed performance breakdowns.

Professional Workflows: Automated password reset via Brevo (SMTP) with secure tokenization.

Result Export: Generate detailed question-wise result summaries and PDF exports.

Admin Dashboard: Full control over question banks, test publishing, and user management via Django Admin.

🛠 Tech Stack
Backend: Django, Django REST Framework

Database: PostgreSQL

Auth: JWT (JSON Web Tokens)

Deployment: Render (Web Service & Managed DB)

WSGI Server: Gunicorn

Static Files: WhiteNoise

Monitoring: UptimeRobot

🚀 Quick Start (Development)
1. Environment Setup
Clone the repository and enter the project directory:

Bash

git clone https://github.com/yourusername/mindsprint.git
cd mindsprint
Create a virtual environment and install dependencies:

Bash

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
2. Configuration
Create a .env file at the project root. This project uses python-dotenv to manage secrets:

Code snippet

DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgres://user:password@localhost:5432/mindsprint
EMAIL_HOST_USER=your_brevo_email
EMAIL_HOST_PASSWORD=your_smtp_key
PASSWORD_RESET_DOMAIN=http://127.0.0.1:8000
3. Database & Server
Apply migrations and start the development server:

Bash

python manage.py migrate
python manage.py runserver
Access the application at http://127.0.0.1:8000.

📦 Deployment (Render + Gunicorn)
This project is optimized for deployment on Render.

Build Command:

Bash

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
Start Command:

Bash

gunicorn mindsprint.wsgi:application --bind 0.0.0.0:$PORT
Essential Environment Variables for Production:

DJANGO_DEBUG=False

DJANGO_SECRET_KEY (Generate a fresh one)

DATABASE_URL (Connection string from Render PostgreSQL)

PASSWORD_RESET_DOMAIN (Your live https://www.google.com/search?q=.onrender.com URL)

🧪 Testing Password Reset
Console Logging: To debug emails without sending them, set EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend in your .env.

Network Testing: To test the flow on a mobile device, use your LAN IP (e.g., 192.168.x.x) in ALLOWED_HOSTS and PASSWORD_RESET_DOMAIN.

🤝 Contributing
Fork the Project.

Create your Feature Branch (git checkout -b feature/AmazingFeature).

Commit your Changes (git commit -m 'Add some AmazingFeature').

Push to the Branch (git push origin feature/AmazingFeature).

Open a Pull Request.