"""
检测知识图谱中被用户提及的
1. 关系名（属性）
2. 属性取值（费用、流量、通话时长三者的取值）
"""
import numpy as np
import tensorflow as tf
from train.NLU_model import EDST, BOW
from dialog.NLU.NLUDetectors import NLU

class ValueDetector(NLU):
    def __init__(self, model_path):
        super(ValueDetector, self).__init__()
        self.tf_graph = tf.Graph()
        with self.tf_graph.as_default():
            self.all_models = {k: EDST(str(i)) for i, k in enumerate(self.values)}
            self.saver = tf.train.Saver()
            tf_config = tf.ConfigProto()
            tf_config.gpu_options.allow_growth = True
            self.sess = tf.Session(config=tf_config)
            # var_to_restore = [val for val in tf.global_variables()
            #                   if 'Adam' not in val.name]
            # self.saver = tf.train.Saver(var_to_restore)
            self.saver.restore(self.sess, model_path + "/model")

    def get_prob(self, l):
        return np.exp(l[1]) / (np.exp(l[0])+np.exp(l[1]))

    def get_value_results(self, user_utter):
        detected_values = []
        for ii, value in enumerate(self.values):
            bdata = [[self.wordseg(user_utter), value]]
            blabel = [0]  # 没用到，随便找个label
            input_emb_, input_match_, input_value_, output_ = \
                self.transform(bdata, blabel)
            pred, logits = self.sess.run([self.all_models[value].predict,
                                  self.all_models[value].final_output_logits],
                               feed_dict={
                                   self.all_models[value].input_emb: input_emb_,
                                   self.all_models[value].input_match: input_match_,
                                   self.all_models[value].input_value: input_value_})
            # print('value:', value, 'pred:', pred)
            if pred[0]>0:
                detected_values.append((value, self.get_prob(logits[0])))
        detected_values.sort(key=lambda x:x[1], reverse=True)
        return detected_values[0] if len(detected_values)>0 else None


    def transform(self, batch_data, batch_label):
        batch_size = len(batch_data)
        input_emb = np.zeros(shape=[batch_size,
                                    self.hypers['max_sent_len'],
                                    self.hypers['emb_size']], dtype=np.float32)
        input_match = np.zeros(shape=[batch_size,
                                      self.hypers['max_sent_len']
                                      ], dtype=np.float32)
        input_value = np.zeros(shape=[batch_size,
                                      self.hypers['emb_size']
                                      ], dtype=np.float32)
        output = np.zeros(shape=[batch_size], dtype=np.int32)
        for i, (sent, v) in enumerate(batch_data):
            for j, w in enumerate(sent):
                if j < self.hypers['max_sent_len']:
                    if w in self.word_dict:
                        input_emb[i, j] = self.embs[w]
                    else:
                        input_emb[i, j] = self.embs['UNK']
                    if w == v:
                        input_match[i, j] = 1
                    elif w in v or v in w:
                        input_match[i, j] = 0.5
            value_emb = np.zeros(self.hypers['emb_size'])

            for w in self.wordseg(v):
                if w in self.word_dict:
                    value_emb += self.embs[w]
                else:
                    value_emb += self.embs['UNK']
            input_value[i] = value_emb
            output[i] = batch_label[i]
        return input_emb, input_match, input_value, output

    def close(self):
        self.sess.close()

class AttrDetector(NLU): # 这里选用 词袋模型 因为运行快且结果不差
    def __init__(self, model_path):
        super(AttrDetector, self).__init__()
        self.stopwords = []
        vocab = self.word_dict
        word_dict = {}
        for w in vocab:
            if w not in self.stopwords:
                word_dict[w] = len(word_dict)
        self.word_dict = word_dict
        self.tf_graph = tf.Graph()
        with self.tf_graph.as_default():
            self.all_models = [BOW(str(ii), vocab_size=len(self.word_dict))
                      for ii in range(len(self.attrs))]
            self.saver = tf.train.Saver()
            tf_config = tf.ConfigProto()
            tf_config.gpu_options.allow_growth = True
            self.sess = tf.Session(config=tf_config)
            # var_to_restore = [val for val in tf.global_variables()
            #                   if 'Adam' not in val.name]
            # self.saver = tf.train.Saver(var_to_restore)
            self.saver.restore(self.sess, model_path + "/model")

    def get_prob(self, l):
        return np.exp(l[1]) / (np.exp(l[0])+np.exp(l[1]))

    def get_attr_results(self, user_utter):
        detected_attr = []
        for ii, attr in enumerate(self.attrs):
            bdata = [self.wordseg(user_utter)]
            blabel = [0]  # 没用到，随便找个label
            input_sent_, output_ = self.transform(bdata, blabel)
            pred, logits = self.sess.run([self.all_models[ii].predict,
                                  self.all_models[ii].output_logits],
                               feed_dict={
                                   self.all_models[ii].input_sent: input_sent_,
                                   self.all_models[ii].output: output_})
            # print('attr:', attr, 'pred:', pred, 'logits', logits)
            if pred[0] > 0:
                detected_attr.append((attr, self.get_prob(logits[0])))
        detected_attr.sort(key=lambda x: x[1], reverse=True)
        return {k:v for k,v in detected_attr}

    def transform(self, batch_data, batch_label, attr=None):
        batch_size = len(batch_data)
        input_sent = np.zeros(shape=[batch_size, len(self.word_dict)],
                              dtype=np.float32)
        output = np.zeros(shape=[batch_size], dtype=np.int32)
        for i, sent in enumerate(batch_data):
            for j, w in enumerate(sent):
                if w in self.word_dict:
                    input_sent[i, self.word_dict[w]] = 1
                else:
                    input_sent[i, self.word_dict['UNK']] = 1
            output[i] = batch_label[i]
        return input_sent, output

    def close(self):
        self.sess.close()


if __name__ == '__main__':
    # model = AttrDetector('D:\CMCC\CMCC-Dialog-kg\\train\AttrDetector_BOW')
    model = ValueDetector('D:\CMCC\CMCC-Dialog-kg\\train/ValueDetector_EDST')
    ss = ['全球通无限尊享计划套餐给我介绍介绍', '帮我变更一下彩信套餐',
          '给我开通一下', '4G流量加油包套餐外收费情况是什么样的呀',
          '告诉我畅游包有几兆流量','办理后，是即时生效，还是下月生效？',
          '畅享套餐38元档介绍一下', "推荐个便宜的套餐"]
    for s in ss:
        print(s, model.get_value_results(s))
