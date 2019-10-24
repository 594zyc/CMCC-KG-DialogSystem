"""
各个检测器的基类：
实现如共享数据读取，分词等可共享的功能
"""
import os, json, pickle
from dialog.config import user_acts, requestable_attrs, \
    informable_attrs, objects, subjects, entity_price
import jieba


class NLU:
    def __init__(self, load_path='./data'):
        self.hypers = {
            'max_sent_len': 30,
            'emb_size': 300,
        }

        self.load_data(load_path)


    def load_data(self, data_dir):
        with open(os.path.join(data_dir, 'word_dict.json'), encoding='utf8') as f:
            self.word_dict = json.load(f)
        with open(os.path.join(data_dir, 'wordvec300d.pkl'), 'rb') as f:
            self.embs = pickle.load(f)
        self.entity_no_price = subjects
        self.entity_price = entity_price
        self.all_entities = [] # 所有
        # 一种是 **套餐**档 之类
        for k in self.entity_price:
            for p in self.entity_price[k]:
                self.all_entities.append('%s%d元档' % (k, p))
                self.all_entities.append('%s%d元' % (k, p))
        # 一种是 **套餐 之类
        for k in self.entity_no_price:
            self.all_entities.append(k)
            self.all_entities.extend(self.entity_no_price[k])
        self.acts = user_acts
        self.attrs = requestable_attrs
        self.informable_attrs = informable_attrs
        self.values = objects
        jieba.load_userdict(data_dir+'/_add_words.txt')
        jieba.del_word('元档')

    def extract_name(self, sent):
        for n in self.all_entities:
            if n in sent:
                sent = sent.replace(n, 'subjectname')
        return sent

    def wordseg(self, sent):
        return list(jieba.cut(self.extract_name(sent)))

if __name__ == '__main__':
    nlu =NLU()
    print(nlu.all_entities)
    while True:
        s = input('输入:')
        print(nlu.wordseg(s))