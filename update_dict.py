import requests
import sys
import os
from bson.objectid import ObjectId
from tqdm import tqdm
import boto3
from kiwipiepy import Kiwi

central_server = "http://central_server"
base_dir = '/open-korean-text/src/main/resources/org/openkoreantext/processor/util'
kiwi_dir = '/kiwi-dict'
kiwi = Kiwi()
# base_dir = './test'
origin = ['예쁜','있어서','비싼']

def noun_to_kiwi(os_path,nouns) :
    with open(f'{os_path}/kiwi-user.dict','a') as fd :
        for noun in tqdm(nouns) :
            fd.write(f"{os.linesep}{noun}\tNNP\t-10.0000")

def adjective_to_kiwi(os_path,adjectives) :
    with open(f'{os_path}/kiwi-user.dict','a') as fd :
        for adjective in tqdm(adjectives) :
            fd.write(f"{os.linesep}{adjective}\tVA\t-10.0000")
            
def suffix_to_kiwi(os_path,suffixs) :
    with open(f'{os_path}/kiwi-user.dict','a') as fd :
        for suffix in tqdm(suffixs) :
            fd.write(f"{os.linesep}{suffix}\tXSN\t-10.0000")
            
def typo_to_kiwi(os_path,typos) :
    with open(f'{os_path}/kiwi-user.dict','a') as fd :
        for typo in tqdm(typos) :
            if typo[0][-1] not in ["용","엉","욤","웡"] :
                result = kiwi.tokenize(typo[1])
                change = " + ".join([f"{res.form}/{res.tag}" for res in result])
                fd.write(f"{os.linesep}{result[0].form}\t{result[0].tag}\t-10.0000")
                fd.write(f"{os.linesep}{typo[0]}\t{change}\t-5.0000")

def download_dictionary(file,os_path):
    response = requests.get(
        url=f"{central_server}/download/storage/dictionary",
        params={"file":file}
    )
    with open(f"{os_path}/{file}","wb") as text:
        text.write(response.content)
        
def upload_dictionary(file,os_path):
    bucket = os.getenv("AWS_S3_BUCKET")
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(os_path+'/'+file, bucket, "tokenizer/backup-dictionary/"+file)

def get_update_word(tag_name):
    response = requests.get(
        url=f"{central_server}/dictionary/word_dict/{tag_name}"
    )
    update_word = response.json()
    return update_word

def get_flag_false_word(tag_name):
    response = requests.get(
        url=f"{central_server}/dictionary/word_dict/{tag_name}",
        params={"updated_flag": False}
    )
    update_word = response.json()
    return update_word

def patch_flag_true(tag_name, words):
    response = requests.patch(
        url=f"{central_server}/dictionary/word_dict/{tag_name}",
        json={"word": words}
    )

def patch_flag_true_typo(tag_name, source_typo, target_typo):
    response = requests.patch(
        url=f"{central_server}/dictionary/word_dict/{tag_name}",
        json={"source_typo": source_typo, "target_typo":target_typo}
    )

def main():
    print("[INFO]------사전 업데이트 작업 진행------")
    download_dictionary(file="adjective.txt",os_path=base_dir+"/adjective")
    download_dictionary(file="names.txt",os_path=base_dir+"/noun")
    download_dictionary(file="suffix.txt",os_path=base_dir+"/substantives")
    download_dictionary(file="typos.txt",os_path=base_dir+"/typos")
    download_dictionary(file="kiwi-user.dict",os_path=kiwi_dir)
    
    with open(f'{base_dir}/adjective/adjective.txt', mode='a', encoding = 'utf-8') as fd :
        words = get_update_word("adjective")
        for word in words:
            fd.write(f"{os.linesep}{word}")
        adjective_to_kiwi(kiwi_dir,words)
        false_words = get_flag_false_word("adjective")
        patch_flag_true("adjective", false_words)
        
            
    with open(f'{base_dir}/noun/names.txt', mode='a', encoding = 'utf-8') as fd :
        words = get_update_word("noun")
        for word in words:
            fd.write(f"{os.linesep}{word}")
        for word in user_words :
            fd.write(f"{os.linesep}{word.replace(' ','')}")
        noun_to_kiwi(kiwi_dir,words+user_words)
        false_words = get_flag_false_word("noun")
        patch_flag_true("noun", false_words)
            
    with open(f'{base_dir}/substantives/suffix.txt', mode='a', encoding = 'utf-8') as fd :
        words = get_update_word("suffix")
        for word in words:
            fd.write(f"{os.linesep}{word}")
        suffix_to_kiwi(kiwi_dir,words)
        false_words = get_flag_false_word("suffix")
        patch_flag_true("suffix", false_words)
            
    with open(f'{base_dir}/typos/typos.txt', mode='a', encoding = 'utf-8') as fd :
        words = get_update_word("typo")
        for word in words:
            fd.write(f"{os.linesep}{' '.join(word)}")
        typo_to_kiwi(kiwi_dir,words)
        false_words = get_flag_false_word("typo")
        for source_typo, target_typo in false_words :
            patch_flag_true_typo("typo", source_typo,target_typo)
            
    print("[COMPLETE]------사전 업데이트 작업 완료------")
            
    upload_dictionary(file="adjective.txt",os_path=base_dir+"/adjective")
    upload_dictionary(file="names.txt",os_path=base_dir+"/noun")
    upload_dictionary(file="suffix.txt",os_path=base_dir+"/substantives")
    upload_dictionary(file="typos.txt",os_path=base_dir+"/typos")
    upload_dictionary(file="kiwi-user.dict",os_path=kiwi_dir)

if __name__ == '__main__':
    main()