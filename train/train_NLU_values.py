import tensorflow as tf
import numpy as np
from NLU_data_helper import Dataset
from NLU_model import EDST, BOW
import os
import json
import pickle
import jieba
jieba.load_userdict('../data/_add_words.txt')
jieba.del_word('元档')
jieba.del_word('一个')

class ValueDetector:
    def __init__(self):
        self.hypers = {
            'max_sent_len': 30,
            'emb_size': 300,
            'total_steps': 10000,
            'tolerance': 20
        }
        self.load_data('../data')

    def load_data(self, data_dir):
        with open(os.path.join(data_dir, 'training_data_value.json'), encoding='utf8') as f:
            self.training_data = json.load(f)
        self.values = list(self.training_data.keys())
        self.dataset = Dataset(self.training_data, jieba)
        with open(os.path.join(data_dir, 'test_data_value.json'), encoding='utf8') as f:
            self.test_data = json.load(f)
        print('test_data_len', len(self.test_data))
        with open(os.path.join(data_dir, 'word_dict.json'), encoding='utf8') as f:
            self.word_dict = json.load(f)
        with open(os.path.join(data_dir, 'wordvec300d.pkl'), 'rb') as f:
            self.embs = pickle.load(f)
        with open(os.path.join(data_dir, 'entity_name'), encoding='utf8') as f:
            self.name_dict = json.load(f)
        self.all_names = [] # 所有
        for k in self.name_dict:
            self.all_names.append(k)
            self.all_names.extend(self.name_dict[k])

    def extract_name(self, sent):
        for n in self.all_names:
            if n in sent:
                sent = sent.replace(n, 'subjectname')
        return sent

    def transform(self, batch_data, batch_label, value=None):
        pass

    @staticmethod
    def get_F1score(correct, predict):
        """
        correct like [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        predict like [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
        :return: F1
        """
        hit = 0
        precision_set = 0
        recall_set = 0
        for i in range(len(correct)):
            if correct[i] == predict[i] and predict[i] == 1:
                hit += 1
            if correct[i] == 1:
                precision_set += 1
            if predict[i] == 1:
                recall_set += 1
        return 2*hit/(precision_set + recall_set)

    def test(self, sess, model, v=None):
        pass

    def run(self): # 跑模型，并存起来
        pass

    def eval(self): # 测试模型
        pass

#用 EDST 模型跑 宾语值识别 实验
class ValueDetector_EDST(ValueDetector):
    def __init__(self):
        super().__init__()

    def run(self):
        accus = {k: 0 for k in self.values}
        F1s = {k: 0 for k in self.values}
        print('prepare models ...')
        all_models = {k: EDST(str(i)) for i, k in enumerate(self.values)}
        saver = tf.train.Saver()
        with tf.Session() as sess:
            sess.run(tf.group(tf.global_variables_initializer()))
            for ii, value in enumerate(self.values):
                print('value:', value)
                model = all_models[value]
                average_loss = 0
                average_accu = 0
                best_test_accu = 0
                tolerance_count = 0
                plot_every_steps = 100
                self.dataset.set_attr(value)
                for step in range(1, self.hypers['total_steps'] + 1):
                    batch_data, batch_label = self.dataset.getbatch()
                    input_emb_, input_match_, input_value_, output_ = \
                        self.transform(batch_data, batch_label, value)
                    _, loss, accu = sess.run(
                        [model.train_op,
                         model.final_loss,
                         model.accu],
                        feed_dict={
                            model.input_emb: input_emb_,
                            model.input_match: input_match_,
                            model.input_value: input_value_,
                            model.output: output_})

                    average_loss += loss / plot_every_steps
                    average_accu += accu / plot_every_steps
                    if step % plot_every_steps == 0:
                        print("step %5d, loss=%0.4f, accu=%0.4f" %
                              (step, average_loss, average_accu))
                        test_accu, test_F1 = self.test(sess, model, value)
                        print('test accu:', test_accu, 'test_F1', test_F1)
                        if best_test_accu < test_accu:
                            best_test_accu = test_accu
                            best_F1 = test_F1
                            tolerance_count = 0
                            if 'ValueDetector_EDST' not in os.listdir('.'):
                                os.mkdir('ValueDetector_EDST')
                            saver.save(sess, './ValueDetector_EDST/model')
                        else:
                            tolerance_count += 1
                        if tolerance_count == self.hypers['tolerance']:
                            print('best_accu:', best_test_accu, 'F1', best_F1)
                            break
                        # test(sess, model)
                        average_loss = 0
                        average_accu = 0
                accus[value] = best_test_accu
                F1s[value] = best_F1

        print('accu:', accus)
        print('mean accu', np.mean(list(accus.values())))
        print('F1:', F1s)
        print('mean F1', np.mean(list(F1s.values())))

    def eval(self):
        accus = {k: 0 for k in self.values}
        F1s = {k: 0 for k in self.values}
        print('load models ...')
        all_models = {k: EDST(str(i)) for i, k in enumerate(self.values)}
        saver = tf.train.Saver()
        with tf.Session() as sess:
            sess.run(tf.group(tf.global_variables_initializer()))
            saver.restore(sess, './ValueDetector_EDST/model')
            for ii, value in enumerate(self.values):
                print('value:', value)
                model = all_models[value]
                self.dataset.set_attr(value)
                test_accu, test_F1 = self.test(sess, model, value)
                accus[value] = test_accu
                F1s[value] = test_F1
                print('test accu:', test_accu, 'test_F1', test_F1)
        print('accu:', accus)
        print('mean accu', np.mean(list(accus.values())))
        print('F1:', F1s)
        print('mean F1', np.mean(list(F1s.values())))

    def transform(self, batch_data, batch_label, value=None):
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
        if value is None:
            for i, (sent, v) in enumerate(batch_data):
                for j, w in enumerate(sent):
                    if w in self.word_dict:
                        input_emb[i, j] = self.embs[w]
                    else:
                        input_emb[i, j] = self.embs['UNK']
                    if w == v:
                        input_match[i, j] = 1
                    elif w in v or v in w:
                        input_match[i, j] = 0.5
                value_emb = np.zeros(self.hypers['emb_size'])

                for w in list(jieba.cut(v)):
                    if w in self.word_dict:
                        value_emb += self.embs[w]
                    else:
                        value_emb += self.embs['UNK']
                input_value[i] = value_emb
                output[i] = batch_label[i]
        else:
            for i, sent in enumerate(batch_data):
                for j, w in enumerate(sent):
                    if w in self.word_dict:
                        input_emb[i, j] = self.embs[w]
                    else:
                        input_emb[i, j] = self.embs['UNK']
                    if w == value:
                        input_match[i, j] = 1
                    elif w in value or value in w:
                        input_match[i, j] = 0.5
                value_emb = np.zeros(self.hypers['emb_size'])
                for w in list(jieba.cut(value)):
                    if w in self.word_dict:
                        value_emb += self.embs[w]
                    else:
                        value_emb += self.embs['UNK']
                input_value[i] = value_emb
                output[i] = batch_label[i]
        return input_emb, input_match, input_value, output

    def test(self, sess, model, v=None):
        accuracy = []
        bsize = 100
        start = 0
        predicts = []
        truths = []
        while start < len(self.test_data):
            bdata = [[list(jieba.cut(self.extract_name(d[0]))), v]
                     for d in self.test_data[start:start+bsize]]
            blabel = []
            for d in self.test_data[start:start + bsize]:
                if v in d[1]: blabel.append(1)
                else: blabel.append(0)

            input_emb_, input_match_, input_value_, output_ = \
                self.transform(bdata, blabel)
            predict = sess.run(model.predict,
                            feed_dict={
                                model.input_emb: input_emb_,
                                model.input_match: input_match_,
                                model.input_value: input_value_})
            predicts.extend([i for i in predict])
            truths.extend(blabel)
            for i in range(len(predict)):
                if predict[i] == blabel[i]:
                    accuracy.append(1)
                else:
                    accuracy.append(0)
            start += bsize
        F1 = self.get_F1score(truths, predicts)
        return np.mean(accuracy), F1

# 神经网络的模型不够稳定，需要每个tracker分别调优
# accu: {'少': 0.8245614035087719, '中': 0.9897660818713451, '多': 0.827485380116959, '任意': 0.9868421052631579, '更多': 0.9853801169590644, '更少': 0.97953216374269}
# mean accu 0.932261208576998
# F1: {'少': 0.6551724137931034, '中': 0.968609865470852, '多': 0.6529411764705882, '任意': 0.9606986899563319, '更多': 0.956140350877193, '更少': 0.9380530973451328}
# mean F1 0.8552692656522002

# 仅仅利用字符串匹配
class StringMatch(ValueDetector):
    def __init__(self):
        super().__init__()
        predicts = []
        truths = []
        accuracy = []
        for d in self.test_data:
            if '低' in d[0] or '少' in d[0]:
                predicts.append(self.values.index('少'))
            elif '中等' in d[0]:
                predicts.append(self.values.index('中'))
            elif '高' in d[0] or  '多'in d[0]:
                predicts.append(self.values.index('多'))
            elif '更多' in d[0] or  '更高'in d[0]:
                predicts.append(self.values.index('更多'))
            else:
                predicts.append(self.values.index('任意'))
            truths.append(self.values.index(d[1]))

        for i in range(len(predicts)):
            if predicts[i] == truths[i]:
                accuracy.append(1)
            else:
                accuracy.append(0)
        print(np.mean(accuracy))

#用 词袋 模型跑 宾语值识别 实验
class ValueDetector_BOW(ValueDetector):
    def __init__(self):
        super().__init__()
        # 去停词，差别并不大
        # with open('data/stopwords-zh.json', encoding='utf8') as f:
        #     self.stopwords = set(json.load(f))
        self.stopwords = []
        vocab = self.word_dict
        word_dict = {}
        for w in vocab:
            if w not in self.stopwords:
                word_dict[w] = len(word_dict)
        self.word_dict = word_dict
        print('after del stopwords ', len(word_dict))

    def run(self):
        accus = {k: 0 for k in self.values}
        F1s = {k: 0 for k in self.values}
        print('prepare models ...')
        all_models = [BOW(str(ii), vocab_size=len(self.word_dict))
                      for ii in range(len(self.values))]
        saver = tf.train.Saver()
        with tf.Session() as sess:
            sess.run(tf.group(tf.global_variables_initializer()))
            for ii, v in enumerate(self.values):
                print('value:', v)
                model = all_models[ii]
                average_loss = 0
                average_accu = 0
                best_test_accu = 0
                tolerance_count = 0
                plot_every_steps = 100
                self.dataset.set_attr(v)
                for step in range(1, self.hypers['total_steps'] + 1):
                    batch_data, batch_label = self.dataset.getbatch()
                    input_sent_, output_ = self.transform(batch_data, batch_label)
                    _, loss, accu = sess.run(
                        [model.train_op,
                         model.final_loss,
                         model.accuracy],
                        feed_dict={
                            model.input_sent: input_sent_,
                            model.output: output_})

                    average_loss += loss / plot_every_steps
                    average_accu += accu / plot_every_steps
                    if step % plot_every_steps == 0:
                        print("step %5d, loss=%0.4f, accu=%0.4f" %
                              (step, average_loss, average_accu))
                        test_accu, test_F1 = self.test(sess, model, v)
                        print('test accu:', test_accu, 'test_F1', test_F1)
                        if best_test_accu < test_accu:
                            best_test_accu = test_accu
                            best_F1 = test_F1
                            tolerance_count = 0
                            if 'ValueDetector_BOW' not in os.listdir('.'):
                                os.mkdir('ValueDetector_BOW')
                            saver.save(sess, './ValueDetector_BOW/model')
                        else:
                            tolerance_count += 1
                        if tolerance_count == self.hypers['tolerance']:
                            print('best_accu:', best_test_accu)
                            break
                        average_loss = 0
                        average_accu = 0
                accus[v] = best_test_accu
                F1s[v] = best_F1

        print('accu:', accus)
        print('mean accu', np.mean(list(accus.values())))
        print('F1:', F1s)
        print('mean F1', np.mean(list(F1s.values())))

    def eval(self):
        accus = {k: 0 for k in self.values}
        F1s = {k: 0 for k in self.values}
        print('load models ...')
        all_models = [BOW(str(ii), vocab_size=len(self.word_dict))
                      for ii in range(len(self.values))]
        saver = tf.train.Saver()
        with tf.Session() as sess:
            sess.run(tf.group(tf.global_variables_initializer()))
            saver.restore(sess, './ValueDetector_BOW/model')
            for ii, v in enumerate(self.values):
                print('value:', v)
                model = all_models[ii]
                test_accu, test_F1 = self.test(sess, model, v)
                print('test accu:', test_accu, 'test_F1', test_F1)
                accus[v] = test_accu
                F1s[v] = test_F1

        print('accu:', accus)
        print('mean accu', np.mean(list(accus.values())))
        print('F1:', F1s)
        print('mean F1', np.mean(list(F1s.values())))

    def transform(self, batch_data, batch_label, value=None):
        batch_size = len(batch_data)
        input_sent = np.zeros(shape=[batch_size, len(self.word_dict)], dtype=np.float32)
        output = np.zeros(shape=[batch_size], dtype=np.int32)
        for i, sent in enumerate(batch_data):
            for j, w in enumerate(sent):
                if w in self.word_dict:
                    input_sent[i, self.word_dict[w]] = 1
                else:
                    input_sent[i, self.word_dict['UNK']] = 1
            output[i] = batch_label[i]
        return input_sent, output

    def test(self, sess, model, v=None):
        accuracy = []
        bsize = 100
        start = 0
        predicts = []
        truths = []
        while start < len(self.test_data):
            bdata = [list(jieba.cut(self.extract_name(d[0])))
                     for d in self.test_data[start:start + bsize]]
            blabel = []
            for d in self.test_data[start:start + bsize]:
                if v in d[1]:
                    blabel.append(1)
                else:
                    blabel.append(0)
            input_sent_, output_ = self.transform(bdata, blabel)
            predict = sess.run(model.predict,
                               feed_dict={
                                   model.input_sent: input_sent_,
                                   model.output: output_})
            predicts.extend([i for i in predict])
            truths.extend(blabel)
            for i in range(len(predict)):
                if predict[i] == blabel[i]:
                    accuracy.append(1)
                else:
                    accuracy.append(0)
            start += bsize
        F1 = self.get_F1score(truths, predicts)
        return np.mean(accuracy), F1

# 词袋模型十分稳定，结果如下
# accu: {'少': 0.7997076023391813, '中': 0.9722222222222222, '多': 0.8187134502923976, '任意': 0.9751461988304093, '更多': 0.9502923976608187, '更少': 0.9488304093567251}
# mean accu 0.9108187134502925
# F1: {'少': 0.5934718100890207, '中': 0.9155555555555556, '多': 0.6352941176470588, '任意': 0.9244444444444444, '更多': 0.8468468468468469, '更少': 0.8401826484018264}
# mean F1 0.7926325704974587


if __name__ == '__main__':
    model = ValueDetector_EDST()
    # model.run()
    model.eval()
















