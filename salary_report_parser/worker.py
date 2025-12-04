import random
import logging
import os
from logs.logging_module import logger, generate_handler

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

os.makedirs(log_path, exist_ok=True)
logger.addHandler(generate_handler(os.path.join(log_path, "worker_all.log"), logging.DEBUG))
logger.addHandler(generate_handler(os.path.join(log_path, "worker_info.log"), logging.INFO))
logger.setLevel(logging.DEBUG)
logger.info(f"Logger enabled")


class Job:
    def __init__(self, work_type, mark, tonns, runs, hectars, hours, salary_for_day):
        self.work_type = work_type
        self.mark = mark
        self.tonns = tonns
        self.runs = runs
        self.hectars = hectars
        self.hours = hours
        self.salary_for_day = salary_for_day

    def generate_job_message(self) -> str:
        message = ""
        if self.work_type is None:
            return "Работа не указана."
        message += f"Название работы: {self.work_type}.\n"

        job_metric_used = False

        if self.tonns is not None and not job_metric_used:
            message += f"Выполнено тонн: {self.tonns}.\n"
            job_metric_used = True
        if self.runs is not None and not job_metric_used:
            message += f"Выполнено проходов: {self.runs}.\n"
            job_metric_used = True
        if self.hectars is not None and not job_metric_used:
            message += f"Охвачено гектаров: {self.hectars}.\n"
            job_metric_used = True
        if self.hours is not None and not job_metric_used:
            message += f"Часов работы: {self.hours}.\n"
            job_metric_used = True

        if not job_metric_used:
            message += "К сожалению, подробности работы не были указаны.\n"
        else:
            message += f"Цена за единицу работы: {self.mark}.\n"
        if self.salary_for_day is not None:
            message += f"Выручка за день за данную работу: {self.salary_for_day}.\n"

        logger.info(
            f"tonns: {self.salary_for_day}, hectars:{self.hectars}, runs:{self.runs}, salary_for_day:{self.salary_for_day}")

        return message


class Worker:
    def __init__(
            self,
            unique_id: str | None = None,
            name: str | None = None,
            machine_type: str | None = None,
            # commentary: str | None = None,
            hours_worked_sum: int | None = None,
            days_worked: int | None = None,
            salary_for_month: int | None = None,
            repair_days_count: int | None = None,
            absence_reason: str | None = None,
            jobs: list[Job] | None = None,

    ):
        self.unique_id = unique_id
        self.name = name
        self.machine_type = machine_type
        # self.commentary = commentary
        self.hours_worked_sum = hours_worked_sum
        self.days_worked = days_worked
        self.salary_for_month = salary_for_month
        self.repair_days_count = repair_days_count
        self.absence_reason = absence_reason
        self.jobs = jobs

    def generate_message(self, date: str) -> str:
        greetings = [
            f"Привет, {self.name}! Вот отчёт за {date}.\n",
            f"Здравствуйте, {self.name}! Статистика за {date}.\n",
            f"Добрый день, {self.name}! Ваша сводка за {date}.\n",
            f"{self.name}, приветствую! Информация за {date}.\n",
            f"Отчёт для {self.name} за {date}.\n"
        ]

        work_type_phrases = [
            f"Сегодня вы работали над следующими задачами:\n",
            f"В этот день вы занимались:\n",
            f"Ваши задачи на сегодня:\n",
            f"Сегодняшняя работа включала:\n",
            f"Вы работали над:\n"
        ]

        monthly_stats = [
            f"За месяц наработано: {self.hours_worked_sum} ч. ({self.salary_for_month} руб.)\n",
            f"Месячная статистика: {self.hours_worked_sum} часов, доход: {self.salary_for_month} руб.\n",
            f"Общее время за месяц: {self.hours_worked_sum} ч. Заработок: {self.salary_for_month} руб.\n",
            f"Наработка за месяц: {self.hours_worked_sum} часов → {self.salary_for_month} руб.\n",
            f"Итоги месяца: {self.hours_worked_sum} ч. = {self.salary_for_month} руб.\n"
        ]

        encouragements = [
            "Отличный результат!",
            "Так держать!",
            "Продолжайте в том же духе!",
            "Прекрасная работа!",
            "Вы молодец!",
            "Ваши усилия впечатляют!",
            "Это продуктивный день!",
            "Вот это эффективность!",
            "Замечательные показатели!",
            "Вы на верном пути!"
        ]

        message = random.choice(greetings)
        if self.absence_reason:
            message += f"Сегодня вы не работали по причине: {self.absence_reason}.\n"
            if self.salary_for_month is not None and self.hours_worked_sum is not None:
                message += random.choice(monthly_stats)
            return message

        work_flag = False

        if len(self.jobs) > 0:
            message += random.choice(work_type_phrases)
            for job in self.jobs:
                message += job.generate_job_message()
            work_flag = True

        if self.salary_for_month is not None and self.hours_worked_sum is not None:
            message += random.choice(monthly_stats)
            work_flag = True
        print("Зарплата за месяц и наработано часов: ", self.salary_for_month, self.hours_worked_sum)
        if work_flag:
            message += random.choice(encouragements)

        return message

    def add_jobs_from(self, worker):
        self.jobs.extend(worker.jobs)
