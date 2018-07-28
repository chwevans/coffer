FROM python:3.7.0-alpine3.8

ADD . /

RUN pip install -r requirements.txt

CMD ["python", "coffer/coffer.py"]
