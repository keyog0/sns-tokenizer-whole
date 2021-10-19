FROM openjdk:11

LABEL author="jgy206@gmail.com"

COPY create-okt.sh /

RUN apt update 
RUN apt upgrade
RUN apt install -y maven
RUN apt install -y zip
RUN apt install -y python3-pip
RUN pip3 install pymongo
RUN pip3 install tqdm

RUN mkdir elasticsearch-plugin
RUN mkdir elasticsearch-plugin/elasticsearch
RUN git clone https://github.com/open-korean-text/open-korean-text.git

WORKDIR /open-korean-text
RUN mvn package
RUN rm -rf /open-korean-text/target
RUN rm -rf /open-korean-text/src/main/resources/org/openkoreantext/processor/util
COPY Dictionary /open-korean-text/src/main/resources/org/openkoreantext/processor/util

WORKDIR /elasticsearch-plugin/elasticsearch
RUN wget https://github.com/Keunyoung-Jung/sns-tokenizer-whole/releases/download/6.5.2/elasticsearch-6.5.2-okt-2.1.0-plugin.zip
RUN unzip elasticsearch-6.5.2-okt-2.1.0-plugin.zip
RUN rm -rf elasticsearch-6.5.2-okt-2.1.0-plugin.zip

WORKDIR /
