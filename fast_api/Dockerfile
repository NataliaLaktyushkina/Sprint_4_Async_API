FROM python:3.9.12-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./requirements.txt .

RUN apt update && apt install -y netcat && which nc

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY ./src /app

# create entrypoint for elasticsearch waiting
COPY ./entrypoint.sh   .
RUN chmod +x entrypoint.sh


ENTRYPOINT ["sh","/app/entrypoint.sh"]
