from zauberzeug/nicegui:latest

copy . /app

workdir /app
cmd ["python3", "main.py"]
