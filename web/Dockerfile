FROM python:3.10-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN set -ex \
  && apk --no-cache add postgresql-dev

# для postgres
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers

WORKDIR /app

COPY ./app/requirements.txt requirements.txt
RUN #pip install --no-cache-dir -r requirements.txt
RUN pip install  -r requirements.txt

COPY ./app /app
RUN mkdir -p /static

COPY ./entrypoint.sh .
ENTRYPOINT ["sh","/app/entrypoint.sh"]

