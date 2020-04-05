FROM python:3.7-alpine
EXPOSE 8000
COPY . /bubnbros
RUN pip install -r /bubnbros/requirements.txt
WORKDIR /bubnbros
ENTRYPOINT ["python", "bb_tornado.py"]
