#from test import model_rest
from ast import arg
import numpy as np
import seaborn as sns
from keras.preprocessing import image
import cv2
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd
from tensorflow.keras import backend as K
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.applications.resnet import ResNet50
from tensorflow.keras.applications.resnet import decode_predictions
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras import optimizers
from tensorflow.keras.optimizers import Adam
from skimage.io import imread
import tensorflow as tf
import numpy as np
import keras
import json
import cv2
import os
from tensorflow import keras
import matplotlib.cm as cm
import tensorflow as tf
import matplotlib.pyplot as plt
from IPython.display import Image, display
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
def model_rest(): 
    # create the base pre-trained model
    base_model = ResNet50(include_top=False, weights='imagenet' )
    # add a global spatial average pooling layer
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    # let's add a fully-connected layer
    x = Dense(64, activation='relu')(x)
    x = Dropout(0.3)(x)
    # and a logistic layer 
    predictions = Dense(1, activation='sigmoid')(x)
    
    # this is the model we will train
    base_model = Model(inputs=base_model.input, outputs=predictions)
    
    optimizer = Adam(lr=0.001)
    base_model.compile(loss='binary_crossentropy', 
              optimizer=optimizer, 
              metrics=["accuracy"])
    
    return base_model
img_path = r'/home/fit/Videos/New_RawAC-20220309T024233Z-001/New_RawAC/3 OP/croped_circle.jpg'
img=mpimg.imread(img_path)
plt.imshow(img)

img = image.load_img(img_path, target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

# load model
model=model_rest()
filepath='weights/resnet50.hdf5'
model.load_weights(filepath)

preds = model.predict(x)
from tensorflow.keras.applications.resnet import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import os

#os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
#model = ResNet50(weights='imagenet')
def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    # First, we create a model that maps the input image to the activations
    # of the last conv layer as well as the output predictions
    grad_model = tf.keras.models.Model(
        [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
    )

    # Then, we compute the gradient of the top predicted class for our input image
    # with respect to the activations of the last conv layer
    with tf.GradientTape() as tape:
        last_conv_layer_output, preds = grad_model(img_array)
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]

    # This is the gradient of the output neuron (top predicted or chosen)
    # with regard to the output feature map of the last conv layer
    grads = tape.gradient(class_channel, last_conv_layer_output)

    # This is a vector where each entry is the mean intensity of the gradient
    # over a specific feature map channel
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # We multiply each channel in the feature map array
    # by "how important this channel is" with regard to the top predicted class
    # then sum all the channels to obtain the heatmap class activation
    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # For visualization purpose, we will also normalize the heatmap between 0 & 1
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()
def save_and_display_gradcam(img_path, heatmap, cam_path="cam.jpg", alpha=0.4):
    # Load the original image
    img = keras.preprocessing.image.load_img(img_path)
    img = keras.preprocessing.image.img_to_array(img)

    # Rescale heatmap to a range 0-255
    heatmap = np.uint8(255 * heatmap)

    # Use jet colormap to colorize heatmap
    jet = cm.get_cmap("jet")

    # Use RGB values of the colormap
    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]

    # Create an image with RGB colorized heatmap
    jet_heatmap = keras.preprocessing.image.array_to_img(jet_heatmap)
    jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
    jet_heatmap = keras.preprocessing.image.img_to_array(jet_heatmap)

    # Superimpose the heatmap on original image
    superimposed_img = jet_heatmap * alpha + img
    superimposed_img = keras.preprocessing.image.array_to_img(superimposed_img)

    # Save the superimposed image
    superimposed_img.save(cam_path)

    # Display Grad CAM
    display(Image(cam_path))

img_path = '/home/fit/Videos/New_RawAC-20220309T024233Z-001/New_RawAC/0 VEN/croped_circle.jpg'
#mg_path1 = '/home/fit/Videos/New_RawAC-20220309T024233Z-001/New_RawAC/0 VEN/croped_circle122123123.jpg'
img = image.load_img(img_path, target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
x = preprocess_input(x)

last_conv_layer_name = 'conv5_block3_3_conv'
heatmap = make_gradcam_heatmap(x, model, last_conv_layer_name)
save_and_display_gradcam(img_path, heatmap)

# Display heatmap
plt.matshow(heatmap)
plt.show()