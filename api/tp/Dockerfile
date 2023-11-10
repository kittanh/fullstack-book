FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ADD requirements.txt .

RUN pip install -r requirements.txt

COPY ./app /app/app