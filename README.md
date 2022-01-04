# sns-tokenizer-word-dict
SNS에 출현하는 단어, 브랜드이름, 신조어 등을 follow하고 토크나이저의 성능을 올리기 위해 단어 사전을 정의 합니다.

# Dependenceis
* Docker
* Docker-Compose

# Elasticsearch plugin version
* [7.9.3](https://github.com/Keunyoung-Jung/sns-tokenizer-whole/releases/tag/7.9.3)
* [6.5.2](https://github.com/Keunyoung-Jung/sns-tokenizer-whole/releases/tag/6.5.2)
* [5.6.5](https://github.com/Keunyoung-Jung/sns-tokenizer-whole/releases/tag/5.6.5)

# Index
* [Install](#install)
    * [전체 빌드 및 설치](#전체-빌드-및-설치)
    * [elasticsearch 이미지만 생성](#elasticsearch-이미지만-생성)
    * Error: max virtual memory areas vm.max_map_count
* [How to use](#how-to-use)
    * [Konlpy 이용](#konlpy-이용)
        * [konlpy 설치](#konlpy-설치)
        * [`.jar`파일 이동하기](#`.jar`파일-이동하기)
        * [python에서 사용하기](#python에서-사용하기)
        * [tweepy에러](#tweepy에러)
    * [Elasticsearch 에 request](#elasticsearch-에-request)
        * [Analyzer](#analyzer)
        * [Tokenizer](#tokenizer)
        * [Tokenizer 컴포넌트 이용하기](#Tokenizer-컴포넌트-이용하기)
            * Normalizer
            * Stemmer
            * Redundant filter
            * Phrase Extractor
* [Reference](#reference)

# Install
`build.sh` 실행시 자동으로 빌드 및 단어사전 업데이트를 수행합니다.    
수행이후 자동으로 `elasticsearch` 컨테이너가 실행됩니다.    
    
빌드를 진행하면 `output` 디렉토리에 `.jar` 파일과 `plugin.zip` 파일이 떨어집니다.    
해당 파일을 이용해서 konlpy 모듈의 okt를 변경하여 사용할수도 있고, elasticsearch 플러그인으로 이용할 수 있습니다.    
해당 파일들은 [Release](https://github.com/Mysterico/sns-tokenizer-word-dict/releases) 페이지에서도 관리되며 직접 다운로드 받을 수 있습니다.    
    
`.jar` 파일과 `plugin.zip`을 빌드 및 설치하는 방법은 두가지 방법으로 사용가능합니다.

## 전체 빌드 및 설치
```shell
sudo ./build.sh
```
* 빌드 파일을 실행하면, 단어사전 업데이트 및 okt 토크나이저를 자동으로 빌드하고, 파일을 생성합니다.    
* 파일 생성및 빌드이후에는 자동으로 elasticsearch로 배포되며, 컨테이너로 올라갑니다.    
* 약 10분정도 소요됩니다. 

## elasticsearch 이미지만 생성
* 경우에 따라, 사전 업데이트가 필요하지 않고 elasticsearch의 image파일만 생성할 수 있습니다.
* 빌드를 따로 진행하지 않기 때문에 `output` 디렉토리에 `plugin.zip` 파일이 없을 수 있습니다.     
* [Release](https://github.com/Mysterico/sns-tokenizer-word-dict/releases) 페이지의 주소를 이용하여 `plugin.zip`파일을 다운로드 받아 `output` 폴더에 넣어 줍니다.
* 또는 직접 주소를 넣어줄 수 있습니다.
    ```dockerfile
    # Line 12
    # 변경전
    ENV plugin_location=file:///usr/share/elasticsearch/elasticsearch-6.5.2-okt-2.1.0-plugin.zip

    #변경후
    ENV plugin_location=https://github.com/Keunyoung-Jung/kubeflow-pipeline-login/raw/master/elasticsearch-6.5.2-okt-2.1.0-plugin.zip
    ```
* default는 output 폴더내 파일의 위치입니다.
* 이 후 빌드를 진행하여 이미지를 생성합니다.
* 약 10초정도 소요됩니다.
```shell
docker build -t es-okt-tokenizer:6.5.2-okt-2.1.0 -f elasticsearch.Dockerfile .
```
### Error: max virtual memory areas vm.max_map_count 
```
elasticsearch-custom-okt | [1]: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
```
* **Linux**    
    해당에러 발생시 `/etc/sysctl.conf`파일에 `vm.max_map_count=262144` 추가 해준다.    
    추가한 후 `sysctl -w vm.max_map_count=262144` 명령어 실행
* **MacOS**    
    `screen ~/Library/Containers/com.docker.docker/Data/vms/0/tty` 명령어 실행    
    `sysctl -w vm.max_map_count=262144` 명령어 실행
* **Windows**    
    `docker-machine ssh` 명령을 통해 ssh 접속
    `sudo sysctl -w vm.max_map_count=262144` 명령어 실행

# How to use
빌드 또는 다운로드 받은 okt tokenizer는 두가지 방법으로 사용가능 합니다.
* [Konlpy 이용](#konlpy-이용)
* [Elasticsearch 에 request](#elasticsearch-에-request)
## Konlpy 이용
* Konlpy를 이용할 때는 okt tokenizer를 사용하는 `open-korean-text-2.1.0.jar` 를 변경해주면 됩니다.
* 아래는 가상환경 사용시의 예제 입니다.
### konlpy 설치
```shell
python3 -m venv venv
pip3 install konlpy
```
### `.jar`파일 이동하기
```shell
cp -i output/open-korean-text-2.1.0.jar venv/lib/python3.8/site-packages/konlpy/java
```
```
cp: 'venv/lib/python3.8/site-packages/konlpy/java/open-korean-text-2.1.0.jar'를 덮어쓸까요? y
```
### python에서 사용하기
```python
from konlpy.tag import Okt

okt = Okt()

okt.pos('이더리움 살려닼ㅋㅋ 안샀음',stem=True,norm=True)
```
```python
vanilla OKT : [('이', 'Determiner'), ('더', 'Noun'), ('리움', 'Noun'), ('살리다', 'Verb'), ('ㅋㅋ', 'KoreanParticle'), ('안', 'VerbPrefix'), ('사다', 'Verb')]

custom OKT : [('이더리움', 'Noun'), ('살리다', 'Verb'), ('ㅋㅋ', 'KoreanParticle'), ('안', 'VerbPrefix'), ('사다', 'Verb')]
```

### tweepy에러
```
AttributeError: module 'tweepy' has no attribute 'StreamListener'
```
만약 tweepy 에러가 뜨면 tweepy 버젼 다운그레이드가 필요합니다.
```
pip install tweepy==3.10.0
```
그래도 에러가 뜨면 java 버젼 업그레이드가 필요합니다.
* version : `openjdk-11`
* [openjdk 다운로드 페이지](https://jdk.java.net/archive/)

## Elasticsearch 에 request
### Analyzer
Elasticsearch에는 기본적으로 analyzer가 있습니다.    
analyzer에는 다음과 같은 기능이 기본적으로 작동 됩니다.    
* stemming - 활용형을 기본형으로 변경합니다. (귀여워 -> 귀엽다)
* normalize - 구어체, SNS말투, 오타등을 평어로 수정합니다. (할려다갘 -> 할려다가)
* redundant - 조사, 띄어쓰기, 마침표 등을 제거합니다.

**Input**
```shell
curl -X POST 'http://localhost:9201/_analyze' -d '{
  "analyzer": "openkoreantext-analyzer",
  "text": "이더리움 살려닼ㅋㅋ 안샀음",
  "explain": true
}'
```
**Output**
```json
{
    "detail": {
        "custom_analyzer": false,
        "analyzer": {
            "name": "org.apache.lucene.analysis.ko.OpenKoreanTextAnalyzer",
            "tokens": [
                {
                    "token": "이더리움",
                    "start_offset": 0,
                    "end_offset": 4,
                    "type": "Noun",
                    "position": 0,
                    "bytes": "[ec 9d b4 eb 8d 94 eb a6 ac ec 9b 80]",
                    "positionLength": 1
                },
                {
                    "token": "살리다",
                    "start_offset": 5,
                    "end_offset": 8,
                    "type": "Verb",
                    "position": 1,
                    "bytes": "[ec 82 b4 eb a6 ac eb 8b a4]",
                    "positionLength": 1
                },
                {
                    "token": "ㅋㅋ",
                    "start_offset": 8,
                    "end_offset": 10,
                    "type": "KoreanParticle",
                    "position": 2,
                    "bytes": "[e3 85 8b e3 85 8b]",
                    "positionLength": 1
                },
                {
                    "token": "안",
                    "start_offset": 11,
                    "end_offset": 12,
                    "type": "VerbPrefix",
                    "position": 3,
                    "bytes": "[ec 95 88]",
                    "positionLength": 1
                },
                {
                    "token": "사다",
                    "start_offset": 12,
                    "end_offset": 14,
                    "type": "Verb",
                    "position": 4,
                    "bytes": "[ec 82 ac eb 8b a4]",
                    "positionLength": 1
                }
            ]
        }
    }
}
```
### Tokenizer
Elasticsearch에서 Tokenizer를 사용하는 방법은 다음과 같습니다.    
**Input**
```shell
curl -X POST 'http://localhost:9201/_analyze' -d '{
  "tokenizer": "openkoreantext-tokenizer",
  "text": "이더리움 살려닼ㅋㅋ 안샀음"
}'
```
**Output**
```json
{
    "tokens": [
        {
            "token": "이더리움",
            "start_offset": 0,
            "end_offset": 4,
            "type": "Noun",
            "position": 0
        },
        {
            "token": " ",
            "start_offset": 4,
            "end_offset": 5,
            "type": "Space",
            "position": 1
        },
        {
            "token": "살려닼",
            "start_offset": 5,
            "end_offset": 8,
            "type": "Noun",
            "position": 2
        },
        {
            "token": "ㅋㅋ",
            "start_offset": 8,
            "end_offset": 10,
            "type": "KoreanParticle",
            "position": 3
        },
        {
            "token": " ",
            "start_offset": 10,
            "end_offset": 11,
            "type": "Space",
            "position": 4
        },
        {
            "token": "안",
            "start_offset": 11,
            "end_offset": 12,
            "type": "VerbPrefix",
            "position": 5
        },
        {
            "token": "샀음",
            "start_offset": 12,
            "end_offset": 14,
            "type": "Verb",
            "position": 6
        }
    ]
}  "explain": true
```
Tokenizer를 사용하는 경우 다양한 컴포넌트와 함께 사용할 수 있습니다.   
      
### Tokenizer 컴포넌트 이용하기
**Normalizer**
* 구어체, SNS말투, 오타등을 평어로 수정합니다. (할려다갘 -> 할려다가)
  ```json
  {
    "tokenizer": "openkoreantext-tokenizer",
    "char_filter": ["openkoreantext-normalizer"],
    "text": "이더리움 살려닼ㅋㅋ 안샀음"
  }
  ```
**Stemmer**
* 활용형을 기본형으로 변경합니다. (귀여워 -> 귀엽다)
  ```json
  {
    "tokenizer": "openkoreantext-tokenizer",
    "filter": ["openkoreantext-stemmer"],
    "text": "이더리움 살려닼ㅋㅋ 안샀음"
  }
  ```
**Redundant filter**
* 조사, 띄어쓰기, 마침표 등을 제거합니다.
  ```json
  {
    "tokenizer": "openkoreantext-tokenizer",
    "filter": ["openkoreantext-redundant-filter"],
    "text": "이더리움 살려닼ㅋㅋ 안샀음"
  }
  ```
**Phrase Extractor**
* 어구를 추출합니다. 단어, 형용사들의 조합을 반환합니다.    
  Input
  ```json
  {
    "tokenizer": "openkoreantext-tokenizer",
    "filter": ["openkoreantext-phrase-extractor"],
    "text": "환상속 모험의 나라"
  }
  ```
  Output
  ```json
  {
      "tokens": [
          {
              "token": "환상속",
              "start_offset": 0,
              "end_offset": 3,
              "type": "Noun",
              "position": 0
          },
          {
              "token": "환상속 모험",
              "start_offset": 0,
              "end_offset": 6,
              "type": "Noun",
              "position": 1
          },
          {
              "token": "환상속 모험의 나라",
              "start_offset": 0,
              "end_offset": 10,
              "type": "Noun",
              "position": 2
          },
          {
              "token": "환상",
              "start_offset": 0,
              "end_offset": 2,
              "type": "Noun",
              "position": 3
          },
          {
              "token": "모험",
              "start_offset": 4,
              "end_offset": 6,
              "type": "Noun",
              "position": 4
          },
          {
              "token": "나라",
              "start_offset": 8,
              "end_offset": 10,
              "type": "Noun",
              "position": 5
          }
      ]
  }

  ```
# Reference
* [https://github.com/open-korean-text/open-korean-text](https://github.com/open-korean-text/open-korean-text)
* [https://github.com/open-korean-text/elasticsearch-analysis-openkoreantext](https://github.com/open-korean-text/elasticsearch-analysis-openkoreantext)
