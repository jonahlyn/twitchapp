FROM centos:7
MAINTAINER Jonahlyn Gilstrap "jonahlyn@unm.edu"

RUN yum -y update && \
    yum -y install https://centos7.iuscommunity.org/ius-release.rpm && \
    yum install -y python36u python36u-libs python36u-devel python36u-pip git

COPY requirements.txt /build/
WORKDIR /build/
RUN pip3.6 install -r requirements.txt

WORKDIR /app

#CMD ["python3.6", "./app.py"]