FROM arm32v7/python:3.9.12-buster

COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "ads1115.py"]
