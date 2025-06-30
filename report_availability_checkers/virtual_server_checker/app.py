import os
import glob
import shutil
import redis
from datetime import datetime
from config.config import UNPROCESSED_FOLDER_PATH, PROCESSED_FOLDER_PATH, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT
from salary_report_parser.app import parse_excel_report
from salary_report_parser.worker import Worker
import logging
from logs.logging_module import logger, generate_handler

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=0,
    decode_responses=True
)

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

os.makedirs(log_path, exist_ok=True)
logger.addHandler(generate_handler(os.path.join(log_path, "virtual_checker_all.log"), logging.DEBUG))
logger.addHandler(generate_handler(os.path.join(log_path, "virtual_checker_error.log"), logging.ERROR))
logger.setLevel(logging.DEBUG)
logger.info(f"Logger enabled")

unprocessed_folder_path = UNPROCESSED_FOLDER_PATH
processed_folder_path = PROCESSED_FOLDER_PATH
logger.info(f"Unprocessed folder path: {unprocessed_folder_path}")

os.makedirs(unprocessed_folder_path, exist_ok=True)
os.makedirs(processed_folder_path, exist_ok=True)

excel_files = glob.glob(os.path.join(unprocessed_folder_path, "*.xlsx"))
if len(excel_files) != 0:
    logger.info(f"{len(excel_files)} excel files found.")
    for excel_file_path in excel_files:
        logger.info(f"Parsing {excel_file_path}")
        workers: list[Worker]
        date: str
        workers, date = parse_excel_report(excel_file_path)
        for worker in workers:
            message = worker.generate_message(date)
            logger.info(f"Generated message: {message}")
            if not r.hexists(worker.unique_id, "State"):
                r.hset(worker.unique_id, mapping={"State": "Registered", "Message": message, "Chat_id": ""})
            else:
                r.hset(worker.unique_id, "Message", message)

        remote_full_path = os.path.join(processed_folder_path,
                                        f"{date}report{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        shutil.move(excel_file_path, remote_full_path)
        logger.info(f"Moved {excel_file_path} to {remote_full_path}")
else:
    logger.info(f"No excel files found at {unprocessed_folder_path}")
