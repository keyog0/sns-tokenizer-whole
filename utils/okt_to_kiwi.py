import sys
import os
from tqdm import tqdm
from kiwipiepy import Kiwi

kiwi = Kiwi()

nouns = []
adjectives = []
suffixs = []
typos = []
base_dir = "../Dictionary"

for dirl in tqdm(os.listdir(f'{base_dir}/noun')) :
    with open(f'{base_dir}/noun/'+dirl,'r') as f:
        while True:
            line = f.readline()
            if not line : break
            nouns.append(line.strip().replace(' ',""))

for dirl in tqdm(os.listdir(f'{base_dir}/adjective')) :
    with open(f'{base_dir}/adjective/'+dirl,'r') as f:
        while True:
            line = f.readline()
            if not line : break
            adjectives.append(line.strip().replace(' ',""))

with open(f'{base_dir}/substantives/suffix.txt','r') as f:
    while True:
        line = f.readline()
        if not line : break
        suffixs.append(line.strip().replace(' ',""))

with open(f'{base_dir}/typos/typos.txt','r') as f:
    while True:
        line = f.readline()
        if not line : break
        typos.append([typo.strip().replace(' ',"") for typo in line.split(" ")])
            
def noun_to_kiwi() :
    with open('user.dict','a') as fd :
        for noun in tqdm(nouns) :
            fd.write(f"{os.linesep}{noun}\tNNP\t-10.0000")

def adjective_to_kiwi() :
    with open('user.dict','a') as fd :
        for adjective in tqdm(adjectives) :
            fd.write(f"{os.linesep}{adjective}\tVA\t-10.0000")
            
def suffix_to_kiwi() :
    with open('user.dict','a') as fd :
        for suffix in tqdm(suffixs) :
            fd.write(f"{os.linesep}{suffix}\tXSN\t-10.0000")
            
def typo_to_kiwi() :
    with open('user.dict','a') as fd :
        for typo in tqdm(typos) :
            if typo[0][-1] not in ["용","엉","욤","웡"] :
                result = kiwi.tokenize(typo[1])
                change = " + ".join([f"{res.form}/{res.tag}" for res in result])
                fd.write(f"{os.linesep}{result[0].form}\t{result[0].tag}\t-10.0000")
                fd.write(f"{os.linesep}{typo[0]}\t{change}\t-5.0000")
            
def main():
    with open('user.dict','a') as fd :
        fd.write(f"{os.linesep}#형용사 사전 정보{os.linesep}")
    adjective_to_kiwi()
    with open('user.dict','a') as fd :
        fd.write(f"{os.linesep}#접미사 사전 정보{os.linesep}")
    suffix_to_kiwi()
    with open('user.dict','a') as fd :
        fd.write(f"{os.linesep}#명사 사전 정보{os.linesep}")
    noun_to_kiwi() 
    with open('user.dict','a') as fd :
        fd.write(f"{os.linesep}#typo 수정하는 부분입니다.{os.linesep}")
    typo_to_kiwi()
    
if __name__ == '__main__':
    main()