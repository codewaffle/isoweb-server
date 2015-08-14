FROM phusion/baseimage:0.9.17

RUN apt-get update && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip

ADD requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt

ADD . /app
RUN python3 setup.py build_ext -b ..
EXPOSE 10000

CMD ["python3", "rserve.py"]
