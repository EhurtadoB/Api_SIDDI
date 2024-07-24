FROM python:3.12

RUN apt-get update && apt-get install -y libgl1-mesa-glx

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
