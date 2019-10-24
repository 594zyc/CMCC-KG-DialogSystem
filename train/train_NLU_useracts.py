import tensorflow as tf
import numpy as np
from NLU_data_helper import Dataset_acts
from NLU_model import CNN, BOW
import json
import pickle
import jieba
import os
from dialog.config import user_acts
jieba.load_userdict('../data/_add_words.txt')
jieba.del_word('元档')

class ActDetector:
    def __init__(self):
        self.hypers = {
            'max_sent_len': 30,
            'emb_size': 300,
            'total_steps': 8000,
        }
        self.load_data('../data')

    def load_data(self, data_dir):
        with open(os.path.join(data_dir, 'training_data_act.json'), encoding='utf8') as f:
            self.training_data = json.load(f)
        with open(os.path.join(data_dir, 'test_data_act.json'), encoding='utf8') as f:
            self.test_data = json.load(f)
        for k in self.training_data:
            self.training_data[k].extend(self.test_data[k])
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
        self.acts = user_acts
        self.dataset = Dataset_acts(self.training_data, jieba)

    def transform(self, batch_data, batch_label):
        batch_size = len(batch_data)
        input_emb = np.zeros(shape=[batch_size,
                                    self.hypers['max_sent_len'],
                                    self.hypers['emb_size']],
                             dtype=np.float32)
        output = np.zeros(shape=[batch_size], dtype=np.int32)
        for i, sent in enumerate(batch_data):
            for j, w in enumerate(sent):
                if w in self.word_dict:
                    input_emb[i, j] = self.embs[w]
                else:
                    input_emb[i, j] = self.embs['UNK']
            output[i] = self.acts.index(batch_label[i])
        return input_emb, output

    def extract_name(self, sent):
        for n in self.all_names:
            if n in sent:
                sent = sent.replace(n, 'subjectname')
        return sent

    def test(self, sess, model):
        accus = {k: 0 for k in self.test_data}
        bsize = 200
        for k in self.test_data:
            start = 0
            average_accu = []
            while start < len(self.test_data[k]):
                bdata = [list(jieba.cut(self.extract_name(d)))
                         for d in self.test_data[k][start:start + bsize]]
                blabel = [k for _ in range(len(self.test_data[k][start:start + bsize]))]
                input_emb_, output_ = self.transform(bdata, blabel)
                accu = sess.run(model.accu,
                                feed_dict={
                                    model.input: input_emb_,
                                    model.output: output_})
                average_accu.append(accu)
                start += bsize
            accus[k] = np.mean(average_accu)
        print(accus)
        print('test accu:', np.mean(list(accus.values())))
        return np.mean(list(accus.values()))

    def run(self):
        pass

class ActDetector_CNN(ActDetector):
    def __init__(self):
        super().__init__()

    def run(self):
        model = CNN('act_detection', output_size=len(self.acts))
        saver = tf.train.Saver()
        best_accu = 0
        with tf.Session() as sess:
            sess.run(tf.group(tf.global_variables_initializer()))
            average_loss = 0
            average_accu = 0
            plot_every_steps = 100
            for step in range(1, self.hypers['total_steps'] + 1):
                batch_data, batch_label = self.dataset.getbatch()
                input_emb_, output_ = self.transform(batch_data, batch_label)
                _, loss, accu = sess.run(
                    [model.train_op,
                     model.final_loss,
                     model.accu],
                    feed_dict={
                        model.input:input_emb_ ,
                        model.output: output_})

                average_loss += loss / plot_every_steps
                average_accu += accu / plot_every_steps
                if step % plot_every_steps == 0:
                    print("step %5d, loss=%0.4f, accu=%0.4f" %
                          (step, average_loss, average_accu))
                    test_accu = self.test(sess, model)
                    average_loss = 0
                    average_accu = 0
                    if best_accu<test_accu:
                        saver.save(sess, './ActDetector/model')
                        best_accu = test_accu

    def eval(self):
        model = CNN('act_detection', output_size=len(self.acts))
        saver = tf.train.Saver()
        with tf.Session() as sess:
            # sess.run(tf.group(tf.global_variables_initializer()))
            saver.restore(sess, './ActDetector/model')
            self.test(sess, model)

class ActDetector_BOW(ActDetector):
    def __init__(self):
        super().__init__()
        self.stopwords = []
        vocab = self.word_dict
        word_dict = {}
        for w in vocab:
            if w not in self.stopwords:
                word_dict[w] = len(word_dict)
        self.word_dict = word_dict
        print('after del stopwords ', len(word_dict))

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
            output[i] = self.acts.index(batch_label[i])
        return input_sent, output

    def test(self, sess, model):
        accus = {k: 0 for k in self.test_data}
        bsize = 200
        for k in self.test_data:
            start = 0
            average_accu = []
            while start < len(self.test_data[k]):
                bdata = [list(jieba.cut(self.extract_name(d)))
                         for d in self.test_data[k][start:start + bsize]]
                blabel = [k for _ in range(len(self.test_data[k][start:start + bsize]))]
                input_emb_, output_ = self.transform(bdata, blabel)
                accu = sess.run(model.accuracy,
                                feed_dict={
                                    model.input_sent: input_emb_,
                                    model.output: output_})
                average_accu.append(accu)
                start += bsize
            accus[k] = np.mean(average_accu)
        print(accus)
        print('test accu:', np.mean(list(accus.values())))
        return np.mean(list(accus.values()))

    def run(self):
        model = BOW('act_detection', vocab_size=len(self.word_dict),
                    output_size=len(self.acts))
        saver = tf.train.Saver()
        best_accu = 0
        with tf.Session() as sess:
            sess.run(tf.group(tf.global_variables_initializer()))
            average_loss = 0
            average_accu = 0
            plot_every_steps = 100
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
                    test_accu = self.test(sess, model)
                    average_loss = 0
                    average_accu = 0
                    if best_accu<test_accu:
                        saver.save(sess, './ActDetector_BOW/model')
                        best_accu = test_accu

    def eval(self):
        model = BOW('act_detection', output_size=len(self.acts))
        saver = tf.train.Saver()
        with tf.Session() as sess:
            # sess.run(tf.group(tf.global_variables_initializer()))
            saver.restore(sess, './ActDetector_BOW/model')
            self.test(sess, model)

if __name__ == '__main__':
    model = ActDetector_BOW()
    model.run()
    # model.eval()
# {'问询': 0.9669909, '告知': 0.96350574, '表达肯定': 1.0, '表达否定': 1.0, '更换': 1.0, '请求推荐': 1.0, '进行选择': 1.0, '结束对话': 1.0, '闲聊': 1.0}
# # test accu: 0.9922774








