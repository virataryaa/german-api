@echo off
setlocal
cd /d "%~dp0"
echo Pulling German coffee tax and trade from Destatis ...
python Automator\ingest_coffee_tax.py
if errorlevel 1 exit /b 1
python Automator\ingest_trade.py
if errorlevel 1 exit /b 1
git pull --rebase --autostash
git add Database\*.csv
git diff --cached --quiet || git commit -m "Data: German coffee tax + trade update"
git push
