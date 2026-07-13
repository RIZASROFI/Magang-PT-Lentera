# Deploy ke PythonAnywhere

## 1. Persiapan environment file
Buat file `.env` di root proyek PythonAnywhere dan isi dengan:

```dotenv
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=rizasrofi.pythonanywhere.com
DB_ENGINE=django.db.backends.mysql
DB_NAME=rizasrofi$db_magang
DB_USER=rizasrofi
DB_PASSWORD=your_mysql_password
DB_HOST=rizasrofi.mysql.pythonanywhere-services.com
DB_PORT=3306
```

Ganti:
- `your-secret-key` dengan secret key yang aman
- `your_mysql_password` dengan password database PythonAnywhere

## 2. Setup virtualenv di PythonAnywhere
Di Bash console PythonAnywhere:

```bash
cd ~/Magang-PT-Lentera
python3.13 -m venv ~/venv/siman
source ~/venv/siman/bin/activate
pip install -r requirements.txt
```

## 3. Konfigurasi Web App
Di tab `Web` PythonAnywhere:
- Source code: `/home/rizasrofi/Magang-PT-Lentera`
- Working directory: `/home/rizasrofi/Magang-PT-Lentera`
- Virtualenv: `/home/rizasrofi/venv/siman`

Pastikan WSGI file memuat:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siman.settings')
```

## 4. Migrasi dan collectstatic
Jalankan di Bash console:

```bash
cd ~/Magang-PT-Lentera
source ~/venv/siman/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

## 5. Catatan tambahan
- Jika jalankan lokal, `.env` bisa berisi SQLite:
  - `DB_ENGINE=django.db.backends.sqlite3`
  - `DB_NAME=db.sqlite3`
- Jangan commit file `.env` ke Git.
