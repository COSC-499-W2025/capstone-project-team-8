FROM python:3.14-slim

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py migrate

CMD ["python", "manage.py", "runserver"]
