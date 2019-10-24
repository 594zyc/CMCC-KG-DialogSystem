import tensorflow as tf
import numpy as np
from NLU_data_helper import Dataset
from NLU_model import EDST, BOW
import os
import json
import pickle
import jieba
import pprint
jieba.load_userdict('../data/_add_words.txt')
jieba.del_word('元档')


class AttrDetector:
    def __init__(self):
        self.hypers = {
            'max_sent_len': 30,
            'emb_size': 300,
            'total_steps': 10000,
            'tolerance': 20
        }
        self.load_data('../data')

    def load_data(self, data_dir):
        with open(os.path.join(data_dir, 'training_data_attr.json'),
                  encoding='utf8') as f:
            self.training_data = json.load(f)
        self.attrs = list(self.training_data.keys())
        self.attrs.remove('无')
        print(self.attrs)
        self.dataset = Dataset(self.training_data, jieba)
        with open(os.path.join(data_dir, 'test_data_attr.json'),
                  encoding='utf8') as f:
            self.test_data = json.load(f)
        print('test_data_len', len(self.test_data))
        with open(os.path.join(data_dir, 'word_dict.json'),
                  encoding='utf8') as f:
            self.word_dict = json.load(f)
        with open(os.path.join(data_dir, 'wordvec300d.pkl'), 'rb') as f:
            self.embs = pickle.load(f)
        with open(os.path.join(data_dir, 'entity_name'),
                  encoding='utf8') as f:
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

    def transform(self, batch_data, batch_label, attr=None):
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


#用 EDST 模型跑 属性识别 实验
class AttrDetector_EDST(AttrDetector):
    def __init__(self):
        super().__init__()

    def transform(self, batch_data, batch_label, attr=None):
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
        if attr is None:
            for i, (sent, a) in enumerate(batch_data):
                for j, w in enumerate(sent):
                    if w in self.word_dict:
                        input_emb[i, j] = self.embs[w]
                    else:
                        input_emb[i, j] = self.embs['UNK']
                    if w == a:
                        input_match[i, j] = 1
                    elif w in a or a in w:
                        input_match[i, j] = 0.5
                attr_emb = np.zeros(self.hypers['emb_size'])
                for w in list(jieba.cut(a)):
                    if w in self.word_dict:
                        attr_emb += self.embs[w]
                    else:
                        attr_emb += self.embs['UNK']
                input_value[i] = attr_emb
                output[i] = batch_label[i]
        else:
            for i, sent in enumerate(batch_data):
                for j, w in enumerate(sent):
                    if w in self.word_dict:
                        input_emb[i, j] = self.embs[w]
                    else:
                        input_emb[i, j] = self.embs['UNK']
                    if w == attr:
                        input_match[i, j] = 1
                    elif w in attr or attr in w:
                        input_match[i, j] = 0.5
                attr_emb = np.zeros(self.hypers['emb_size'])
                for w in list(jieba.cut(attr)):
                    if w in self.word_dict:
                        attr_emb += self.embs[w]
                    else:
                        attr_emb += self.embs['UNK']
                input_value[i] = attr_emb
                output[i] = batch_label[i]
        return input_emb, input_match, input_value, output

    def test(self, sess, model, at=None):
        accuracy = []
        bsize = 100
        start = 0
        predicts = []
        truths = []
        while start < len(self.test_data):
            bdata = [[list(jieba.cut(self.extract_name(d[0]))), at]
                     for d in self.test_data[start:start+bsize]]
            blabel = []
            for d in self.test_data[start:start + bsize]:
                if at in d[1]: blabel.append(1)
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

    def run(self):
        accus = {k:0 for k in self.attrs}
        F1s = {k:0 for k in self.attrs}
        print('prepare models ...')
        all_models = {k: EDST(str(i)) for i,k in enumerate(self.attrs)}
        saver = tf.train.Saver()
        with tf.Session() as sess:
            sess.run(tf.group(tf.global_variables_initializer()))
            saver.restore(sess, './AttrDetector_EDST/model')
            for ii, attr in enumerate(self.attrs):
                print('attr:', attr)
                model = all_models[attr]
                average_loss = 0
                average_accu = 0
                best_test_accu = 0
                best_F1 = 0
                tolerance_count = 0
                plot_every_steps = 100
                self.dataset.set_attr(attr)
                for step in range(1, self.hypers['total_steps'] + 1):
                    batch_data, batch_label = self.dataset.getbatch()
                    input_emb_, input_match_, input_value_, output_ = \
                        self.transform(batch_data, batch_label, attr)
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
                        test_accu, test_F1 = self.test(sess, model, attr)
                        print('test accu:', test_accu, 'test_F1', test_F1)
                        if best_test_accu < test_accu:
                            best_test_accu = test_accu
                            best_F1 = test_F1
                            tolerance_count = 0
                            if 'AttrDetector_EDST' not in os.listdir('.'):
                                os.mkdir('AttrDetector_EDST')
                            saver.save(sess, './AttrDetector_EDST/model')
                        else:
                            tolerance_count += 1
                        if tolerance_count == self.hypers['tolerance']:
                            print('best_accu:', best_test_accu, 'F1', best_F1)
                            break
                        # test(sess, model)
                        average_loss = 0
                        average_accu = 0
                accus[attr] = best_test_accu
                F1s[attr] = best_F1

        print('accu:', accus)
        print('mean accu', np.mean(list(accus.values())))
        print('F1:', F1s)
        print('mean F1', np.mean(list(F1s.values())))

    def eval(self):
        accus = {k: 0 for k in self.attrs}
        F1s = {k: 0 for k in self.attrs}
        print('load models ...')
        all_models = {k: EDST(str(i)) for i, k in enumerate(self.attrs)}
        saver = tf.train.Saver()
        with tf.Session() as sess:
            sess.run(tf.group(tf.global_variables_initializer()))
            saver.restore(sess, './AttrDetector_EDST/model')
            for ii, a in enumerate(self.attrs):
                print('value:', a)
                model = all_models[a]
                self.dataset.set_attr(a)
                test_accu, test_F1 = self.test(sess, model, a)
                accus[a] = test_accu
                F1s[a] = test_F1
                print('test accu:', test_accu, 'test_F1', test_F1)
        print('accu:', accus)
        print('mean accu', np.mean(list(accus.values())))
        print('F1:', F1s)
        print('mean F1', np.mean(list(F1s.values())))


# 用 词袋 模型跑 属性识别 实验
class AttrDetector_BOW(AttrDetector):
    def __init__(self):
        super().__init__()

        # 去停词，差别并不大
        # with open('D:\CMCC\CMCC-Dialog-kg/data/stopwords-zh.json', encoding='utf8') as f:
        #     self.stopwords = set(json.load(f))
        self.stopwords = []
        vocab = self.word_dict
        word_dict = {}
        for w in vocab:
            if w not in self.stopwords:
                word_dict[w] = len(word_dict)
        self.word_dict = word_dict
        print('after del stopwords ', len(word_dict))

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

    def test(self, sess, model, attr=None):
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
                if attr in d[1]:
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

    def run(self):
        accus = {k: 0 for k in self.attrs}
        F1s = {k: 0 for k in self.attrs}
        all_models = [BOW(str(ii), vocab_size=len(self.word_dict))
                      for ii in range(len(self.attrs))]
        saver = tf.train.Saver()
        with tf.Session() as sess:
            sess.run(tf.group(tf.global_variables_initializer()))
            for ii, attr in enumerate(self.attrs):
                print('attr:', attr)
                model = all_models[ii]
                average_loss = 0
                average_accu = 0
                best_test_accu = 0
                best_F1 = 0
                tolerance_count = 0
                plot_every_steps = 100
                self.dataset.set_attr(attr)
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
                        test_accu, test_F1 = self.test(sess, model, attr)
                        print('test accu:', test_accu, 'test_F1', test_F1)
                        if best_test_accu < test_accu:
                            best_test_accu = test_accu
                            best_F1 = test_F1
                            tolerance_count = 0
                            if 'AttrDetector_BOW' not in os.listdir('.'):
                                os.mkdir('AttrDetector_BOW')
                            saver.save(sess, './AttrDetector_BOW/model')
                        else:
                            tolerance_count += 1
                        if tolerance_count == self.hypers['tolerance']:
                            print('best_accu:', best_test_accu)
                            break
                        # test(sess, model)
                        average_loss = 0
                        average_accu = 0
                accus[attr] = best_test_accu
                F1s[attr] = best_F1

        print('accu:', accus)
        print('mean accu', np.mean(list(accus.values())))
        print('F1:', F1s)
        print('mean F1', np.mean(list(F1s.values())))

    def eval(self):
        accus = {k: 0 for k in self.attrs}
        F1s = {k: 0 for k in self.attrs}
        print('load models ...')
        all_models = [BOW(str(ii), vocab_size=len(self.word_dict))
                      for ii in range(len(self.attrs))]
        saver = tf.train.Saver()
        with tf.Session() as sess:
            sess.run(tf.group(tf.global_variables_initializer()))
            saver.restore(sess, './AttrDetector_BOW/model')
            for ii, a in enumerate(self.attrs):
                print('value:', a)
                model = all_models[ii]
                test_accu, test_F1 = self.test(sess, model, a)
                print('test accu:', test_accu, 'test_F1', test_F1)
                accus[a] = test_accu
                F1s[a] = test_F1
        print('accu:', accus)
        print('mean accu', np.mean(list(accus.values())))
        print('F1:', F1s)
        print('mean F1', np.mean(list(F1s.values())))\



if __name__ == '__main__':
    model = AttrDetector_BOW()
    model.run()
    # model.eval()
# mean accu 0.9921901441819536
# mean F1 0.8728749647891921









