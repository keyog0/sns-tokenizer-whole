# import kss
from tokenizer import tokenized_okt_no_hash,tokenized_nori, kiwi
from tokenizer_with_tag import extract_phrases_by_kiwi
from itertools import permutations
import concurrent.futures
import re
import asyncio
import time
import concurrent.futures


def tokenized_sentence(text) :
    text = text[:19999]

    text = text.replace('\u200b', '').replace('\"','').replace('\'','')
    text = re.sub('[^a-zA-Z0-9ㄱ-ㅣ가-힣!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]',' ',text)
    sentences = [sent.text for sent in kiwi.split_into_sents(text)]
    return sentences

    
def tokenized_sentence_no_special(text) :
    if len(text) < 20000 :
        text = text.replace('\u200b', '').replace('\"','').replace('\'','')
        text = re.sub('[^a-zA-Z0-9ㄱ-ㅣ가-힣!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]',' ',text)
        sentences = [sent.text for sent in kiwi.split_into_sents(text) if not re.search(
    '[ㄱ-ㅣ가-힣\s]{200,}', sent.text, re.MULTILINE)]
        return sentences
    else :
        return []

# Regacy combinations     
# def get_combinations(tokens,num=2):
#     tmp = []
#     for token in permutations(tokens,num) :
#         tmp.append(
#             {
#                 'src':token[0],
#                 'dst':token[1]
#              }
#             )
#     return tmp

def get_combinations(tokens,num=2):
    tmp = {
                'src':[],
                'dst':[]
            }
    tmp_dict = {}
    for token in tokens :
        tmp_dict[token]= []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(permutations, tokens, num)
        for src,dst in future.result() :
            tmp_dict[src].append(dst)
    for key,value in tmp_dict.items() :
        if len(value) > 0 :
            tmp['src'].append(key)
            tmp['dst'].append(value)
    return tmp

def get_kiwi_graphframe(text) :
    graphframe = []
    sentences = tokenized_sentence_no_special(text)
    graphframe = {
                'src':[],
                'dst':[]
            }
    for sentence in sentences :
        tokens,adjective,_,_ = extract_phrases_by_kiwi(sentence,adjective=True)
        combnations = get_combinations(list(set(tokens+adjective)))
        graphframe['src'] += combnations['src']
        graphframe['dst'] += combnations['dst']
    return graphframe

def get_graphframe(text):
    graphframe = []
    sentences = tokenized_sentence_no_special(text)
    graphframe = {
                'src':[],
                'dst':[]
            }
    for sentence in sentences :
        tokens = tokenized_okt_no_hash(sentence)
        combnations = get_combinations(list(set(tokens)))
        graphframe['src'] += combnations['src']
        graphframe['dst'] += combnations['dst']
    return graphframe

async def get_sentence_token(text):
    tokens = []
    sentences = tokenized_sentence_no_special(text)
    for sentence in sentences :
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            nori_token,okt_token = await asyncio.gather(
                loop.run_in_executor(pool,tokenized_nori,sentence),
                loop.run_in_executor(pool,tokenized_okt_no_hash,sentence),
            )
        
        token_value = {
            'okt_tokens': okt_token,
            'nori_tokens': [token['token'] for token in nori_token['tokens']]
        }
        tokens.append(token_value)
    return tokens
        