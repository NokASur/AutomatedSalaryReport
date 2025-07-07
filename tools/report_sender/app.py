import paramiko
from paramiko import SSHClient, SFTPClient
from scp import SCPClient
import os
import sys
import re
from datetime import datetime
from config.config import HOST, PORT, USERNAME, PASSWORD, REMOTE_PATH_BASE, DEBUG
import logging
from logs.logging_module import logger, generate_handler
from custom_exceptions.exceptions import SSHException, SFTPException, OSException, SCPException

log_path = ""
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

if DEBUG:
    log_path = os.path.join(os.path.dirname(base_path), "logs")
else:
    log_path = os.path.join(base_path, "logs")

os.makedirs(log_path, exist_ok=True)
logger.addHandler(generate_handler(os.path.join(log_path, "report_sender_all.log"), logging.DEBUG))
logger.addHandler(generate_handler(os.path.join(log_path, "report_sender_error.log"), logging.ERROR))
logger.setLevel(logging.DEBUG)
logger.info(f"Logger enabled")


def initialize_connection() -> SSHClient:
    """
    Initializes the SSH-connection with the virtual server
    Returns SSHClient object
    """
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, PORT, USERNAME, PASSWORD)
        logger.info("Connection established successfully")
        return ssh

    except Exception as e:
        raise SSHException(e)


def send_file_scp(ssh: SSHClient, local_path: str, remote_path: str) -> None:
    logger.info(f"Попытка отправить файл: {local_path} → {remote_path}")
    try:
        if not os.path.exists(local_path):
            logger.error(f"Локальный файл не найден: {local_path}")
            raise SCPException(f"Файл не существует: {local_path}")

        remote_dir = os.path.dirname(remote_path)
        remote_filename = os.path.basename(remote_path)

        cmd = f"mkdir -p {remote_dir}"
        stdin, stdout, stderr = ssh.exec_command(cmd)

        with SCPClient(ssh.get_transport()) as scp:
            print(local_path)
            print("test")
            print(remote_path)

            scp.put(local_path, remote_path)

        logger.info(f"Файл успешно отправлен на сервер: {remote_path}")
    except Exception as e:
        logger.error(f"Ошибка при отправке файла: {str(e)}")
        raise SCPException(e)


def report_scanner() -> list[str]:
    try:
        logger.info(f"Scanning for excel files")
        xlsx = r".*\.xlsx$"
        excel_files = []
        for file in os.listdir(base_path):
            if re.match(xlsx, file):
                excel_files.append(os.path.join(base_path, file))
        logger.info(f"Excel files found: {excel_files}")
        return excel_files
    except Exception as e:
        raise OSException(e)


excel_file_names = report_scanner()

if len(excel_file_names) == 1:
    ssh: SSHClient | None = None
    try:
        ssh = initialize_connection()
        for file in excel_file_names:
            if os.path.exists(file):
                print(file)
                send_file_scp(
                    ssh,
                    file,
                    REMOTE_PATH_BASE + "report"+datetime.now().strftime("%Y%m%d_%H%M%S")+".xlsx",
                )
        logger.info(f"Excel file sent successfully")
    except SSHException as e:
        logger.error(f"{e}")
    except SFTPException as e:
        logger.error(f"{e}")
    except OSException as e:
        logger.error(f"{e}")
    except Exception as e:
        logger.error(f"Unknown Error: {e}")
    finally:
        if ssh is not None:
            ssh.close()

elif len(excel_file_names) == 0:
    logger.error("No excel files found")

else:
    logger.error(f"Multiple excel files found: {excel_file_names}")
