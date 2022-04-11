FROM python:3.7-alpine

EXPOSE 5000
COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

CMD ["python3","-u","app.py"]