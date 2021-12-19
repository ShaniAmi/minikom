FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt test_application.py ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["pytest"]