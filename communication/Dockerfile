FROM python:3.8-alpine

RUN mkdir /app
WORKDIR /app

ADD requirement.txt /app/requirement.txt
RUN pip install -r /app/requirement.txt

ADD . /app

# EXPOSE 5003

CMD ["python", "/app/communication.py"]