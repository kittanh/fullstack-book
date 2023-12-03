FROM python:3.8
 
ADD requirements.txt .

RUN pip install -r ./requirements.txt

COPY . /app/front
  
CMD ["python", "/app/front/front_api.py"]