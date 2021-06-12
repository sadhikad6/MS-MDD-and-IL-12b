# -*- coding: utf-8 -*-
"""CNN_MDD.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ejs09VOK9Sf4-AvIIAhazmiQTk0n1jJG
"""

!pip install PyDrive
import os

#create connection between colab and drive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials

#Authenticate and create the pydrive client
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
#gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

#mount the google drive
from google.colab import drive
drive.mount('/content/gdrive')

PATH_OF_DATA='/content/gdrive/"My Drive"/"Neuroscience/CNN/Data/MDD/"/'
!ls {PATH_OF_DATA}

import torch
import numpy as np
import torchvision.transforms as transforms
import torch.utils.data as utils_data

import torchvision
import torchvision.transforms as transforms
from torchvision import datasets

data_transforms = transforms.Compose([
                                      transforms.Resize(1048),
                                      transforms.CenterCrop(1048),
                                      transforms.ToTensor()])

image_datasets = datasets.ImageFolder(root= "/content/gdrive/My Drive/Neuroscience/CNN/Data/MDD/Train", transform=data_transforms)

dataloaders = torch.utils.data.DataLoader(image_datasets, batch_size=32, shuffle=True, num_workers=2)

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
# %matplotlib inline

# helper function to un-normalize and display an image
def imshow(img):
  img = img / 2 + 0.5 # unnormalize
  plt.imshow(np.transpose(img, (1, 2, 0))) # convert from Tensor image


dataiter = iter(dataloaders)
images, labels = dataiter.next()
images = images.numpy()

# plot the images in the batch, along with the corresponding labels
fig = plt.figure(figsize=(25, 4))
# display 20 images
for idx in np.arange(20):
  ax = fig.add_subplot(2, 20/2, idx+1, xticks=[], yticks=[])
  imshow(images[idx])

from tensorflow.keras.preprocessing.image import ImageDataGenerator

# All images will be rescaled by 1./255
# train_datagen = ImageDataGenerator(rescale=1/255, vertical_flip=True, horizontal_flip=True)

train_datagen = ImageDataGenerator(
    width_shift_range= 0.2, height_shift_range= 0.2,
    rotation_range= 90, rescale = 1/255,
    horizontal_flip= True, vertical_flip=True)

# Flow training images in batches using train_datagen generator
train_generator = train_datagen.flow_from_directory(
    '/content/gdrive/My Drive/Neuroscience/CNN/Data/MDD/Train/', # This is the source directory for training images
    target_size=(256, 256), # All images will be resized
    batch_size=32,
    # Specify the classes explicitly
    classes = ['Healthy', 'MDD'],
    # Since we use categorical_crossentropy loss, we need categorical labels
    class_mode='categorical')

test_datagen = ImageDataGenerator(rescale=1./255, vertical_flip=True, horizontal_flip=True)
validation_generator = train_datagen.flow_from_directory(
    '/content/gdrive/My Drive/Neuroscience/CNN/Data/MDD/Valid/',
    target_size=(256, 256),
    batch_size=32,
    classes = ['Healthy', 'MDD'],
    # Since we use categorical_crossentropy loss, we need categorical labels
    class_mode='categorical')

import tensorflow as tf

model = tf.keras.models.Sequential([
                                    # Note the input shape is the desired size
                                    # The first convolution
                                    tf.keras.layers.Conv2D(16, (3, 3), activation='relu', input_shape=(256, 256, 3)),
                                    tf.keras.layers.BatchNormalization(),
                                    tf.keras.layers.MaxPooling2D(2, 2),
                                    # The second convolution
                                    tf.keras.layers.Conv2D(32, (3,3), activation='relu'),
                                    tf.keras.layers.BatchNormalization(),
                                    tf.keras.layers.MaxPooling2D(2, 2),
                                    # The third convolution
                                    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                                    tf.keras.layers.BatchNormalization(),
                                    tf.keras.layers.MaxPooling2D(2, 2),
                                    # The fourth convolution
                                    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                                    tf.keras.layers.BatchNormalization(),
                                    tf.keras.layers.MaxPooling2D(2, 2),
                                    # The fifth convolution
                                    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                                    tf.keras.layers.BatchNormalization(),
                                    tf.keras.layers.MaxPooling2D(2, 2),
                                    # Flatten the results to feed into a dense layer
                                    tf.keras.layers.Flatten(),
                                    # 128 neuron in the fully-connected layer
                                    tf.keras.layers.BatchNormalization(),
                                    tf.keras.layers.Dense(128, activation='relu'),
                                    # 2 output neurons for 2 classes
                                    tf.keras.layers.Dense(2, activation='softmax')
])

model.summary()

from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.optimizers import Adam




model.compile(loss='categorical_crossentropy',
              #optimizer=RMSprop(1r=0.001),
              optimizer=Adam(lr=0.001),
              metrics=['acc'])

total_sample=train_generator.n
total_valid=validation_generator.n

print(total_sample)
print(total_valid)

n_epochs = 10

history = model.fit_generator(
    train_generator,
    steps_per_epoch=int(total_sample/32),
    #steps_per_epoch=20
    epochs=n_epochs,
    validation_data=validation_generator,
    validation_steps=int(total_valid/32),
    verbose=1)

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
# %matplotlib inline
plt.figure(figsize=(7,4))
plt.plot([i+1 for i in range(n_epochs)], history.history['acc'], '-o', c='k', lw=2, markersize=9)
plt.grid(True)
plt.title("Model accuracy with epochs\n", fontsize=18)
plt.xlabel("Model epochs",fontsize=15)
plt.ylabel("Model accuracy",fontsize=15)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.show()

plt.figure(figsize=(7,4))
plt.plot([i+1 for i in range(n_epochs)],history.history['loss'],'-o',c='k',lw=2,markersize=9)
plt.grid(True)
plt.title("Model loss with epochs\n", fontsize=18)
plt.xlabel("Model epochs",fontsize=15)
plt.ylabel("Model loss",fontsize=15)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.show()

model.save('fullmodel1.h5')

from keras.layers import Dense, Dropout, Flatten, Input, ZeroPadding2D
from keras.layers.normalization import BatchNormalization
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from keras.preprocessing import image
from keras.utils import plot_model
from keras.models import Model
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import Conv2D
from keras.layers.pooling import MaxPooling2D
from numpy import array
from keras import regularizers
from keras import optimizers
from keras.models import load_model
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from PIL import ImageFile

visible = Input(shape=(256,256,3))
conv1 = Conv2D(16, kernel_size=(3,3), activation='relu', strides=(1, 1))(visible)
conv2 = Conv2D(16, kernel_size=(3,3), activation='relu', strides=(1, 1))(conv1)
bat1 = BatchNormalization()(conv2)
zero1 = ZeroPadding2D(padding=(1, 1))(bat1)

conv3 = Conv2D(32, kernel_size=(3,3), activation='relu', padding='valid', kernel_regularizer=regularizers.l2(0.05))(zero1)
conv4 = Conv2D(32, kernel_size=(3,3), activation='relu', padding='valid', kernel_regularizer=regularizers.l2(0.05))(conv3)
bat2 = BatchNormalization()(conv4)

conv5 = Conv2D(64, kernel_size=(3,3), activation='relu', strides=(1, 1), padding='valid')(bat2)
conv6 = Conv2D(64, kernel_size=(3,3), activation='relu', strides=(1, 1), padding='valid')(conv5)
bat3 = BatchNormalization()(conv6)
pool1 = MaxPooling2D(pool_size=(2, 2))(bat3)
zero2 = ZeroPadding2D(padding=(1, 1))(pool1)

conv7 = Conv2D(128, kernel_size=(3,3), activation='relu', padding='valid', kernel_regularizer=regularizers.l2(0.01))(zero2)
conv8 = Conv2D(64, kernel_size=(2,2), activation='relu', strides=(1, 1), padding='valid')(conv7)
bat4 = BatchNormalization()(conv8)

conv9 = Conv2D(64, kernel_size=(3,3), activation='relu', padding='valid', kernel_regularizer=regularizers.l2(0.02))(bat4)
conv10 = Conv2D(64, kernel_size=(3,3), activation='relu', padding='valid', kernel_regularizer=regularizers.l2(0.02))(conv9)
bat5 = BatchNormalization()(conv10)

conv11 = Conv2D(64, kernel_size=(3,3), activation='relu', strides=(1, 1))(bat5)
conv12 = Conv2D(64, kernel_size=(3,3), activation='relu', strides=(1, 1))(conv11)
bat6 = BatchNormalization()(conv12)
pool2 = MaxPooling2D(pool_size=(2, 2))(bat6)

conv13 = Conv2D(64, kernel_size=(3,3), activation='relu', padding='valid', kernel_regularizer=regularizers.l2(0.02))(pool2)
conv14 = Conv2D(64, kernel_size=(3,3), activation='relu', padding='valid', kernel_regularizer=regularizers.l2(0.02))(conv13)
bat7 = BatchNormalization()(conv14)

conv15 = Conv2D(128, kernel_size=(3,3), activation='relu', padding='valid', kernel_regularizer=regularizers.l2(0.05))(bat7)
conv16 = Conv2D(128, kernel_size=(2,2), activation='relu', strides=(1, 1), padding='valid')(conv15)
bat8 = BatchNormalization()(conv16)

flat = Flatten()(bat8)
hidden1 = Dense(32, activation='relu')(flat)
drop1 = Dropout(0.3)(hidden1)

hidden2 = Dense(32, activation='relu')(drop1)
drop2 = Dropout(0.2)(hidden2)

output = Dense(2, activation='sigmoid')(drop2)
model_ver_1 = Model(inputs=visible, outputs=output)

opt = optimizers.Adam()

model_ver_1.compile(optimizer= opt,
                    loss = 'binary_crossentropy',
                    metrics=['accuracy'])

Callbacks=[EarlyStopping(patience=3, restore_best_weights=True),
           ReduceLROnPlateau(patience=2),
           ModelCheckpoint(filepath='ImageDataGen_Size256_oneHOT_ClassWeights_Callbacks_adam_L2.h5', save_best_only=True)]

model_ver_1.summary()

m1 = model_ver_1.fit_generator(
    train_generator,
    epochs=10,
    validation_data=validation_generator,
    callbacks=Callbacks,
    verbose=1)

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
# %matplotlib inline
plt.figure(figsize=(7,4))
plt.plot([i+1 for i in range(10)], m1.history['accuracy'], '-o', c='k', lw=2, markersize=9)
plt.grid(True)
plt.title("Model accuracy with epochs\n", fontsize=18)
plt.xlabel("Model epochs",fontsize=15)
plt.ylabel("Model accuracy",fontsize=15)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.show()

plt.figure(figsize=(7,4))
plt.plot([i+1 for i in range(10)],m1.history['loss'],'-o',c='k',lw=2,markersize=9)
plt.grid(True)
plt.title("Model loss with epochs\n", fontsize=18)
plt.xlabel("Model epochs",fontsize=15)
plt.ylabel("Model loss",fontsize=15)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.show()