import os
import glob
import time
import shutil
from secrets import UNPROCESSED_FOLDER_PATH, PROCESSED_FOLDER_PATH
from salary_report_parser.app import parse_excel_report
import logging
from logs.logging_module import logger, generate_handler

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

os.makedirs(log_path, exist_ok=True)
logger.addHandler(generate_handler(os.path.join(log_path, "virtual_checker_all.log"), logging.DEBUG))
logger.addHandler(generate_handler(os.path.join(log_path, "virtual_checker_info.log"), logging.INFO))
logger.setLevel(logging.DEBUG)
logger.info(f"Logger enabled")

unprocessed_folder_path = UNPROCESSED_FOLDER_PATH
processed_folder_path = PROCESSED_FOLDER_PATH
os.makedirs(unprocessed_folder_path, exist_ok=True)
os.makedirs(processed_folder_path, exist_ok=True)

while True:
    excel_files = glob.glob(os.path.join(unprocessed_folder_path, "*.xlsx"))
    excel_files.append("test")
    if len(excel_files) != 0:
        logger.info(f"{len(excel_files)} excel files found.")
        for excel_file_path in excel_files:
            logger.info(f"Parsing {excel_file_path}")
            workers = parse_excel_report(excel_file_path)
            for worker in workers:
                logger.info(f"Generated message: {worker.generate_message()}")
            shutil.move(excel_file_path, os.path.join(processed_folder_path, excel_file_path))
            logger.info(f"Moved {excel_file_path} to {os.path.join(processed_folder_path, excel_file_path)}")
    else:
        logger.info("No excel files found")

    time.sleep(60)
