import os
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))

# Load .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(basedir, '.env'))
except ImportError:
    pass


def _get_secret_key():
    """Get SECRET_KEY from env, .env, or generate+persist one."""
    key = os.environ.get('SECRET_KEY')
    if key:
        return key
    key_file = os.path.join(basedir, 'instance', 'secret_key.txt')
    try:
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        if os.path.exists(key_file):
            with open(key_file, 'r') as f:
                key = f.read().strip()
            if key:
                return key
        key = secrets.token_hex(32)
        with open(key_file, 'w') as f:
            f.write(key)
        return key
    except OSError:
        return secrets.token_hex(32)


class Config:
    SECRET_KEY = _get_secret_key()
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'muhasebe.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    BACKUP_DIR = os.path.join(basedir, 'instance', 'backups')
    LAST_BACKUP_FILE = os.path.join(basedir, 'instance', '.last_backup')
    BACKUP_REMINDER_DAYS = 7
