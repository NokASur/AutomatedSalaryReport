from salary_report_parser.worker import Worker
from openpyxl import load_workbook
import logging
from logs.logging_module import logger, generate_handler
import os
import shutil

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

os.makedirs(log_path, exist_ok=True)
logger.addHandler(generate_handler(os.path.join(log_path, "salary_report_parser_all.log"), logging.DEBUG))
logger.addHandler(generate_handler(os.path.join(log_path, "salary_report_parser_info.log"), logging.INFO))
logger.setLevel(logging.DEBUG)
logger.info(f"Logger enabled")


def safe_stoi_convertion(s: str | None) -> int | None:
    if s is None:
        return s
    try:
        return int(s)
    except (ValueError, TypeError) as e:
        logger.error(f"Fail during stoi convertion {e} from string: {s}")
        return None


# A slobby amoeba
def parse_excel_report(path: str) -> (list[Worker], str):
    path = os.path.abspath(path)

    logger.info(f"Trying to parse: {path}")
    workbook = load_workbook(filename=path, read_only=True, data_only=True)
    sheet_names = workbook.sheetnames
    last_sheet_name = sheet_names[-1]
    sheet = workbook[last_sheet_name]

    workers = []
    date = sheet.cell(row=3, column=3).value.strftime("%d-%m-%Y")

    for row in sheet.iter_rows(min_row=8, values_only=True):
        if row[0] is not None:
            # RE DO
            worker = Worker(
                id=safe_stoi_convertion(row[1]) if safe_stoi_convertion(row[1]) else None,
                name=row[2],
                machine_type=row[3],
                commentary=row[4],
                work_type=row[5],
                mark1=row[6],
                mark2=row[7],
                run_count1=row[8],
                run_count2=row[9],
                hours_worked=round(safe_stoi_convertion(row[10]), 2) if safe_stoi_convertion(row[10]) else None,
                hours_worked_sum=round(safe_stoi_convertion(row[11]), 2) if safe_stoi_convertion(row[11]) else None,
                days_worked=round(safe_stoi_convertion(row[12]), 2) if safe_stoi_convertion(row[12]) else None,
                salary_for_day=round(safe_stoi_convertion(row[13]), 2) if safe_stoi_convertion(row[13]) else None,
                salary_for_month=round(safe_stoi_convertion(row[14]), 2) if safe_stoi_convertion(row[14]) else None,
                repair_days_count=row[15],
                absence_reason=row[16],
            )
            workers.append(worker)
    logger.info(f"Parsed successfully")
    workbook.close()
    return workers, date

# test

# workers, date = parse_excel_report("../unparsed_reports/report.xlsx")
# logger.info(f"Printing result messages:\n")
# for worker in workers:
#     logger.info(f"{worker.generate_message(date)}")
# logger.info(f"Finished printing result messages:\n")
#
# logger.info(f"Moving report to the ../parsed_reports/{date}report.xlsx folder:\n")
# shutil.move("../unparsed_reports/report.xlsx", f"../parsed_reports/{date}report.xlsx")
# logger.info(f"Moved successfully\n")
