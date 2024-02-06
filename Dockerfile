FROM python:3.11
WORKDIR /src
COPY ./requirements_lite.txt /src/
RUN pip install -r requirements_lite.txt
RUN apt update && apt install libgl1-mesa-dev
