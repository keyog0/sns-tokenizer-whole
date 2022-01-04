sysctl -w vm.max_map_count=262144
docker build -t create-okt -f okt-builder.Dockerfile .

docker run --rm \
 -v $PWD/output:/output \
 create-okt \
 /bin/bash -c "source create-okt.sh"

docker build -t es-okt-tokenizer:7.9.3-okt-2.1.0 \
 -f elasticsearch.Dockerfile .

docker-compose up -d
