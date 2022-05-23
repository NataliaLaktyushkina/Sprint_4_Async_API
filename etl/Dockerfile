FROM python:3.9.12-buster
# Базовый образ Python

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY ./requirements.txt .

RUN apt update && apt install -y netcat && which nc

# install dependencies
RUN pip install --no-cache-dir --upgrade pip &&\
 pip install --no-cache-dir -r requirements.txt

#Копируем приложение
COPY ./app /app

# create entrypoint for DB waiting
# Копируем entrypoint.sh
COPY ./entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["sh","/app/entrypoint.sh"]
CMD ["python", "/app/get_data_psql.py"]