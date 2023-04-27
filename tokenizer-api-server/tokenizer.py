from konlpy.tag import Okt
from stopwords import StopWords
import requests
from requests.auth import HTTPBasicAuth
import os
import time
from kiwipiepy import Kiwi

kiwi = None
okt = None

if os.environ["kiwi"] == "true" :
    kiwi = Kiwi()
    print('kiwi user dict load')
    kiwi.load_user_dictionary('kiwi-user.dict')
    kiwi.prepare()
    print('kiwi user dict complete')

if os.environ["okt"] == "true"  :
    okt = Okt()

    warmup_text = '레몬아이스티 디자인이 이쁘더라구요, 흰곰 그려진게 너무 귀여웠어요 공을 던졌어요 의료기기전자민원창구 알잘딱깔센하게 주세요 맛있다'
    kiwi.tokenize(warmup_text)
    okt.pos(warmup_text)

stop_words_cls = StopWords()

stopwords= stop_words_cls.stopwords
backadj= stop_words_cls.backadj
backwords= stop_words_cls.backwords
unitwords= stop_words_cls.unitwords
pre_build_unit= stop_words_cls.pre_build_unit
ko_num = stop_words_cls.ko_num
not_ko_num = stop_words_cls.not_ko_num

def reload_words():
    stopwords = stop_words_cls.reload_stopwords()

def tokenized_okt(text):
    token_list = []
    tokens = okt.pos(text.replace('#',' '),norm=True,stem=True)
    hash_tag = [token.upper() for token,tag in okt.pos(text.replace('#',' #')) if tag == 'Hashtag']
    postword = ''
    posttag = ''
    postnumber = ''
    posttagtmp = ''
    for token,tag in tokens :
        if len(token) == len([char for char in list(token) if char in ko_num]) and token not in not_ko_num:
            tag = 'KoNum'
        if (posttagtmp == 'KoNum' or posttagtmp == 'Number' ) and (tag == 'KoNum' or tag == 'Number') :
            token = postnumber+token
        if tag == 'Alpha' :
            token = token.upper()
            if token == 'NEWS' :
                continue
            elif len(token) < 2 :
                continue 
        if tag == 'Number' :
            posttagtmp = tag
            postnumber = token
            for pre_unit in pre_build_unit :
                if pre_unit in token :
                    token_list.append(token.replace(',',''))
                    postnumber=''
                    posttagtmp = ''
                    continue
        if token in unitwords and (posttagtmp == 'Number' or posttagtmp == 'KoNum') :
            if postnumber != '' :
                token = postnumber+token
                token_list.append(token)
                postnumber=''
                posttagtmp = ''
                continue
        if tag == 'Suffix' and len(token_list) > 0 :
            token_list[-1] = token_list[-1]+token
            postword = token_list[-1]
            posttag = 'Noun'
            postnumber=''
            posttagtmp = ''
            continue
            
        if tag in ['Noun','Adjective','Alpha'] and token not in stopwords :
            if token in backadj and posttag == 'Noun' :
                token = postword+' '+token
                token_list.append(token)
                postword = ''
                posttag = ''
                postnumber=''
                posttagtmp = ''
                continue
            if token in backwords and posttag == 'Noun' :
                token = postword+token
            if (len(token) < 10 and tag != 'Alpha') or (len(token) < 20 and tag == 'Alpha') :
                token_list.append(token)
                postword = token
                posttag = tag
                postnumber=''
                posttagtmp = ''
        elif tag not in ['Noun','Adjective','Alpha','Number','Alpha'] and token not in stopwords :
            if tag == 'KoNum' :
                posttagtmp = 'KoNum'
                postnumber = token

    return [token_list,hash_tag]

def tokenized_okt_no_hash(text):
    token_list = []
    tokens = okt.pos(text.replace('#',' '),norm=True,stem=True)
    postword = ''
    posttag = ''
    postnumber = ''
    posttagtmp = ''
    for token,tag in tokens :
        if len(token) == len([char for char in list(token) if char in ko_num]) and token not in not_ko_num:
            tag = 'KoNum'
        if (posttagtmp == 'KoNum' or posttagtmp == 'Number' ) and (tag == 'KoNum' or tag == 'Number') :
            token = postnumber+token
        if tag == 'Alpha' :
            token = token.upper()
            if token == 'NEWS' :
                continue
            elif len(token) < 2 :
                continue 
        if tag == 'Number' :
            posttagtmp = tag
            postnumber = token
            for pre_unit in pre_build_unit :
                if pre_unit in token :
                    clean_number = token.replace(',','').replace(pre_unit,'')
                    if len(clean_number) > 5 and pre_unit in ["년","월","일","시","분","초"] :
                        continue
                    else :
                        token_list.append(token.replace(',',''))
                        postnumber=''
                        posttagtmp = ''
                        continue
        if token in unitwords and (posttagtmp == 'Number' or posttagtmp == 'KoNum') :
            if postnumber != '' :
                token = postnumber+token
                token_list.append(token)
                postnumber=''
                posttagtmp = ''
                continue
                
        if tag == 'Suffix' and len(token_list) > 0 :
            token_list[-1] = token_list[-1]+token
            postword = token_list[-1]
            posttag = 'Noun'
            postnumber=''
            posttagtmp = ''
            continue
                
        if tag in ['Noun','Adjective','Alpha'] and token not in stopwords :
                if token in backadj and posttag == 'Noun' :
                    token = postword+' '+token
                    token_list.append(token)
                    postword = ''
                    posttag = ''
                    postnumber=''
                    posttagtmp = ''
                    continue
                if token in backwords and posttag == 'Noun' :
                    token = postword+token
                if (len(token) < 10 and tag != 'Alpha') or (len(token) < 20 and tag == 'Alpha') :
                    token_list.append(token)
                    postword = token
                    posttag = tag
                    postnumber=''
                    posttagtmp = ''
        elif tag not in ['Noun','Adjective','Alpha','Number','Alpha'] and token not in stopwords :
            if tag == 'KoNum' :
                posttagtmp = 'KoNum'
                postnumber = token
                    
                    
    return token_list
    
def tokenized_nori(text) :
    data = {
        "tokenizer": "nori_korean_tokenizer",
        "filter": [
            "lowercase",
            {
                "type": "nori_part_of_speech",
                "stoptags": [
                    "E",
                    "VV",
                    "VCP",
                    "VCN",
                    "VX",
                    "IC",
                    "J",
                    "MAG",
                    "MAJ",
                    "MM",
                    "SP",
                    "SSC",
                    "SSO",
                    "SC",
                    "SE",
                    "SY",
                    "XPN",
                    "XSA",
                    "XSN",
                    "XSV",
                    "UNA",
                    "NA",
                    "VSV",
                    "SN"
                ]
            },
            {
                "type": "length",
                "min": "2"
            }
        ],
        "text": text
    }
    response = requests.get(os.environ['ES_URL']+'/word_analyze/_analyze',json=data, auth=HTTPBasicAuth('elastic', os.environ['ES_PWD'])).json()
    return response