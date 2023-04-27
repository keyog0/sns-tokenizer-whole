from tokenizer import okt,kiwi
from stopwords import StopWords
import concurrent.futures
import requests
from requests.auth import HTTPBasicAuth
import os
import time
import asyncio
import functools

stop_words_cls = StopWords()

kiwi_stopwords = stop_words_cls.kiwi_stopwords
kiwi_adj_stopwords = stop_words_cls.kiwi_adj_stopwords
stopwords= stop_words_cls.stopwords
backadj= stop_words_cls.backadj
backwords= stop_words_cls.backwords
unitwords= stop_words_cls.unitwords
pre_build_unit= stop_words_cls.pre_build_unit
ko_num = stop_words_cls.ko_num
not_ko_num = stop_words_cls.not_ko_num

def reload_words():
    stopwords = stop_words_cls.reload_stopwords()

def tokenized_okt_with_tag(text,normalize):
    token_list = []
    tokens = okt.pos(text.replace('#',' '),norm=normalize,stem=normalize)
    hash_tag = [{'token':token.upper(),'tag':'Hashtag'} for token,tag in okt.pos(text.replace('#',' #')) if tag == 'Hashtag']
    postword = ''
    posttag = ''
    postnumber = ''
    posttagtmp = ''
    for token,tag in tokens :
        token = token.upper()
        if len(token) == len([char for char in list(token) if char in ko_num]) and token not in not_ko_num:
            tag = 'KoNum'
        if (posttagtmp == 'KoNum' or posttagtmp == 'Number' ) and (tag == 'KoNum' or tag == 'Number'):
            token = postnumber+token
        if tag == 'Alpha' :
            if len(token) < 2 and token not in unitwords+pre_build_unit :
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
                        token_list.append({'token':token.replace(',',''),
                                        'tag':f"{clean_number}/{posttagtmp}+{pre_unit}/Unit"})
                        postnumber=''
                        posttagtmp = ''
                        continue
        if token in unitwords+pre_build_unit and (posttagtmp == 'Number' or posttagtmp == 'KoNum') :
            if postnumber != '' :
                new_token = postnumber+token
                token_list.append({'token':new_token,'tag':f'{postnumber}/{posttagtmp}+{token}/Unit'})
                token=new_token
                postnumber=''
                posttagtmp = ''
                continue
        if tag == 'Suffix' and len(token_list) > 0 :
            token_list[-1] = {
                "token":token_list[-1]["token"]+token,
                "tag": f"{token_list[-1]['token']}/Noun+{token}/{tag}"
            }
            postword = token_list[-1]['token']
            posttag = f"{token_list[-1]['token']}/Noun+{token}/{tag}"
            postnumber=''
            posttagtmp = ''
            continue
            
        if tag in ['Noun','Adjective','Alpha'] and token not in stopwords :
            if token in backadj and posttag == 'Noun' :
                new_token = postword+' '+token
                token_list.append({'token':new_token,'tag':f'{postword}/{posttag}+{token}/{tag}'})
                token=new_token
                postword = ''
                posttag = ''
                postnumber=''
                posttagtmp = ''
                continue
            if token in backwords and posttag == 'Noun' :
                new_token = postword+token
                token_list.append({'token':new_token,'tag':f'{postword}/{posttag}+{token}/{tag}'})
                token=new_token
                continue
            elif (len(token) < 10 and tag != 'Alpha') or (len(token) < 20 and tag == 'Alpha') :
                token_list.append({'token':token,'tag':tag})
                postword = token
                posttag = tag
                postnumber=''
                posttagtmp = ''
                continue
        elif tag not in ['Noun','Adjective','Alpha','Number'] and token not in stopwords :
            if tag == 'KoNum' :
                posttagtmp = 'KoNum'
                postnumber = token
            else :
                token_list.append({'token':token,'tag':tag})
    tmp = token_list + hash_tag
    return tmp
    
def tokenized_nori_with_tag(text) :
    data = {
        "tokenizer": {
                "type": "nori_tokenizer",
                "decompound_mode": "none",
                "discard_punctuation": "false"
            },
            "text": text,
            "explain": True
    }
    response = requests.get(os.environ['ES_URL']+'/word_analyze/_analyze',json=data,
                            auth=HTTPBasicAuth('elastic', os.environ['ES_PWD'])).json()
    
    token_with_tag = []
    for token in response['detail']['tokenizer']['tokens'] :
        if token['leftPOS'] != 'SP(Space)' :
            tmp_dict = {}
            tmp_dict['token'] = token['token']
            tmp_dict['posType'] = token['posType']
            if token['posType'] == 'COMPOUND' :
                tmp_dict['tag'] = token['morphemes']
            else :
                tmp_dict['tag'] = token['leftPOS']
            token_with_tag.append(tmp_dict)
        
    return token_with_tag

def func_kiwi_rule_base(token_result,naive) :
    nountags = [
        "NNG","NNP","NP","NNB"
    ]
    stoptags = [
        "EP","EF","EC","ETN","ETM","NP","SO"
    ]
    head_tags = [
        "SN","XPN","NR"
    ]
    suffix_tags = [
        "NNB","XSN","XSA","XSV"
    ]
    recovery_tags = [
        "VV","VCP","VCN","VX","VA"
    ]
    result = [
        {
            "token":res.form.upper(),
            "tag":res.tag,
            "start": res.start,
            "length": res.len
        }
        for res in token_result
    ]
    if naive :
        return result
    ret_result = []
    token = {}
    post_token = None
    
    for res in result:
        if "-I" in res["tag"] or "-R" in res["tag"] :
            res["tag"] = res["tag"].split("-")[0]
        if res["tag"] not in stoptags:
            if res["tag"] in head_tags and post_token == None:
                post_token = res
            else :
                if res["tag"] in recovery_tags :
                    token = {
                        "token": res["token"]+"다",
                        "tag": res["tag"],
                        "pure_tag": res["tag"],
                        "start": res["start"],
                        "length": res["length"]
                    }
                    post_token = None
                    ret_result.append(token)
                    continue
                elif post_token != None :
                    if post_token["tag"] == "XPN" and res["tag"] in nountags :
                        token = {
                            "token": post_token["token"] + res["token"],
                            "tag": f'{post_token["token"]}/{post_token["tag"]}+{res["token"]}/{res["tag"]}',
                            "pure_tag": f'{post_token["tag"]}+{res["tag"]}',
                            "start": post_token["start"],
                            "length": post_token["length"]+res["length"]
                        }
                        post_token = None
                        ret_result.append(token)
                        continue
                    elif post_token["tag"] in ["SN","NR"] :
                        if res["tag"] in ["SN","NR"] :
                            post_token = {
                                "token": post_token["token"] + res["token"],
                                "tag": res["tag"],
                                "pure_tag": res["tag"],
                                "start": post_token["start"],
                                "length": post_token["length"]+res["length"]
                            }
                            continue
                        elif res["token"] in pre_build_unit+unitwords:
                            token = {
                                "token": post_token["token"] + res["token"],
                                "tag": f'{post_token["token"]}/{post_token["tag"]}+{res["token"]}/{res["tag"]}',
                                "pure_tag": f'{post_token["tag"]}+{res["tag"]}',
                                "start": post_token["start"],
                                "length": post_token["length"]+res["length"]
                            }
                            post_token = None
                            ret_result.append(token)
                            continue
                        else :
                            token = {
                                "token": res["token"],
                                "tag": res["tag"],
                                "pure_tag": res["tag"],
                                "start": res["start"],
                                "length": res["length"]
                            }
                            post_token = None
                            ret_result.append(token)
                            continue
                    else :
                        token = {
                            "token": res["token"],
                            "tag": res["tag"],
                            "pure_tag": res["tag"],
                            "start": res["start"],
                            "length": res["length"]
                        }
                        post_token = None
                        ret_result.append(token)
                        continue
                elif res["tag"] in suffix_tags :
                    if len(ret_result) > 0 and ret_result[-1]["tag"] in nountags+["XR"] :
                        if res["tag"] in ["XSA","XSV"] :
                            res["token"] = res["token"]+"다"
                        token = {
                            "token": ret_result[-1]["token"]+res["token"],
                            "tag": f'{ret_result[-1]["token"]}/{ret_result[-1]["tag"]}+{res["token"]}/{res["tag"]}',
                            "pure_tag": f'{ret_result[-1]["tag"]}+{res["tag"]}',
                            "start": ret_result[-1]["start"],
                            "length": res["length"]+ret_result[-1]["length"]
                        }
                        post_token = None
                        ret_result[-1] = token
                        continue
                    else : 
                        token = {
                            "token": res["token"],
                            "tag": res["tag"],
                            "pure_tag": res["tag"],
                            "start": res["start"],
                            "length": res["length"]
                        }
                        post_token = None
                        ret_result.append(token)
                        continue
                else :
                    token = {
                        "token": res["token"],
                        "tag": res["tag"],
                        "pure_tag": res["tag"],
                        "start": res["start"],
                        "length": res["length"]
                    }
                    post_token = None
                    ret_result.append(token)
                    continue
    return ret_result

def tokenized_kiwi_with_tag(text,normalize,naive) :
    result = kiwi.tokenize(text,normalize_coda=normalize)

    if type(text) != list :
        ret_result = func_kiwi_rule_base(result,naive)
        return ret_result
    else :
        ret_result =[
                func_kiwi_rule_base(token_result,naive)
                for token_result in list(result)
            ]
        return ret_result

def tokenized_kiwi_generate_space(text) :
    result = kiwi.space(text)

    if type(text) != list :
        return result
    else :
        ret_result = [res for res in result]

        return ret_result
    
def extract_phrases_by_kiwi(sentence: str, adjective: bool = False):
    available_pos = ["NNG","NNP","XPN","SL","NNG+XSN","NNP+XSN","NNG+NNB","NR+SL","NR+NNB","NR+XSN","XPN+NNG","XPN+NNP"]
    nnp_pos = ["NNP","NNP+XSN","XPN+NNP"]
    josa_pos = ('JKS', 'JKC','JKG','JKO','JKB','JKV','JKQ','JX','SP','SS','SSO','SSC','SF','SE','SW')
    adjective_pos = ["VA","VX","XSA"]

    def join_noun_tokens(noun_phrase_tokens, josa: bool = False):
        first_token = noun_phrase_tokens[0]
        result = first_token["token"]
        index = first_token["start"] + first_token["length"]
        for noun_token in noun_phrase_tokens[1:]:
            c = noun_token["token"]
            if index == noun_token["start"]:
                result += c
            else:
                if noun_token["tag"] == "SL" :
                    result += f" {c}"
                else :
                    result += c
            index = noun_token["start"] + noun_token["length"]
        return result

    def join_and_insert_phrase(noun_phrase_tokens,noun_phrases,josa=True):
        if len(noun_phrase_tokens) > 0 :
            noun_phrase_tokens = list(reversed(noun_phrase_tokens))
            joined_noun_phrase = join_noun_tokens(noun_phrase_tokens.copy(),josa)
            if joined_noun_phrase != None and len(joined_noun_phrase) > 1:
                noun_phrases.append(joined_noun_phrase)
        return joined_noun_phrase
    # Given iterables, Kiwi enables Multi-Threading
    tokens = tokenized_kiwi_with_tag(sentence.replace("  ","\n").replace("\n",". "),normalize=True,naive=False)

    noun_phrases = list()
    just_noun_phrases = list()
    noun_phrase_tokens = list()
    adjective_phrases = list()
    word_count_dict = {}
    nnp_count_dict = {}
    reversed_tokens = list(reversed(tokens))
    josa_flag = False
    used_index = list()
    # ----조사가 있는 경우 조사 기반 단어를 우선시 추출 -------
    for i, token in enumerate(reversed_tokens):
        pure_tag = token["pure_tag"]
        if pure_tag in josa_pos or pure_tag.startswith("V") :  # JKS : 주격 조사, JKQ : 목적격 조사
            josa_flag = True
            if len(noun_phrase_tokens) > 0 :
                word_count = len(noun_phrase_tokens)
                nnp_count = len([token for token in noun_phrase_tokens if token["tag"] in nnp_pos])
                joined_noun_phrase = join_and_insert_phrase(noun_phrase_tokens,noun_phrases,josa=True)
                if joined_noun_phrase != None :
                    used_index += [ tk['start'] for tk in noun_phrase_tokens]
                noun_phrase_tokens = []
                word_count_dict[joined_noun_phrase] = word_count
                nnp_count_dict[joined_noun_phrase] = nnp_count
            continue
        if josa_flag :
            if pure_tag in available_pos and token["token"] not in kiwi_stopwords:
                if len(noun_phrase_tokens) < 5 :
                    noun_phrase_tokens.append(token)
            else :
                if len(noun_phrase_tokens) > 0 :
                    word_count = len(noun_phrase_tokens)
                    nnp_count = len([token for token in noun_phrase_tokens if token["tag"] in nnp_pos])
                    joined_noun_phrase = join_and_insert_phrase(noun_phrase_tokens,noun_phrases,josa=True)
                    if joined_noun_phrase != None :
                        used_index += [ tk['start'] for tk in noun_phrase_tokens]
                    noun_phrase_tokens = []
                    word_count_dict[joined_noun_phrase] = word_count
                    nnp_count_dict[joined_noun_phrase] = nnp_count
                    josa_flag = False
        else :
            if len(noun_phrase_tokens) > 0 :
                word_count = len(noun_phrase_tokens)
                nnp_count = len([token for token in noun_phrase_tokens if token["tag"] in nnp_pos])
                joined_noun_phrase = join_and_insert_phrase(noun_phrase_tokens,noun_phrases,josa=True)
                if joined_noun_phrase != None :
                    used_index += [ tk['start'] for tk in noun_phrase_tokens]
                noun_phrase_tokens = []
                word_count_dict[joined_noun_phrase] = word_count
                nnp_count_dict[joined_noun_phrase] = nnp_count
                josa_flag = False
            else :
                josa_flag = False
                continue
    
    if len(noun_phrase_tokens) > 0 :
        word_count = len(noun_phrase_tokens)
        nnp_count = len([token for token in noun_phrase_tokens if token["tag"] in nnp_pos])
        joined_noun_phrase = join_and_insert_phrase(noun_phrase_tokens,noun_phrases)
        if joined_noun_phrase != None :
            used_index += [ tk['start'] for tk in noun_phrase_tokens]
        noun_phrase_tokens = []
        word_count_dict[joined_noun_phrase] = word_count
        nnp_count_dict[joined_noun_phrase] = nnp_count
    
    
    # ----조사가 없는 경우에 추출되지 않은 명사를 등록하기 위해 한번 더 순회 -------
    for i, token in enumerate(reversed_tokens):
        pure_tag = token["pure_tag"]
        if len(token["token"]) > 1 \
            and (pure_tag in adjective_pos or "+XSA" in pure_tag or "+XSV" in pure_tag) \
                and token["token"] not in kiwi_adj_stopwords:
            adjective_phrases.append(token["token"])
        
        if token["tag"] == "W_HASHTAG" :
            process_token = token["token"].replace("#","").replace("_","")
            noun_phrases.append(process_token)
            word_count_dict[process_token] = len(process_token.split(" "))
            nnp_count_dict[process_token] = 1

        if pure_tag in available_pos and token['start'] not in used_index and token["token"] not in kiwi_stopwords:
            if len(noun_phrase_tokens) > 0 :
                if token["start"]+token["length"] == noun_phrase_tokens[-1]["start"] :
                    noun_phrase_tokens.append(token)
                else :
                    word_count = len(noun_phrase_tokens)
                    nnp_count = len([token for token in noun_phrase_tokens if token["tag"] in nnp_pos])
                    joined_noun_phrase = join_and_insert_phrase(noun_phrase_tokens,noun_phrases)
                    noun_phrase_tokens = []
                    word_count_dict[joined_noun_phrase] = word_count
                    nnp_count_dict[joined_noun_phrase] = nnp_count
                    noun_phrase_tokens.append(token)
            else :
                noun_phrase_tokens.append(token)
            # noun_phrase_tokens.append(token)
        else :
            if len(noun_phrase_tokens) > 0 :
                word_count = len(noun_phrase_tokens)
                nnp_count = len([token for token in noun_phrase_tokens if token["tag"] in nnp_pos])
                joined_noun_phrase = join_and_insert_phrase(noun_phrase_tokens,noun_phrases)
                noun_phrase_tokens = []
                word_count_dict[joined_noun_phrase] = word_count
                nnp_count_dict[joined_noun_phrase] = nnp_count

    if len(noun_phrase_tokens) > 0 :
        word_count = len(noun_phrase_tokens)
        nnp_count = len([token for token in noun_phrase_tokens if token["tag"] in nnp_pos])
        joined_noun_phrase = join_and_insert_phrase(noun_phrase_tokens,noun_phrases)
        noun_phrase_tokens = []
        word_count_dict[joined_noun_phrase] = word_count
        nnp_count_dict[joined_noun_phrase] = nnp_count
    
    noun_phrases = list(reversed(functools.reduce(lambda acc, cur: acc if cur in acc else acc+[cur], noun_phrases, [])))
    adjective_phrases = list(reversed(functools.reduce(lambda acc, cur: acc if cur in acc else acc+[cur], adjective_phrases, [])))
    
    # 확률 기반으로 인해 명사로 잡힌 문제 토큰 제거
    noun_phrases_process = []
    tmp = tokenized_kiwi_with_tag(noun_phrases,normalize=True,naive=False)
    for idx,token in enumerate(tmp):
        if len(token) == 1 :
            if token[0]['pure_tag'] in available_pos :
                noun_phrases_process.append(noun_phrases[idx])
            else :
                pass
        else :
            noun_phrases_process.append(noun_phrases[idx])
    
    word_count_list = [ word_count_dict[noun] for noun in noun_phrases_process]
    nnp_count_list = [ nnp_count_dict[noun] for noun in noun_phrases_process]

    if adjective :
        return [noun_phrases_process,adjective_phrases,word_count_list,nnp_count_list]
    else :
        return noun_phrases_process
    
def extract_phrases_by_kiwi_legacy(sentence: str, adjective: bool = False):
    available_pos = ["NNG","NNP","XPN","SL","NNG+XSN","NNP+XSN","NNG+NNB","NR+SL","NR+NNB","NR+XSN","XPN+NNG","XPN+NNP"]
    nnp_pos = ["NNP","NNP+XSN","XPN+NNP"]
    josa_pos = ('JKS', 'JKC','JKG','JKO','JKB','JKV','JKQ','JX','SP','SS','SSO','SSC','SF','SE','SW')
    adjective_pos = ["VA","VX","XSA"]

    def join_noun_tokens(noun_phrase_tokens, josa: bool = False):
        first_token = noun_phrase_tokens[0]
        result = first_token["token"]
        index = first_token["start"] + first_token["length"]
        for noun_token in noun_phrase_tokens[1:]:
            c = noun_token["token"]
            if index == noun_token["start"]:
                result += c
            else:
                if len(c) < 2 or len(result) < 2 :
                    return None
                result += f' {c}'
            index = noun_token["start"] + noun_token["length"]
        return result

    def join_and_insert_phrase(noun_phrase_tokens,noun_phrases,josa=True):
        if len(noun_phrase_tokens) > 0 :
            noun_phrase_tokens = list(reversed(noun_phrase_tokens))
            joined_noun_phrase = join_noun_tokens(noun_phrase_tokens.copy(),josa)
            if joined_noun_phrase != None and len(joined_noun_phrase) > 1:
                noun_phrases.append(joined_noun_phrase)
        return joined_noun_phrase
    # Given iterables, Kiwi enables Multi-Threading
    tokens = tokenized_kiwi_with_tag(sentence.replace("\n"," , ").replace("  "," , "),normalize=True,naive=False)

    noun_phrases = list()
    just_noun_phrases = list()
    noun_phrase_tokens = list()
    adjective_phrases = list()
    word_count_dict = {}
    nnp_count_dict = {}
    reversed_tokens = list(reversed(tokens))
    josa_flag = False
    
    reversed_tokens = list(reversed(tokens))
    for i, token in enumerate(reversed_tokens):
        pure_tag = token["pure_tag"]
        if len(token["token"]) > 1 \
            and (pure_tag in adjective_pos or "+XSA" in pure_tag or "+XSV" in pure_tag) \
                and token["token"] not in kiwi_adj_stopwords:
            adjective_phrases.append(token["token"])
        
        if token["tag"] == "W_HASHTAG" :
            process_token = token["token"].replace("#","").replace("_"," ")
            noun_phrases.append(process_token)
            word_count_dict[process_token] = len(process_token.split(" "))
            nnp_count_dict[process_token] = 1

        if pure_tag in available_pos and token["token"] not in kiwi_stopwords:
            noun_phrase_tokens.append(token)
        else :
            if len(noun_phrase_tokens) > 0 :
                word_count = len(noun_phrase_tokens)
                nnp_count = len([token for token in noun_phrase_tokens if token["tag"] in nnp_pos])
                joined_noun_phrase = join_and_insert_phrase(noun_phrase_tokens,noun_phrases)
                noun_phrase_tokens = []
                word_count_dict[joined_noun_phrase] = word_count
                nnp_count_dict[joined_noun_phrase] = nnp_count

    if len(noun_phrase_tokens) > 0 :
        word_count = len(noun_phrase_tokens)
        nnp_count = len([token for token in noun_phrase_tokens if token["tag"] in nnp_pos])
        joined_noun_phrase = join_and_insert_phrase(noun_phrase_tokens,noun_phrases)
        noun_phrase_tokens = []
        word_count_dict[joined_noun_phrase] = word_count
        nnp_count_dict[joined_noun_phrase] = nnp_count
    
    noun_phrases = list(reversed(functools.reduce(lambda acc, cur: acc if cur in acc else acc+[cur], noun_phrases, [])))
    adjective_phrases = list(reversed(functools.reduce(lambda acc, cur: acc if cur in acc else acc+[cur], adjective_phrases, [])))
    
    word_count_list = [ word_count_dict[noun] for noun in noun_phrases]
    nnp_count_list = [ nnp_count_dict[noun] for noun in noun_phrases]

    if adjective :
        return [noun_phrases,adjective_phrases,word_count_list,nnp_count_list]
    else :
        return noun_phrases