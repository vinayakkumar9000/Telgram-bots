import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")  # Telegram Bot Token
MAIL_TM_API = "https://api.mail.tm"
GUERRILLA_MAIL_API = "https://api.guerrillamail.com/ajax.php"
DEFAULT_PROVIDER = "mail.tm"
