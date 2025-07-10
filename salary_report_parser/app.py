from salary_report_parser.worker import Worker
from openpyxl import load_workbook
import logging
from logs.logging_module import logger, generate_handler
import os

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
def parse_excel_report(path: str) -> (dict[str, Worker], str):
    path = os.path.abspath(path)

    logger.info(f"Trying to parse: {path}")
    workbook = load_workbook(filename=path, read_only=True, data_only=True)
    sheet_names = workbook.sheetnames
    last_sheet_name = sheet_names[-1]
    sheet = workbook[last_sheet_name]
    workers_dict = {}
    date = sheet.cell(row=3, column=3).value.strftime("%d-%m-%Y")

    for row in sheet.iter_rows(min_row=8, values_only=True):
        if row[0] is not None and row[1] is not None:
            # RE DO
            worker = Worker(
                unique_id=row[1],
                name=row[2],
                machine_type=row[3],
                commentary=row[4],
                work_type=[row[5]] if row[5] else [""],
                mark=[row[6]] if row[6] else [""],
                run_count=[row[7]] if row[7] else [""],
                hours_worked=[round(safe_stoi_convertion(row[8]), 2)] if safe_stoi_convertion(row[8]) else [""],
                hours_worked_sum=row[9] if row[9] else None,
                days_worked=round(safe_stoi_convertion(row[10]), 2) if safe_stoi_convertion(row[10]) else None,
                salary_for_day=[round(safe_stoi_convertion(row[11]), 2)] if safe_stoi_convertion(row[11]) else [""],
                salary_for_month=round(safe_stoi_convertion(row[12]), 2) if safe_stoi_convertion(row[12]) else None,
                repair_days_count=row[13],
                absence_reason=row[14],
            )
            if workers_dict.get(worker.unique_id) is None:
                workers_dict[worker.unique_id] = worker
            else:
                workers_dict[worker.unique_id].merge_workers(worker)
        if row[1] is None:
            logger.info("Special data is skipped")
    logger.info(f"Parsed successfully")
    workbook.close()
    return workers_dict, date

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
