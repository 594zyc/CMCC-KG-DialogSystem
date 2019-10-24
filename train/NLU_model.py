import tensorflow as tf
tf.set_random_seed(123)

max_sent_len = 30

# EDST is suitable for attrs, values

class EDST:
    def __init__(self, name,
                 max_sent_length=max_sent_len,
                 word_embed_size=300,
                 output_size=2,
                 word_feature_map=10, # window 1,2,3,
                 learning_rate = 0.001
                 ):
        self.name = name
        with tf.variable_scope(name_or_scope=self.name,
                            initializer=tf.truncated_normal_initializer(0, 0.01)):

            self.input_emb = tf.placeholder(dtype=tf.float32,
                                             shape=[None, max_sent_length, word_embed_size])
            self.input_match = tf.placeholder(dtype=tf.float32,
                                             shape=[None, max_sent_length])
            self.input_value = tf.placeholder(dtype=tf.float32,
                                              shape=[None, word_embed_size])
            self.specific = tf.einsum('ijk,ik->ij', self.input_emb, self.input_value)
            self.input = tf.concat([self.input_emb,
                                    tf.expand_dims(self.input_match, 2),
                                    tf.expand_dims(self.specific, 2),
                                    ], 2)
            # print(self.input)
            self.output = tf.placeholder(dtype=tf.int32, shape=[None])
            self.batch_size = tf.shape(self.input_emb)[0]

            def conv_relu(inputs, filters, kernel, poolsize):
                conv = tf.layers.conv1d(
                    inputs=inputs,
                    filters=filters,
                    kernel_size=kernel,
                    strides=1,
                    padding='same',
                    activation=tf.nn.relu,
                    kernel_initializer=tf.random_normal_initializer(0, 0.01)
                )
                # print('conv:', conv.get_shape())
                pool = tf.layers.max_pooling1d(
                    inputs=conv,
                    pool_size=poolsize,
                    strides=1,
                )
                # print('pool:', pool.get_shape())
                _pool = tf.squeeze(pool, [1])
                # print('_pool:', _pool.get_shape())
                return _pool
            def cnn(inputs, maxlength):
                with tf.variable_scope("winsize1"):
                    conv2 = conv_relu(inputs, word_feature_map, 1, maxlength)
                with tf.variable_scope("winsize2"):
                    conv3 = conv_relu(inputs, word_feature_map, 2, maxlength)
                with tf.variable_scope("winsize3"):
                    conv4 = conv_relu(inputs, word_feature_map, 3, maxlength)
                return tf.concat([conv2, conv3, conv4], 1)
            with tf.variable_scope("CNN_output"):
                self.feature = cnn(self.input, max_sent_length)
                # print('cnn_output:', self.feature)
            with tf.variable_scope("projection"):
                self.final_output_logits = tf.layers.dense(
                    inputs=self.feature,
                    units=output_size,
                    activation=tf.nn.relu)

                # print(self.final_output_logits.get_shape())

            with tf.variable_scope("loss"):
                self.loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
                    logits=self.final_output_logits,
                    labels=self.output)
                # print(self.loss.get_shape())

            with tf.variable_scope("train"):
                self.tvars = tf.get_collection(key=tf.GraphKeys.GLOBAL_VARIABLES, scope=self.name)
                self.optimizer = tf.train.AdamOptimizer(learning_rate)
                self.l2_loss = [tf.nn.l2_loss(v) for v in self.tvars]
                self.final_loss = tf.reduce_mean(self.loss) + 0.001 * tf.add_n(self.l2_loss)
                self.train_op = self.optimizer.minimize(self.final_loss)
                self.predict = tf.cast(tf.argmax(self.final_output_logits, axis=1), tf.int32)
                self.accu = tf.reduce_mean(tf.cast(tf.equal(self.predict, self.output), tf.float32))

# 简化版 EDST, 使用了相同的 CNN
class CNN:
    def __init__(self, name,
                 max_sent_length=max_sent_len,
                 word_embed_size=300,
                 output_size=9,
                 word_feature_map=10, # window 1,2,3,
                 learning_rate = 0.001
                 ):
        self.name = name
        with tf.variable_scope(name_or_scope=self.name,
                            initializer=tf.truncated_normal_initializer(0, 0.01)):

            self.input = tf.placeholder(dtype=tf.float32,
                                             shape=[None, max_sent_length, word_embed_size])
            self.output = tf.placeholder(dtype=tf.int32, shape=[None])
            self.batch_size = tf.shape(self.input)[0]

            def conv_relu(inputs, filters, kernel, poolsize):
                conv = tf.layers.conv1d(
                    inputs=inputs,
                    filters=filters,
                    kernel_size=kernel,
                    strides=1,
                    padding='same',
                    activation=tf.nn.relu,
                    kernel_initializer=tf.random_normal_initializer(0, 0.01)
                )
                # print('conv:', conv.get_shape())
                pool = tf.layers.max_pooling1d(
                    inputs=conv,
                    pool_size=poolsize,
                    strides=1,
                )
                # print('pool:', pool.get_shape())
                _pool = tf.squeeze(pool, [1])
                # print('_pool:', _pool.get_shape())
                return _pool
            def cnn(inputs, maxlength):
                with tf.variable_scope("winsize1"):
                    conv2 = conv_relu(inputs, word_feature_map, 1, maxlength)
                with tf.variable_scope("winsize2"):
                    conv3 = conv_relu(inputs, word_feature_map, 2, maxlength)
                with tf.variable_scope("winsize3"):
                    conv4 = conv_relu(inputs, word_feature_map, 3, maxlength)
                return tf.concat([conv2, conv3, conv4], 1)
            with tf.variable_scope("CNN_output"):
                self.feature = cnn(self.input, max_sent_length)
                # print('cnn_output:', self.feature)
            with tf.variable_scope("projection"):
                self.final_output_logits = tf.layers.dense(
                    inputs=self.feature,
                    units=output_size,
                    activation=tf.nn.relu)

                # print(self.final_output_logits.get_shape())

            with tf.variable_scope("loss"):
                self.loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
                    logits=self.final_output_logits,
                    labels=self.output)
                # print(self.loss.get_shape())

            with tf.variable_scope("train"):
                self.tvars = tf.get_collection(key=tf.GraphKeys.GLOBAL_VARIABLES, scope=self.name)
                self.optimizer = tf.train.AdamOptimizer(learning_rate)
                self.l2_loss = [tf.nn.l2_loss(v) for v in self.tvars]
                self.final_loss = tf.reduce_mean(self.loss) + 0.001 * tf.add_n(self.l2_loss)
                self.train_op = self.optimizer.minimize(self.final_loss)
                self.predict = tf.cast(tf.argmax(self.final_output_logits, axis=1), tf.int32)
                self.accu = tf.reduce_mean(tf.cast(tf.equal(self.predict, self.output), tf.float32))

class BOW:
    def __init__(self,name,
                 vocab_size=1500,
                 output_size=2,
                 learning_rate=0.3,
                 ):
        self.input_sent = tf.placeholder(dtype=tf.int32,
                                         shape=[None, vocab_size])
        self.output = tf.placeholder(dtype=tf.int32,
                                         shape=[None])
        with tf.variable_scope(name, initializer=tf.truncated_normal_initializer(0, 0.03)):
            self.output_logits = tf.layers.dense(
                inputs=tf.cast(self.input_sent, tf.float32),
                units=output_size
            )
            self.loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
                logits=self.output_logits,
                labels=self.output)
            self.tvars = tf.trainable_variables()
            self.optimizer = tf.train.MomentumOptimizer(learning_rate, 0.9)
            self.l2_loss = [tf.nn.l2_loss(v) for v in self.tvars]
            self.final_loss = tf.reduce_mean(self.loss)  # + 0.001 * tf.add_n(self.l2_loss)
            self.train_op = self.optimizer.minimize(self.final_loss)


            self.predict = tf.argmax(self.output_logits, axis=1)
            # print(self.predict.get_shape())
            self.correct = tf.equal(tf.cast(self.predict, tf.int32),
                                    tf.cast(self.output, tf.int32))
            self.accuracy = tf.reduce_mean(tf.cast(self.correct, tf.float32))


if __name__ == '__main__':
    model = EDST('model')

