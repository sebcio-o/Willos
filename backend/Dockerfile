FROM python:3.9

RUN apt update -y && apt upgrade -y
RUN apt-get install -y libgdal-dev g++ --no-install-recommends && \
    apt-get clean -y

RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal
RUN PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --upgrade pip setuptools
RUN pip install --requirement requirements.txt

WORKDIR /backend