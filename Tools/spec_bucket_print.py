"""train the model"""

import argparse
import configparser
import logging
import reprlib
import sys
import os
import numpy as np

import tensorflow as tf

sys.path.append("../../../tftools")
from Trainer.InputFn import input_fn

from FCGen import FCGen

def configure(parser):
  parser.add_argument(
    '--conf', type=str, help='param configuration file is requried'
  )

  
def print_feature_sample(key,train_inputs):
  with tf.Session() as sess:
    sess.run(train_inputs['iterator_init_op'])
    next_element = train_inputs['features']
    ##print(next_element)

    sample = sess.run([
        next_element[key],
    ])
    Asample=np.array(sample)
    print(Asample)

    
        
def write_spec(config):
  """Entry for trainig

  Args:
    config: (configparser) All the hyperparameters for training
  """
  train_dir = config['input']['train']
  train_files = [os.path.join(train_dir, f) for f in os.listdir(train_dir) if f != "_SUCCESS"]
  logging.info('train directory: {}'.format(train_dir))
  logging.info('train files: {}'.format(reprlib.repr(train_files)))

  feature_config = configparser.ConfigParser()
  feature_config.read(config['input']['spec'])
  columns, spec = FCGen.GetFeatureSpec(feature_config)

  logging.info("Creating iterators...")
  batch_size = 10
  train_inputs = input_fn(train_files, spec, shuffle=True, batch_size=10)

  # get tfrecods
  num_epochs = 1
  logging.info("Start training for {} epoch(s)".format(num_epochs))

  dict_liner = {}
  for sec in feature_config.sections() :
    info_dict = feature_config[sec]  	
    if sec not in ('label') and info_dict.get('ftype', 'numeric') in ('numeric','bucketized','cat_hash'):
      print(sec+':\n')
      print_feature_sample(info_dict.get('fname', sec),train_inputs)
      print('\n')


if __name__ == '__main__':
  os.environ["CUDA_VISIBLE_DEVICES"] = ""
  logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
  parser = argparse.ArgumentParser()
  configure(parser) 
  FLAGS, _ = parser.parse_known_args()

  config = configparser.ConfigParser()  
  config.read(FLAGS.conf)

  seed = int(config['train'].get('seed', 19910825))
  tf.set_random_seed(seed)

  write_spec(config)
