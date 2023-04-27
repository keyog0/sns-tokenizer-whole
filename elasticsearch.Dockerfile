FROM elasticsearch:7.17.4

LABEL author="jgy206@gmail.com"

COPY $PWD/output/elasticsearch-7.17.4-okt-2.1.0-plugin.zip \
 /usr/share/elasticsearch/elasticsearch-7.17.4-okt-2.1.0-plugin.zip

ENV cluster.name=docker-cluster
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"
ENV bootstrap.memory_lock=true
ENV discovery.type=single-node
ENV plugin_location=file:///usr/share/elasticsearch/elasticsearch-7.17.4-okt-2.1.0-plugin.zip

EXPOSE 9200/tcp 9300/tcp

USER root

RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install ${plugin_location}

USER elasticsearch

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["elasticsearch"]