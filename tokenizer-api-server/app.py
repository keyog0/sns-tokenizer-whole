from fastapi import FastAPI, HTTPException
from tokenizer import tokenized_okt, tokenized_nori, reload_words
from tokenizer_with_tag import tokenized_nori_with_tag, tokenized_okt_with_tag, tokenized_kiwi_with_tag, extract_phrases_by_kiwi,tokenized_kiwi_generate_space
from spliter import get_graphframe, tokenized_sentence, tokenized_sentence_no_special, get_sentence_token, get_kiwi_graphframe
import re
import unicodedata
import time
from dto import *
import asyncio
import concurrent.futures
from typing import Optional, List, Union

app = FastAPI(title=f'SNS tokenzier API')

def error(msg,status_code=400):
    raise HTTPException(status_code=status_code, detail=msg)

@app.get('/')
async def health_check():
    return 'healthy'

@app.get('/sns_tokenizer/reload_words')
async def reload_words_api():
    reload_words()
    return 'reloaded'
    
@app.post('/sns_tokenizer/tokenize',
           response_model=ResponseTokenize)
async def tokenize(data:RequestModel):
    text = unicodedata.normalize('NFC',data.text)
    loop = asyncio.get_event_loop()
    
    with concurrent.futures.ThreadPoolExecutor() as pool:
        okt_tokens,nori_tokens,graphframe = await asyncio.gather(
            loop.run_in_executor(pool,tokenized_okt,text),
            loop.run_in_executor(pool,tokenized_nori,text),
            loop.run_in_executor(pool,get_graphframe,text)
        )

    response = ResponseTokenize(
        nori=NoriModel(
            tokens=[token['token'] for token in nori_tokens['tokens']]
        ),
        okt=OktModel(
            hashtag=okt_tokens[1],
            tokens=okt_tokens[0]
        ),
        graphframe=GraphFrameModel(
            src=graphframe['src'],
            dst=graphframe['dst']
        )
    )
    return response

@app.post('/sns_tokenizer/tokenize/nori',
           response_model=ResponseNoriWithTagModel)
async def tokenize_nori(data:RequestModel):
    text = unicodedata.normalize('NFC',data.text)
    
    nori_tokens = await tokenized_nori_with_tag(text)

    response = ResponseNoriWithTagModel(
        nori=[
            NoriWithTagModel(
                token=nori['token'],
                posType=nori['posType'],
                tag=nori['tag']
            )
            for nori in nori_tokens
            ]
    )
    return response

@app.post('/sns_tokenizer/tokenize/okt',
           response_model=ResponseOktWithTagModel)
async def tokenize_okt(data:RequestModel,normalize: bool = True):
    text = unicodedata.normalize('NFC',data.text)
    
    okt_tokens = await tokenized_okt_with_tag(text,normalize)

    response = ResponseOktWithTagModel(
        okt=[
            OktWithTagModel(
                token=okt['token'],
                tag=okt['tag']
            )
            for okt in okt_tokens
            ]
    )
    return response

@app.post('/sns_tokenizer/tokenize/kiwi',
           response_model=Union[ResponseKiwiWithTagModel,List[ResponseKiwiWithTagModel]])
async def tokenize_kiwi(data:RequestModelKiwi,normalize: bool = True,naive: bool =False):
    if type(data.text) != list :
        text = unicodedata.normalize('NFC',data.text)
    
        kiwi_tokens = await tokenized_kiwi_with_tag(text,normalize,naive)
        
        response = ResponseKiwiWithTagModel(
            kiwi=[
                KiwiWithTagModel(
                    token=kiwi["token"],
                    tag=kiwi["tag"],
                    pureTag=kiwi["pure_tag"],
                    start=kiwi["start"],
                    length=kiwi["length"]
                )
                for kiwi in kiwi_tokens
            ]
        )
        return response
    else :
        text = [unicodedata.normalize('NFC',t) for t in data.text]
    
        kiwi_tokens = await tokenized_kiwi_with_tag(text,normalize,naive)
        
        response = []
        for kiwi_token in kiwi_tokens :
            response.append(ResponseKiwiWithTagModel(
                kiwi=[
                    KiwiWithTagModel(
                        token=kiwi["token"],
                        tag=kiwi["tag"],
                        pureTag=kiwi["pure_tag"],
                        start=kiwi["start"],
                        length=kiwi["length"]
                    )
                    for kiwi in kiwi_token
                    ]
                )
            )
        return response
    
@app.post('/sns_tokenizer/tokenize/kiwi/extract',
           response_model=ResponseKiwiExtractPhrases)
async def tokenize_kiwi_extract_phrases(data:RequestModel):
    text = unicodedata.normalize('NFC',data.text)
    phrases = extract_phrases_by_kiwi(text)
    response = ResponseKiwiExtractPhrases(
        kiwi_phrases=phrases
    )
    return response

@app.post('/sns_tokenizer/sentence',
           response_model=ResponseSentence)
async def sentence(data:RequestModel,
                   special:str = "true"):
    text = unicodedata.normalize('NFC',data.text)
    sentences = tokenized_sentence(text) if special == "true" else tokenized_sentence_no_special(text)
    response = ResponseSentence(
        sentence=sentences
    )
    return response

@app.post('/sns_tokenizer/sentence/tokenize',
           response_model=ResponseSentenceTokenize)
async def sentence_token(data:RequestModel):
    text = unicodedata.normalize('NFC',data.text)
    sentence_token = await get_sentence_token(text)
    response = ResponseSentenceTokenize(
        sentence_token=sentence_token
    )
    return response

@app.post('/sns_tokenizer/tokenize/clickhouse', response_model=ResponseClickhouseTokenize)
async def clickhouse_tokenize(data:RequestModel):
    text = unicodedata.normalize('NFC',data.text)
    loop = asyncio.get_event_loop()
    
    with concurrent.futures.ThreadPoolExecutor() as pool:
        okt_tokens,kiwi_tokens,graphframe,kiwi_graphframe = await asyncio.gather(
            loop.run_in_executor(pool,tokenized_okt,text),
            loop.run_in_executor(pool,extract_phrases_by_kiwi,text,True),
            loop.run_in_executor(pool,get_graphframe,text),
            loop.run_in_executor(pool,get_kiwi_graphframe,text)
        )

    response = ResponseClickhouseTokenize(
        kiwi=KiwiModel(
            noun=kiwi_tokens[0],
            adjective=kiwi_tokens[1],
            wordCount=kiwi_tokens[2],
            nnpCount=kiwi_tokens[3]
        ),
        okt=OktModel(
            hashtag=okt_tokens[1],
            tokens=list(set(okt_tokens[0]))
        ),
        graphframe=GraphFrameModel(
            src=graphframe['src'],
            dst=graphframe['dst']
        ),
        kiwiGraphframe=KiwiGraphFrameModel(
            src=kiwi_graphframe['src'],
            dst=kiwi_graphframe['dst']
        )
    )
    return response

@app.post('/sns_tokenizer/tokenize/clickhouse/okt', response_model=ResponseClickhouseTokenizeOkt)
async def clickhouse_tokenize(data:RequestModel):
    text = unicodedata.normalize('NFC',data.text)
    loop = asyncio.get_event_loop()
    
    with concurrent.futures.ThreadPoolExecutor() as pool:
        okt_tokens,graphframe = await asyncio.gather(
            loop.run_in_executor(pool,tokenized_okt,text),
            loop.run_in_executor(pool,get_graphframe,text)
        )

    response = ResponseClickhouseTokenizeOkt(
        okt=OktModel(
            hashtag=okt_tokens[1],
            tokens=list(set(okt_tokens[0]))
        ),
        graphframe=GraphFrameModel(
            src=graphframe['src'],
            dst=graphframe['dst']
        )
    )
    return response

@app.post('/sns_tokenizer/tokenize/clickhouse/kiwi', response_model=ResponseClickhouseTokenizeKiwi)
async def clickhouse_tokenize(data:RequestModel):
    text = unicodedata.normalize('NFC',data.text)
    loop = asyncio.get_event_loop()
    
    with concurrent.futures.ThreadPoolExecutor() as pool:
        kiwi_tokens,kiwi_graphframe = await asyncio.gather(
            loop.run_in_executor(pool,extract_phrases_by_kiwi,text,True),
            loop.run_in_executor(pool,get_kiwi_graphframe,text)
        )

    response = ResponseClickhouseTokenizeKiwi(
        kiwi=KiwiModel(
            noun=kiwi_tokens[0],
            adjective=kiwi_tokens[1],
            wordCount=kiwi_tokens[2],
            nnpCount=kiwi_tokens[3]
        ),
        kiwiGraphframe=KiwiGraphFrameModel(
            src=kiwi_graphframe['src'],
            dst=kiwi_graphframe['dst']
        )
    )
    return response

@app.post('/sns_tokenizer/tokenize/kiwi/space', response_model=ResponseModelKiwiSpace)
async def tokenize_generate_space(data:RequestModelKiwi):
    loop = asyncio.get_event_loop()
    
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool,tokenized_kiwi_generate_space,data.text)
    return ResponseModelKiwiSpace(text=result)
if __name__ == '__main__':
    app.run(port=8080)
    