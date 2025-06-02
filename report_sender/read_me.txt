Run
"
    pyinstaller --onefile  --hidden-import=logging.handlers --add-data "report_sender/constants.py;constants" --add-data "logs/logging_module.py;logs" --add-data "custom_exceptions/exceptions.py;custom_exceptions" report_sender/app.py
"
 to get .exe file