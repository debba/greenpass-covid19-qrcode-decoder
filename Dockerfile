# syntax=docker/dockerfile:1

FROM python:3.9

WORKDIR /app
RUN apt update && apt install -y libzbar-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
ENV PRODUCTION=${PRODUCTION}
ENV GA_ID=${GA_ID}
ENV SHARETHIS_SCRIPT_SRC=${SHARETHIS_SCRIPT_SRC}
ENV APP_URL=${APP_URL}
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "-w", "2", "--access-logfile", "-", "app:app"]