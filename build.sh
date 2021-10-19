docker build -t create-okt -f okt-builder.Dockerfile .

docker run --rm \
 -v $PWD/output:/output \
 create-okt \
 /bin/bash -c "source create-okt.sh"

docker build -t es-okt-tokenizer:6.5.2-okt-2.1.0 \
 -f elasticsearch.Dockerfile .

docker-compose up -d
