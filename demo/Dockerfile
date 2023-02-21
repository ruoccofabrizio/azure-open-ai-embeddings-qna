FROM python:3.9.10-slim-buster
RUN apt-get update && apt-get install python-tk python3-tk tk-dev -y
WORKDIR /usr/local/src/myscripts
COPY . /usr/local/src/myscripts
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["streamlit", "run", "demo.py", "--server.port", "80"]