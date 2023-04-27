import os

filename = 'niadic_new'
mecab = open(filename+'.csv','r') 
okt = open(filename+'.txt','w')

while True:
    line = mecab.readline()
    if not line : break
    word = line.split(',')[0]
    okt.write(f'{word}{os.linesep}')
    
mecab.close()
okt.close()