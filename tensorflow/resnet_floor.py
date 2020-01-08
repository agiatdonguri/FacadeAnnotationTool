import datetime
import os
from PIL import Image
import numpy
import glob

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.callbacks import TensorBoard, LearningRateScheduler

import resnet


NUM_GPUS = 1
BS_PER_GPU = 64
NUM_EPOCHS = 10

HEIGHT = 96
WIDTH = 96
NUM_CHANNELS = 3
NUM_CLASSES = 1

BASE_LEARNING_RATE = 0.01
LR_SCHEDULE = [(0.1, 30), (0.01, 45)]


def normalize(x, y):
  x = tf.image.per_image_standardization(x)
  return x, y


def augmentation(x, y):
    x = tf.image.resize_with_crop_or_pad(
        x, HEIGHT + 8, WIDTH + 8)
    x = tf.image.random_crop(x, [HEIGHT, WIDTH, NUM_CHANNELS])
    x = tf.image.random_flip_left_right(x)
    return x, y	


def schedule(epoch):
  initial_learning_rate = BASE_LEARNING_RATE * BS_PER_GPU / 128
  learning_rate = initial_learning_rate
  for mult, start_epoch in LR_SCHEDULE:
    if epoch >= start_epoch:
      learning_rate = initial_learning_rate * mult
    else:
      break
  tf.summary.scalar('learning rate', data=learning_rate, step=epoch)
  return learning_rate

def load_img(file_path):
	img = Image.open(file_path)
	img.load()
	img = img.resize((WIDTH, HEIGHT))
	img = numpy.asarray(img, dtype="int32")
	img = img.astype("float")
	return img

def load_annotation(file_path):
	params = {}
	file = open(file_path, "r")
	for line in file.readlines():
		line = line.strip()
		values = []
		data = line.split(',')
		if len(data) > 1:
			for i in range(1,len(data)):
				values.append(float(data[i].strip()))
			params[data[0]] = values
		
	return params


# Load parameters
params = load_annotation("facade_annotation.txt")


# Load images
path_list = glob.glob("../ECP/images/*.jpg")
X = numpy.zeros((len(path_list), WIDTH, HEIGHT, 3), dtype=float)
Y = numpy.zeros((len(path_list)), dtype=float)
i = 0
for file_path in path_list:
	X[i,:,:,:] = load_img(file_path)
	file_name = os.path.basename(file_path)
	Y[i] = max(params[file_name])
	i += 1


# Create tensor from numpy array
X = tf.constant(X)
X = tf.compat.v2.image.per_image_standardization(X)
Y = tf.constant(Y)

# Split the tensor into train and test dataset
num_train = int(len(Y) * 0.8)
num_test = len(Y) - num_train
trainX, testX = tf.split(X, [num_train, num_test], 0)
trainY, testY = tf.split(Y, [num_train, num_test], 0)
print(trainX.shape)
print(testX.shape)


# Build model
input_shape = (HEIGHT, WIDTH, NUM_CHANNELS)
img_input = tf.keras.layers.Input(shape=input_shape)
#opt = keras.optimizers.SGD(learning_rate=0.1, momentum=0.9)
opt = tf.keras.optimizers.RMSprop(0.001)
model = resnet.resnet56(img_input=img_input, classes=NUM_CLASSES)
model.compile(
	optimizer=opt,
	loss='mse',
	metrics=['mae', 'mse'])


# Setup for Tensorboard
log_dir="logs\\fit\\" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
file_writer = tf.summary.create_file_writer(log_dir + "\\metrics")
file_writer.set_as_default()
tensorboard_callback = TensorBoard(
	log_dir=log_dir,
	update_freq='batch',
	histogram_freq=1)


# Training model
lr_schedule_callback = LearningRateScheduler(schedule)
model.fit(trainX, trainY,
	epochs=NUM_EPOCHS,
	validation_split = 0.2,
	callbacks=[tensorboard_callback, lr_schedule_callback])
		  
		  
# Test
model.evaluate(trainX, trainY)
predictedY = model.predict(X).flatten()
print(predictedY)

model.save('model.h5')

#new_model = keras.models.load_model('model.h5')
 
#new_model.evaluate(testX, testY)