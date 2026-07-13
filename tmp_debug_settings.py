from pathlib import Path
import os
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')
print('ENV DB_ENGINE', repr(os.getenv('DB_ENGINE')))
print('ENV DB_NAME', repr(os.getenv('DB_NAME')))
print('ENV DB_HOST', repr(os.getenv('DB_HOST')))
print('CWD', BASE_DIR)
import siman.settings as s
print('SETTINGS FILE:', s.__file__)
print('DATABASES:', s.DATABASES)
