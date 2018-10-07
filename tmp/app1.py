from flask import Flask, jsonify, request
import tensorflow as tf
from scipy import misc
from PIL import Image
import numpy as np
from sklearn.externals import joblib
from sklearn import multilayer_perceptron

app = Flask(__name__)

#def predict():


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    im = misc.imread(f)
    img = im.reshape((1,784))
    softmax_m = joblib.load('softmax_model.m')
    pred = softmax_m.predict(img)
    #sess = tf.Session()
    # define model
    #x = tf.placeholder(tf.float32, [None, 784])
    #i = np.array([1 - flatten_img])
    #W = tf.Variable(tf.zeros([784, 10]))
    #b = tf.Variable(tf.zeros([10]))
    #y = tf.nn.softmax(tf.matmul(x, W) + b)
    #saver = tf.train.Saver([W, b])
    # restore model
    #saver.restore(sess, "model/")
    # predict by model
    #ret = sess.run(y, feed_dict = {x : img})
    #prediction = ret.argmax()
    return 'The number is %s' % (pred[0])

@app.route('/')
def index():
	return '''
	<!doctype html>
	<html>
	<body>
	<form action='/upload' method='post' enctype='multipart/form-data'>
  		<input type='file' name='file'>
	        <input type='submit' value='Upload'>
	</form>
	'''    
if __name__ == '__main__':
	app.run()

    
