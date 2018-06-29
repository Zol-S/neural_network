from keras import backend as K
from keras.datasets import mnist
from keras.models import Sequential, load_model

from sklearn import preprocessing

import cv2
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

K.set_learning_phase(1)

img_rows, img_cols = 28, 28

# Loading model
model = load_model('mnist_28x28_percent98.96.h5')

layer_dict = dict([(layer.name, layer) for layer in model.layers])
#print('Layer dict', layer_dict)
#print(model.summary())

# util function to convert a tensor into a valid image
def deprocess_image(x):
	# normalize tensor: center on 0., ensure std is 0.1
	x -= x.mean()
	x /= (x.std() + 1e-5)
	x *= 0.1

	# clip to [0, 1]
	x += 0.5
	x = np.clip(x, 0, 1)

	# convert to RGB array
	x *= 255
	#x = x.transpose((1, 2, 0))
	x = np.clip(x, 0, 255).astype('uint8')
	return x

def vis_img_in_filter(img, layer_name = 'conv2d_2'):
	layer_output = layer_dict[layer_name].output
	img_ascs = list()
	for filter_index in range(layer_output.shape[3]):
		# build a loss function that maximizes the activation
		# of the nth filter of the layer considered
		loss = K.mean(layer_output[:, :, :, filter_index])

		# compute the gradient of the input picture wrt this loss
		grads = K.gradients(loss, model.input)[0]

		# normalization trick: we normalize the gradient
		grads /= (K.sqrt(K.mean(K.square(grads))) + 1e-5)

		# this function returns the loss and grads given the input picture
		iterate = K.function([model.input], [loss, grads])

		# step size for gradient ascent
		step = 5.

		img_asc = np.array(img)
		# run gradient ascent for 20 steps
		for i in range(20):
			loss_value, grads_value = iterate([img_asc])
			img_asc += grads_value * step

		img_asc = img_asc[0]
		img_ascs.append(deprocess_image(img_asc).reshape((28, 28)))
		
	if layer_output.shape[3] >= 35:
		plot_x, plot_y = 6, 6
	elif layer_output.shape[3] >= 23:
		plot_x, plot_y = 4, 6
	elif layer_output.shape[3] >= 11:
		plot_x, plot_y = 2, 6
	else:
		plot_x, plot_y = 1, 2
	fig, ax = plt.subplots(plot_x, plot_y, figsize = (12, 12))
	ax[0, 0].imshow(img.reshape((28, 28)), cmap = 'gray')
	ax[0, 0].set_title('Input image')
	fig.suptitle('Input image and %s filters' % (layer_name,))
	fig.tight_layout(pad = 0.3, rect = [0, 0, 0.9, 0.9])
	for (x, y) in [(i, j) for i in range(plot_x) for j in range(plot_y)]:
		if x == 0 and y == 0:
			continue
		ax[x, y].imshow(img_ascs[x * plot_y + y - 1], cmap = 'gray')
		ax[x, y].set_title('filter %d' % (x * plot_y + y - 1))

img_face = cv2.imread("images/face_grayscale_small.jpg", cv2.IMREAD_GRAYSCALE).flatten()
img_face = np.divide(img_face, 255).reshape(1, 28, 28, 1)

vis_img_in_filter(img_face)
plt.show()
