# TensorBoxPy3 https://github.com/SMH17/TensorBoxPy3

"""Tests for slim.inception_resnet_v2."""

import tensorflow as tf

from utils.slim_nets import inception


class InceptionTest(tf.test.TestCase):

  def testBuildLogits(self):
    batch_size = 5
    height, width = 299, 299
    num_classes = 1000
    with self.test_session():
      inputs = tf.random_uniform((batch_size, height, width, 3))
      logits, _ = inception.inception_resnet_v2(inputs, num_classes)
      self.assertTrue(logits.op.name.startswith('InceptionResnetV2/Logits'))
      self.assertListEqual(logits.get_shape().as_list(),
                           [batch_size, num_classes])

  def testBuildEndPoints(self):
    batch_size = 5
    height, width = 299, 299
    num_classes = 1000
    with self.test_session():
      inputs = tf.random_uniform((batch_size, height, width, 3))
      _, end_points = inception.inception_resnet_v2(inputs, num_classes)
      self.assertTrue('Logits' in end_points)
      logits = end_points['Logits']
      self.assertListEqual(logits.get_shape().as_list(),
                           [batch_size, num_classes])
      self.assertTrue('AuxLogits' in end_points)
      aux_logits = end_points['AuxLogits']
      self.assertListEqual(aux_logits.get_shape().as_list(),
                           [batch_size, num_classes])
      pre_pool = end_points['PrePool']
      self.assertListEqual(pre_pool.get_shape().as_list(),
                           [batch_size, 8, 8, 1536])

  def testVariablesSetDevice(self):
    batch_size = 5
    height, width = 299, 299
    num_classes = 1000
    with self.test_session():
      inputs = tf.random_uniform((batch_size, height, width, 3))
      # Force all Variables to reside on the device.
      with tf.variable_scope('on_cpu'), tf.device('/cpu:0'):
        inception.inception_resnet_v2(inputs, num_classes)
      with tf.variable_scope('on_gpu'), tf.device('/gpu:0'):
        inception.inception_resnet_v2(inputs, num_classes)
      for v in tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='on_cpu'):
        self.assertDeviceEqual(v.device, '/cpu:0')
      for v in tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope='on_gpu'):
        self.assertDeviceEqual(v.device, '/gpu:0')

  def testHalfSizeImages(self):
    batch_size = 5
    height, width = 150, 150
    num_classes = 1000
    with self.test_session():
      inputs = tf.random_uniform((batch_size, height, width, 3))
      logits, end_points = inception.inception_resnet_v2(inputs, num_classes)
      self.assertTrue(logits.op.name.startswith('InceptionResnetV2/Logits'))
      self.assertListEqual(logits.get_shape().as_list(),
                           [batch_size, num_classes])
      pre_pool = end_points['PrePool']
      self.assertListEqual(pre_pool.get_shape().as_list(),
                           [batch_size, 3, 3, 1536])

  def testUnknownBatchSize(self):
    batch_size = 1
    height, width = 299, 299
    num_classes = 1000
    with self.test_session() as sess:
      inputs = tf.placeholder(tf.float32, (None, height, width, 3))
      logits, _ = inception.inception_resnet_v2(inputs, num_classes)
      self.assertTrue(logits.op.name.startswith('InceptionResnetV2/Logits'))
      self.assertListEqual(logits.get_shape().as_list(),
                           [None, num_classes])
      images = tf.random_uniform((batch_size, height, width, 3))
      sess.run(tf.global_variables_initializer())
      output = sess.run(logits, {inputs: images.eval()})
      self.assertEqual(output.shape, (batch_size, num_classes))

  def testEvaluation(self):
    batch_size = 2
    height, width = 299, 299
    num_classes = 1000
    with self.test_session() as sess:
      eval_inputs = tf.random_uniform((batch_size, height, width, 3))
      logits, _ = inception.inception_resnet_v2(eval_inputs,
                                                num_classes,
                                                is_training=False)
      predictions = tf.argmax(logits, 1)
      sess.run(tf.global_variables_initializer())
      output = sess.run(predictions)
      self.assertEqual(output.shape, (batch_size,))

  def testTrainEvalWithReuse(self):
    train_batch_size = 5
    eval_batch_size = 2
    height, width = 150, 150
    num_classes = 1000
    with self.test_session() as sess:
      train_inputs = tf.random_uniform((train_batch_size, height, width, 3))
      inception.inception_resnet_v2(train_inputs, num_classes)
      eval_inputs = tf.random_uniform((eval_batch_size, height, width, 3))
      logits, _ = inception.inception_resnet_v2(eval_inputs,
                                                num_classes,
                                                is_training=False,
                                                reuse=True)
      predictions = tf.argmax(logits, 1)
      sess.run(tf.global_variables_initializer())
      output = sess.run(predictions)
      self.assertEqual(output.shape, (eval_batch_size,))


if __name__ == '__main__':
  tf.test.main()
