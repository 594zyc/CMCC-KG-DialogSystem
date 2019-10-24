import jieba
import json
import pickle

jieba.load_userdict('new_words_.txt')
with open('raw_data.json', encoding='utf8') as f:
    data = json.load(f)
with open('entity_name', encoding='utf8') as f:
    name_dict = json.load(f)
all_names = []
for k in name_dict:
    all_names.append(k)
    all_names.extend(name_dict[k])

def extract_name(sent, all_names):
    for n in all_names:
        if n in sent:
            sent = sent.replace(n, 'subjectname')
    return sent

all_words = []
max_len = 0
for k in data:
    for sent in data[k]['data']:
        sent = extract_name(sent, all_names)
        words = list(jieba.cut(sent))
        max_len = max(max_len, len(words))
        all_words.extend(words)
print(max_len)
from collections import Counter
c = Counter(all_words).most_common(1500-1)
word_dict = {'UNK': 0}
for item in c:
    word_dict[item[0]] = len(word_dict)
with open('word_dict.json', 'w', encoding='utf-8') as f:
    json.dump(word_dict, f, ensure_ascii=False)







