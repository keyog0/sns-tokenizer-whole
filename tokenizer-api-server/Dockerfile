FROM openjdk:slim

COPY --from=python:3.7 / /

RUN pip install konlpy==0.6.0
RUN pip install kiwipiepy==0.15.0
RUN pip install requests
RUN pip install fastapi==0.78.0
RUN pip install hypercorn==0.13.2
RUN pip install uvloop==0.16.0

COPY . /app

WORKDIR /app

RUN chmod +x entrypoint.sh

ENTRYPOINT ./entrypoint.sh
CMD hypercorn app:app --bind 0.0.0.0:8080 --worker-class uvloop --keep-alive 10 --workers 4 --access-logfile -