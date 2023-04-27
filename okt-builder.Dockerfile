FROM openjdk:11

LABEL author="jgy206@gmail.com"

COPY create-okt.sh /
COPY update_dict.py /
COPY upload_plugin.py /

# ENV AWS_ACCESS_KEY_ID="your_key_id"
# ENV AWS_SECRET_ACCESS_KEY="your_secret_key"
# ENV AWS_S3_BUCKET="your_bucket"

RUN apt update
RUN apt install -y maven
RUN apt install -y zip
RUN apt install -y python3-pip
RUN pip3 install pymongo
RUN pip3 install tqdm
RUN pip3 install boto3
RUN pip3 install requests
RUN pip3 install kiwipiepy==0.14.0

RUN mkdir elasticsearch-plugin
RUN mkdir elasticsearch-plugin/elasticsearch
RUN mkdir /kiwi-dict
RUN git clone https://github.com/Keunyoung-Jung/open-korean-text.git

WORKDIR /open-korean-text
RUN mvn package
RUN rm -rf /open-korean-text/target
RUN rm -rf /open-korean-text/src/main/resources/org/openkoreantext/processor/util
COPY Dictionary /open-korean-text/src/main/resources/org/openkoreantext/processor/util
COPY kiwi-dict /kiwi-dict

WORKDIR /elasticsearch-plugin/elasticsearch
RUN wget -O elasticsearch-7.17.4-okt-2.1.0-plugin.zip https://github.com/Keunyoung-Jung/sns-tokenizer-whole/releases/download/7.17.4/elasticsearch-7.17.4-okt-2.1.0-plugin.zip
RUN unzip elasticsearch-7.17.4-okt-2.1.0-plugin.zip
RUN rm -rf elasticsearch-7.17.4-okt-2.1.0-plugin.zip

WORKDIR /