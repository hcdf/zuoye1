import sys
import tensorflow as tf
from flask import Flask, request
from PIL import Image, ImageFilter
from redis import Redis, RedisError
import os
import socket
import cassandra_mnist

# Connect to Redis
redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)

### Model Setup
x = tf.placeholder(tf.float32, [None, 784])
W = tf.Variable(tf.zeros([784, 10]))
b = tf.Variable(tf.zeros([10]))
y = tf.nn.softmax(tf.matmul(x, W) + b)
init = tf.global_variables_initializer()
saver = tf.train.Saver()
sess = tf.Session()
sess.run(init)
saver.restore(sess, "model4/model")
##############

@app.route("/prediction", methods=['GET','POST'])
def predictint():
    imname = request.files["file"]   #Input
    imvalu = prepareImage(imname)
    prediction = tf.argmax(y,1)
    pred = prediction.eval(feed_dict={x: [imvalu]}, session=sess)
    return "The number is: %s" % str(pred[0])
    insertData(1, imname, str(pred[0]))

def prepareImage(i):
    im = Image.open(i).convert('L')
    width = float(im.size[0])
    height = float(im.size[1])
    newImage = Image.new('L', (28, 28), (255)) #creates white canvas of 28x28 pixels
    
    if width > height: #check which dimension is bigger
        #Width is bigger. Width becomes 20 pixels.
        nheight = int(round((20.0/width*height),0)) #resize height according to ratio width
        if (nheight == 0): #rare case but minimum is 1 pixel
            nheight = 1
        # resize and sharpen
        img = im.resize((20,nheight), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
        wtop = int(round(((28 - nheight)/2),0)) #caculate horizontal pozition
        newImage.paste(img, (4, wtop)) #paste resized image on white canvas
    else:
        #Height is bigger. Height becomes 20 pixels. 
        nwidth = int(round((20.0/height*width),0)) #resize width according to ratio height
        if (nwidth == 0): #rare case but minimum is 1 pixel
            nwidth = 1
         # resize and sharpen
        img = im.resize((nwidth,20), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
        wleft = int(round(((28 - nwidth)/2),0)) #caculate vertical pozition
        newImage.paste(img, (wleft, 4)) #paste resized image on white canvas
    
    tv = list(newImage.getdata()) #get pixel values
    
    #normalize pixels to 0 and 1. 0 is pure white, 1 is pure black.
    tva = [ (255-x)*1.0/255.0 for x in tv] 
    return tva  # Vector of values

@app.route('/')
def index():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    html = '''
	<!doctype html>
	<html>
	<body>
	<form action='/prediction' method='post' enctype='multipart/form-data'>
  		<input type='file' name='file'>
	<input type='submit' value='Upload'>
	</form>
	'''   
    return html.format(name=os.getenv("NAME", "MNIST"), hostname=socket.gethostname(), visits=visits) 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9042)

