FROM python:3.8.5-slim

ENV FLASK_APP pipetest.py
ENV FLASK_ENV development
ENV FLASK_DEBUG false
ENV FLASK_RUN_PORT 8088
ENV FLASK_RUN_HOST 0.0.0.0

ENV PIPETEST_QUERIED_USERS antomer
ENV PIPETEST_QUERYING_INTERVAL 10
ENV PIPETEST_PIEPEDRIVE_COMPANY_NAME antonsawesomecompany

RUN mkdir /db/

COPY pipetest.py /app/
COPY settings.py /app/
COPY requirements.txt /app/

RUN pip3 install -r /app/requirements.txt

WORKDIR /app/
EXPOSE 8088
CMD flask run
