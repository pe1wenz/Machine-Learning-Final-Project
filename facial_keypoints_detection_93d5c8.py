# imports
import numpy as np 
import pandas as pd 
import os
import matplotlib.pyplot as plt
from keras.layers.advanced_activations import ReLU
from keras.models import Sequential, Model
from keras.layers import Activation, Convolution2D, MaxPooling2D
from keras.layers import Flatten, Dense, Dropout, Conv2D,MaxPool2D

# io reading
train_data = pd.read_csv('./training.csv',header=0, sep=',', quotechar='"')
test_data = pd.read_csv('./test.csv', header=0, sep=',', quotechar='"')
IdLookupTable = pd.read_csv('./IdLookupTable.csv',header=0, sep=',', quotechar='"')
train_data.fillna(method = 'ffill',inplace = True)


# get x-train and y-train
trainimg = []

for i in range(len(train_data)):
  trainimg.append(train_data['Image'][i].split(' '))


array_float = np.array(trainimg, dtype='float')
X_train = array_float.reshape(-1,96,96,1)


photo_visualize = array_float[1].reshape(96,96)

plt.imshow(photo_visualize, cmap='gray')
plt.title("Visualize Image")
plt.show()


Facial_Keypoints_Data = train_data.drop(['Image'], axis=1)
facial_pnts = []

for i in range(len(Facial_Keypoints_Data)):
  facial_pnts.append(Facial_Keypoints_Data.iloc[i])

training_data = train_data.drop('Image',axis = 1)

y_train = []
for i in range(len(train_data)):
    y = training_data.iloc[i,:]
    y_train.append(y)
    
    
y_train = np.array(y_train,dtype = 'float')

facial_pnts_float = np.array(facial_pnts, dtype='float')


photo_visualize_pnts = Facial_Keypoints_Data.iloc[1].values

plt.imshow(photo_visualize, cmap='gray')
plt.scatter(photo_visualize_pnts[0::2], photo_visualize_pnts[1::2], c='Pink', marker='*')
plt.title("Image with Facial Keypoints")
plt.show()

# build CNN structures

model = Sequential()

model.add(Convolution2D(32, (3,3), padding='same', input_shape=(96,96,1)))
model.add(Activation('relu'))
model.add(MaxPool2D(pool_size=(2, 2)))
model.add(Dropout(0.1))

model.add(Convolution2D(32, (3,3), padding='same'))
model.add(Activation('relu'))
model.add(MaxPool2D(pool_size=(2, 2)))
model.add(Dropout(0.2))

model.add(Convolution2D(64, (3,3), padding='same'))
model.add(Activation('relu'))
model.add(MaxPool2D(pool_size=(2, 2)))
model.add(Dropout(0.2))

model.add(Convolution2D(128, (3,3), padding='same'))
model.add(Activation('relu'))
model.add(MaxPool2D(pool_size=(2, 2)))

model.add(Flatten())
model.add(Dense(256,activation='relu'))
model.add(Dropout(0.3))
model.add(Dense(30))

model.summary()

model.compile(optimizer='adam', 
              loss='mean_squared_error',
              metrics=['accuracy'])

# training
model.fit(X_train,y_train,epochs = 25,batch_size=32,validation_split = 0.2)


test_images = []
for i in range(len(test_data)):
    item = test_data['Image'][i].split(' ')
    test_images.append(item)

array_float_test = np.array(test_images,dtype = 'float')
X_test = array_float_test.reshape(-1,96,96,1)

# predict
predict = model.predict(X_test)
print(predict)


FeatureName = list(IdLookupTable['FeatureName'])
ImageId = list(IdLookupTable['ImageId']-1)
RowId = list(IdLookupTable['RowId'])

predict = list(predict)

Data = []
for i in list(FeatureName):
    Data.append(FeatureName.index(i))
    
    
Data_Pre = []
for x,y in zip(ImageId,Data):
    Data_Pre.append(predict[x][y])
    

RowId = pd.Series(RowId,name = 'RowId')
Location = pd.Series(Data_Pre,name = 'Location')

submission = pd.concat([RowId,Location],axis = 1)
submission.to_csv('./Submit.csv',index=False)

# show test images and predictions.
testvis = []

for i in range(len(test_data)):
  testvis.append(test_data['Image'][i].split(' '))


test_array_float = np.array(testvis, dtype='float')

X_test_pred = test_array_float.reshape(-1,96,96,1)

print(len(test_array_float))

for i in range(100):

  test_photo_visualize = test_array_float[i+1].reshape(96,96)

  plt.imshow(test_photo_visualize, cmap='gray')
  plt.scatter(Data_Pre[i*30:(i+1)*30:2], Data_Pre[(i*30)+1:(i+1)*30:2], c='Pink', marker='*')
  plt.title("Visualize Image")
  plt.show()
