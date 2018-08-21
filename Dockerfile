FROM python:3.7.0-alpine3.8

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . /


CMD ["python", "coffer/coffer.py"]
