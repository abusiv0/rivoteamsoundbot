@echo off
:TFT
echo (%time%) Bot started.
python run.py
echo (%time%) PELIGRO: Concha BOT se cerró, reiniciando...
ping 1.1.1.1 -n 1 -w 3000 >nul
goto TFT