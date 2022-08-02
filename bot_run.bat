@echo off

call %~dp0venv\Scripts\activate

cd %~dp0

set TOKEN=5484593859:AAHu8GsdsvogFXw7-b6GaQOqIr-hy_uGqug

python TSA_bot.py

pause