"""
用户动作识别
"""
import numpy as np
import tensorflow as tf
from train.NLU_model import BOW
from dialog.NLU.NLUDetectors import NLU


class UserActDetector(NLU):
    def __init__(self, model_path):
        super(UserActDetector, self).__init__()
        self.stopwords = []
        vocab = self.word_dict
        word_dict = {}
        for w in vocab:
            if w not in self.stopwords:
                word_dict[w] = len(word_dict)
        self.word_dict = word_dict
        self.tf_graph = tf.Graph()
        with self.tf_graph.as_default():
            self.model = BOW('act_detection', vocab_size=len(self.word_dict),
                    output_size=len(self.acts))
            self.saver = tf.train.Saver()
            tf_config = tf.ConfigProto()
            tf_config.gpu_options.allow_growth = True
            self.sess = tf.Session(config=tf_config)
            # var_to_restore = [val for val in tf.global_variables()
            #                   if 'Adam' not in val.name]
            # self.saver = tf.train.Saver(var_to_restore)
            self.saver.restore(self.sess, model_path + "/model")

    def get_prob(self, l):
        return np.exp(l)/sum(np.exp(l))

    def get_user_act_results(self, user_utter):
        bdata = [self.wordseg(user_utter)]
        blabel = ['问询']  # 没用到，随便找个动作
        input_emb_, output_ = self.transform(bdata, blabel)
        logits = self.sess.run(self.model.output_logits,
                        feed_dict={
                            self.model.input_sent: input_emb_,
                            self.model.output: output_})
        # print('pred:', pred)
        output_acts = []
        probs = self.get_prob(logits[0])
        for i in range(len(self.acts)):
            output_acts.append((self.acts[i], probs[i]))
        output_acts.sort(key=lambda x:x[1], reverse=True)
        return output_acts[0]

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
            output[i] = self.acts.index(batch_label[i])
        return input_sent, output

    def close(self):
        self.sess.close()

if __name__ == '__main__':
    model = UserActDetector('D:\CMCC\CMCC-Dialog-kg\\train\ActDetector_BOW')
    ss = ['高一档的套餐',
          '怎么开通畅享套餐',
          '嗯嗯我就是问这个',
          '我的意思不是这样的',
          '推荐其他套餐吧',
          "这个畅游包是办理的时候扣费吗？",
          "上个月的开销是多少",
          "介绍一下畅游包",
          "我想了解一下最新的套餐",
          "套餐什么内容",
          "剩余多少流量",
          "费用多少",
          "怎么开通",
          "怎么开通？",
          "不是，我是问怎么办理",
          "都有什么",
          "都有啥",
          "主要有些什么",
          "有什么",
          "来个便宜的套餐",
          "来一个便宜的套餐",
          "换一个",
          "换个套餐",
          "推荐个别的"
          ]
    for s in ss:
        print(s, model.get_user_act_results(s))