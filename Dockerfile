FROM python:3.7
EXPOSE 8000
COPY . /bubnbros
CMD python /bubnbros/bb_tornado.py
