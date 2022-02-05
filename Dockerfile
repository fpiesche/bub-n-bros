FROM python:3.10.2-alpine
COPY . /bubnbros
RUN pip install -r /bubnbros/requirements.txt

ENV BUBNBROS_PORT=8000
WORKDIR /bubnbros
CMD python bb_tornado.py --port=${BUBNBROS_PORT} --logging=WARNING --log_file_prefix=/bubnbros/bubnbros-${BUBNBROS_PORT}.log
