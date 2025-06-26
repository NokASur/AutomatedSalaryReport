Run in your project root path:

1) pip install pyinstaller

2) pyinstaller --onefile  --hidden-import=logging.handlers --add-data "config/config.py;config" --add-data "logs/logging_module.py;logs" --add-data "custom_exceptions/exceptions.py;custom_exceptions" report_sender/app.py

 to get .exe file