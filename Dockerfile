FROM registry.yandex.net/ubuntu:trusty
MAINTAINER borislitv@yandex-team.ru

RUN apt-get update -qq
RUN apt-get install python-pip -y --force-yes
RUN pip install --upgrade pip
RUN pip install setuptools
RUN pip install https://github.com/cocaine/cocaine-framework-python/archive/master.zip

ADD ./unicorn.py /root/unicorn.py
RUN chmod +x /root/unicorn.py

