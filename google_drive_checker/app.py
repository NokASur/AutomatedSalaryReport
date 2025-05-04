import time
import datetime
import logging
from logging.handlers import RotatingFileHandler
import os.path
from pip._internal.network.auth import Credentials
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from constants import (CHECKER_START_TIME, CHECKER_END_TIME,
                       CHECKER_FREQUENCY_SECONDS, API_SCOPES,
                       TOKEN_FILE, CREDENTIALS_FILE)

all_logs_handler = RotatingFileHandler(
    filename="google_drive_checker.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding='utf-8',
    mode='a',

)
all_logs_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
all_logs_handler.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.addHandler(all_logs_handler,)


def authenticate_drive() -> Credentials:
    """
    Uses token to gain access to Google Drive API if it exists
    Generates a new one using credentials.json if not
    """

    logger.info("Starting authentication with Google Drive API")
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, API_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def find_new_report():
    pass


def check_drive() -> bool:
    """
    Checks if the drive is available and contains new files to consume.
    Returns True if both are available, False otherwise.
    """

    logger.info("Authenticating google Drive...")
    drive_data: Credentials = authenticate_drive()

    if drive_data:
        file = find_new_report()
        if file:
            return True
        else:
            logger.error(f"No new report found. Recheck in {CHECKER_FREQUENCY_SECONDS} second(s)")
    else:
        logger.error("Drive not available")
    return False


def app() -> None:
    logger.info("Google drive checker service is running.")
    last_execution_time: datetime = None
    while True:
        now = datetime.datetime.now()
        # if CHECKER_START_TIME <= now.time() <= CHECKER_END_TIME: # Commented for debug
        if True:

            if last_execution_time is None or now - last_execution_time >= datetime.timedelta(CHECKER_FREQUENCY_SECONDS):
                last_execution_time = now
                result = check_drive()

        time.sleep(0.1)


if __name__ == "__main__":
    app()
