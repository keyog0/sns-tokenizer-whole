import os
from tqdm import tqdm

origin = []

print('create origin array')
for dirl in tqdm(os.listdir('../Dictionary/noun')) :
    with open('../Dictionary/noun/'+dirl,'r') as f:
        while True:
            line = f.readline()
            if not line : break
            origin.append(line)


print('Check & delete distinct')

tmp = []
for txtl in tqdm(os.listdir('../custom-dict')) :
    filename = txtl
    custom = open(f'../custom-dict/{filename}','r')
    count = 1
    x = 0
    
    while True:
        count += 1
        if count % 100 == 1:
            x += 1
            b = "Loading" + "." * x
            print (b, end="\r")
        line = custom.readline()
        if not line : break
        word = line
        if word not in origin :
            tmp.append(word)
        else :
            pass
        if count == 2001 :
            print('')
            count = 0
            x = 0
            
tmp = list(set(tmp))

print('Save start')
with open('../deleted_distinct_nouns_set.txt','w') as f:
    for word in tmp :
        f.write(word)
