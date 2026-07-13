# PowerShell helper to setup local Python virtual environment and run Django

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
