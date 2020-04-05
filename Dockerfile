# To build different architectures, simply run:
# docker build --build-arg BASE_ARCH=arm32v7 -t florianpiesche/bubnbros:arm32v7-latest
ARG BASE_ARCH=amd64
ARG PORT=8000

FROM ${BASE_ARCH}/python:3.7-alpine
EXPOSE ${PORT}
COPY . /bubnbros
RUN pip install -r /bubnbros/requirements.txt
WORKDIR /bubnbros
ENTRYPOINT ["python", "bb_tornado.py",
            "--port=${PORT}", "--logging=WARNING", "--log_file_prefix=/bubnbros/bubnbros-${PORT}.log"]
