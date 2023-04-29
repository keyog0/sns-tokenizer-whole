from fastapi import FastAPI, HTTPException, APIRouter
from tokenizer import tokenized_okt, tokenized_nori, reload_words
from tokenizer_with_tag import tokenized_nori_with_tag, tokenized_okt_with_tag, tokenized_kiwi_with_tag, extract_phrases_by_kiwi,tokenized_kiwi_generate_space
from spliter import get_graphframe, tokenized_sentence, tokenized_sentence_no_special, get_sentence_token, get_kiwi_graphframe
import re
import unicodedata
import time, os
from dto import *
import asyncio
import concurrent.futures
from typing import Optional, List, Union

app = FastAPI(title=f'SNS tokenzier API')
router = APIRouter()
tokenize_router = APIRouter() 
okt_router = APIRouter()
kiwi_router = APIRouter()

def error(msg,status_code=400):
    raise HTTPException(status_code=status_code, detail=msg)

@app.get('/')
async def health_check():
    return 'healthy'

@router.post('/sentence',
           response_model=ResponseSentence)
async def sentence(data:RequestModel,
                   special:str = "true"):
    text = unicodedata.normalize('NFC',data.text)
    sentences = tokenized_sentence(text) if special == "true" else tokenized_sentence_no_special(text)
    response = ResponseSentence(
        sentence=sentences
    )
    return response

@router.post('/sentence/tokenize',
           response_model=ResponseSentenceTokenize)
async def sentence_token(data:RequestModel):
    text = unicodedata.normalize('NFC',data.text)
    sentence_token = await get_sentence_token(text)
    response = ResponseSentenceTokenize(
        sentence_token=sentence_token
    )
    return response


@kiwi_router.post('',
           response_model=Union[ResponseKiwiWithTagModel,List[ResponseKiwiWithTagModel]])
async def tokenize_kiwi(data:RequestModelKiwi,normalize: bool = True,naive: bool =False):
    if type(data.text) != list :
        text = unicodedata.normalize('NFC',data.text)
        loop = asyncio.get_event_loop()
    
        with concurrent.futures.ThreadPoolExecutor() as pool:
            kiwi_tokens = await asyncio.gather(
                loop.run_in_executor(pool,tokenized_kiwi_with_tag,text,normalize,naive)
            )
        
        response = ResponseKiwiWithTagModel(
            kiwi=[
                KiwiWithTagModel(
                    token=kiwi["token"],
                    tag=kiwi["tag"],
                    pureTag=kiwi["pure_tag"],
                    start=kiwi["start"],
                    length=kiwi["length"]
                )
                for kiwi in kiwi_tokens[0]
            ]
        )
        return response
    else :
        text = [unicodedata.normalize('NFC',t) for t in data.text]
    
        loop = asyncio.get_event_loop()
    
        with concurrent.futures.ThreadPoolExecutor() as pool:
            kiwi_tokens = await asyncio.gather(
                loop.run_in_executor(pool,tokenized_kiwi_with_tag,text,normalize,naive)
            )
        
        response = []
        for kiwi_token in kiwi_tokens[0] :
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
    
@kiwi_router.post('/extract',
           response_model=ResponseKiwiExtractPhrases)
async def tokenize_kiwi_extract_phrases(data:RequestModel):
    text = unicodedata.normalize('NFC',data.text)
    phrases = extract_phrases_by_kiwi(text)
    response = ResponseKiwiExtractPhrases(
        kiwi_phrases=phrases
    )
    return response

@kiwi_router.post('/clickhouse', response_model=ResponseClickhouseTokenizeKiwi)
async def clickhouse_tokenize(data:RequestModel,adjective:bool = True):
    text = unicodedata.normalize('NFC',data.text)
    loop = asyncio.get_event_loop()
    
    with concurrent.futures.ThreadPoolExecutor() as pool:
        kiwi_tokens,kiwi_graphframe = await asyncio.gather(
            loop.run_in_executor(pool,extract_phrases_by_kiwi,text,True),
            loop.run_in_executor(pool,get_kiwi_graphframe,text,adjective)
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

@kiwi_router.post('/space', response_model=ResponseModelKiwiSpace)
async def tokenize_generate_space(data:RequestModelKiwi):
    loop = asyncio.get_event_loop()
    
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool,tokenized_kiwi_generate_space,data.text)
    return ResponseModelKiwiSpace(text=result)

@okt_router.post('',
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

@okt_router.post('/clickhouse', response_model=ResponseClickhouseTokenizeOkt)
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

if os.environ["kiwi"] == "true" :
    tokenize_router.include_router(kiwi_router, tags=['kiwi'], prefix='/kiwi')

if os.environ["okt"] == "true"  :
    tokenize_router.include_router(okt_router, tags=['okt'], prefix='/okt')
router.include_router(tokenize_router, prefix='/tokenize')
app.include_router(router, prefix='/tokenizer')

if __name__ == '__main__':
    app.run(port=8080)
    