cd /open-korean-text
mvn package -Dmaven.test.skip=true

echo "[INFO] Copy .jar to ouput directory"
rm -rf /output/open-korean-text-2.1.0.jar
cp /open-korean-text/target/open-korean-text-2.3.2-SNAPSHOT.jar \
    /output/open-korean-text-2.1.0.jar
echo "[INFO] Copy .jar to elasticsearch directory"
rm -rf /elasticsearch-plugin/elasticsearch/open-korean-text-2.1.0.jar
cp /open-korean-text/target/open-korean-text-2.3.2-SNAPSHOT.jar \
    /elasticsearch-plugin/elasticsearch/open-korean-text-2.1.0.jar

cd /elasticsearch-plugin/elasticsearch
echo "[INFO] Create elasticsearch Okt plugin"
zip -r elasticsearch-6.5.2-okt-2.1.0-plugin.zip ./*

echo "[INFO] Copy .zip to ouput directory"
rm -rf /output/elasticsearch-6.5.2-okt-2.1.0-plugin.zip
cp elasticsearch-6.5.2-okt-2.1.0-plugin.zip \
    /output/elasticsearch-6.5.2-okt-2.1.0-plugin.zip
