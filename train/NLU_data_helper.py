import random
import copy
import json


with open('../data/entity_name', encoding='utf8') as f:
    name_dict = json.load(f)
all_names = []
for k in name_dict:
    all_names.append(k)
    all_names.extend(name_dict[k])

def extract_name(sent):
    for n in all_names:
        if n in sent:
            sent = sent.replace(n, 'subjectname')
    return sent


class Dataset_acts:
    def __init__(self, data, jieba):
        self.data = {}
        for k in data:
            self.data[k] = []
            for sent in data[k]:
                self.data[k].append(list(jieba.cut(extract_name(sent))))
        self.num = len(self.data)
        self.batch_id = {k:0 for k in self.data}

    def getbatch(self):
        batch_data = []
        batch_label = []
        for k in self.batch_id:
            if self.batch_id[k]==len(self.data[k]):
                self.batch_id[k] = 0
                random.shuffle(self.data[k])
            batch_data.append(self.data[k][self.batch_id[k]])
            batch_label.append(k)
            self.batch_id[k] += 1
        return batch_data, batch_label


class Dataset:
    def __init__(self, data, jieba):
        self.data = {}
        for k in data:
            self.data[k] = []
            for sent in data[k]:
                self.data[k].append(list(jieba.cut(extract_name(sent))))
        self.num = len(self.data)

    def set_attr(self, attr):
        self.pos_id = 0
        self.neg_id = 0
        self.pos_data = copy.deepcopy(self.data[attr])
        self.neg_data = []
        for k in self.data:
            if k != attr:
                self.neg_data.extend(copy.deepcopy(self.data[k]))
        # random.shuffle(self.pos_data)
        # random.shuffle(self.neg_data)


    def getbatch(self, batch_size=64):
        # 正负例 1:3
        batch_data = []
        batch_label = [1] * (batch_size//4) + [0] * (batch_size//4*3)
        if self.pos_id + batch_size//4 >= len(self.pos_data):
            self.pos_id = 0
            random.shuffle(self.pos_data)
        batch_data.extend(self.pos_data[self.pos_id: self.pos_id+batch_size//4])
        self.pos_id += batch_size//4
        if self.neg_id + batch_size//4*3 >= len(self.neg_data):
            self.neg_id = 0
            random.shuffle(self.neg_data)
        batch_data.extend(self.neg_data[self.neg_id: self.neg_id+batch_size//4*3])
        self.neg_id += batch_size//4*3
        return batch_data, batch_label









