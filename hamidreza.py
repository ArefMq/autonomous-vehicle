import numpy as np
import cv2
from scipy import ndimage

from utils.config import Config
from model import ICNet, ICNet_BN

model_config = {'train': ICNet, 'trainval': ICNet, 'train_bn': ICNet_BN, 'trainval_bn': ICNet_BN, 'others': ICNet_BN}

# Choose dataset here, but remember to use `script/downlaod_weight.py` first
dataset = 'cityscapes'
filter_scale = 1


class InferenceConfig(Config):
    def __init__(self, dataset, is_training, filter_scale):
        Config.__init__(self, dataset, is_training, filter_scale)

    # You can choose different model here, see "model_config" dictionary. If you choose "others",
    # it means that you use self-trained model, you need to change "filter_scale" to 2.
    model_type = 'trainval'

    # Set pre-trained weights here (You can download weight from Google Drive)
    model_weight = './model/cityscapes/icnet_cityscapes_train_30k.npy'

    # Define default input size here
    INFER_SIZE = (64, 128, 3)


cfg = InferenceConfig(dataset, is_training=False, filter_scale=filter_scale)
cfg.display()

# Create graph here
model = model_config[cfg.model_type]
net = model(cfg=cfg, mode='inference')

# Create session & restore weight!
net.create_session()
net.restore(cfg.model_weight)


def hamid_process(image):
    if image.shape != cfg.INFER_SIZE:
        image = cv2.resize(image, (cfg.INFER_SIZE[1], cfg.INFER_SIZE[0]))

    results1 = net.predict(image)
    overlap_results1 = 0.5 * image + 0.5 * results1[0]
    ##############################
    a = results1[0].copy() / 255
    # my_im1 = image.copy()
    a[a[:, :, 0] > 0.502] = 0
    a[a[:, :, 0] < 0.501] = 0

    a[a[:, :, 1] > 0.26] = 0
    a[a[:, :, 1] < 0.24] = 0

    a[a[:, :, 2] > 0.502] = 0
    a[a[:, :, 2] < 0.501] = 0
    ##############################
    c = ndimage.measurements.center_of_mass(a)
    # theta = (int(c[0]) - image.shape[0])/(int(c[1])-int(image.shape[1]/2))
    theta = (np.arctan2((int(c[0]) - image.shape[0]), (int(c[1]) - int(image.shape[1] / 2))) / np.pi) * 180
    return (theta + 90) / 90
