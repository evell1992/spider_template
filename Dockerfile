FROM opsbears/supervisord:18.04
WORKDIR /root
RUN mkdir -p spider_template && mkdir -p .pip
COPY ./docker_conf/pip.conf .pip/
COPY ./requirements.txt .

RUN echo "Asia/Shanghai" > /etc/timezone \
    && apt-get update \
    && apt-get install -y tzdata \
    && rm -rf /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && apt-get install python3-pip -y \
    && pip3 install -r requirements.txt
ENV TZ 'Asia/Shanghai'