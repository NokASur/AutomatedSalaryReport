import json
import time
import datetime
import os.path
from pip._internal.network.auth import Credentials
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, Resource

from logs.logging_module import logger
from constants import (CHECKER_START_TIME, CHECKER_END_TIME,
                       CHECKER_FREQUENCY_SECONDS, API_SCOPES,
                       TOKEN_FILE, CREDENTIALS_FILE)


def authenticate_drive() -> Credentials:
    """
    Uses token to gain access to Google Drive API if it exists
    Generates a new one using credentials.json if not
    Returns a Credentials object you can build a service with
    """

    logger.info("Starting authentication with Google Drive API")
    creds: Credentials | None = None

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
    return creds


def download_new_report(service: Resource) -> str:
    """
    :param service: drive service that we download the report from
    :return: string with the name of the report, or "" if no report was found
    """

    logger.info("Trying to identificate and download a new report")
    try:
        value = service.files().list().execute()
        filtered = (list(filter(lambda d: d['title'] == 'SalaryReports', value['items'])))
        filtered_data = json.dumps(filtered, sort_keys=True, indent=4)
        data = json.dumps(value, sort_keys=True, indent=4, ensure_ascii=False)
        print(data)
    except Exception as e:
        logger.error("Problem with downloading new files: " + e.__str__())
    finally:
        service.close()
    return ""


def check_drive() -> bool:
    """
    Checks if the drive is available and contains new files to consume.
    Returns True if both are available, False otherwise.
    """

    logger.info("Authenticating google Drive...")

    drive_credentials_data: Credentials = authenticate_drive()

    if drive_credentials_data:
        drive_service: Resource = build('drive', 'v2', credentials=drive_credentials_data)
        if drive_service:
            report_name = download_new_report(drive_service)
            if report_name:
                return True
            else:
                logger.error(f"No new report found. Recheck in {CHECKER_FREQUENCY_SECONDS} second(s)")
        else:
            logger.error("Drive not available")
    else:
        logger.error("Problem creating google drive credentials")
    return False


def app() -> None:
    logger.info("Google drive checker service is running.")
    last_execution_time: datetime = None
    while True:
        now = datetime.datetime.now()
        # if CHECKER_START_TIME <= now.time() <= CHECKER_END_TIME: # Commented for debug
        if True:

            if last_execution_time is None or now - last_execution_time >= datetime.timedelta(
                    CHECKER_FREQUENCY_SECONDS):
                last_execution_time = now
                result = check_drive()

        time.sleep(0.1)


if __name__ == "__main__":
    app()
