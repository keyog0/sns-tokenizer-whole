FROM keyog/python:3.8-dood

COPY . /tmp
WORKDIR /tmp
RUN chmod +x /tmp/build.sh

CMD [ "/bin/bash","./build.sh" ]