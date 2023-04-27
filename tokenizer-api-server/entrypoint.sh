echo "entry point jar download"

rm -rf /usr/local/lib/python3.7/site-packages/konlpy/java/open-korean-text-2.1.0.jar

wget -O /usr/local/lib/python3.7/site-packages/konlpy/java/open-korean-text-2.1.0.jar https://github.com/Keunyoung-Jung/sns-tokenizer-whole/releases/download/7.17.4/open-korean-text-2.1.0.jar

wget -O /app/kiwi-user.dict https://github.com/Keunyoung-Jung/sns-tokenizer-whole/releases/download/7.17.4/kiwi-user.dict

# python3 add_kiwi_dict.py

ulimit -c unlimited

echo "tokenizer update complete"

hypercorn app:app --bind 0.0.0.0:8080 --worker-class uvloop --keep-alive 10 --workers 4 --access-logfile -