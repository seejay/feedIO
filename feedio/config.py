import os
from platformdirs import user_data_dir

APP_NAME = "feedIO"
USER_DIR = user_data_dir(APP_NAME)
DB_FILE = os.path.join(USER_DIR, "feedIO.sqlite")
CLASSIFIER_DIR = os.path.join(USER_DIR, "classifier")

def ensure_dirs():
    if not os.path.isdir(USER_DIR):
        os.makedirs(USER_DIR, exist_ok=True)
    if not os.path.isdir(CLASSIFIER_DIR):
        os.makedirs(CLASSIFIER_DIR, exist_ok=True)
