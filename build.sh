docker build -f okt-builder.Dockerfile . -t create-okt

docker run --rm \
 -v $PWD/output:/output \
 create-okt \
 /bin/bash -c "source create-okt.sh"

docker rmi create-okt

# Elasticsearch Create Part
# docker build -t es-okt-tokenizer:7.17.4-okt-2.1.0 \
#  -f elasticsearch.Dockerfile .

# docker-compose up -d