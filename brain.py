import numpy as np
import cv2
from scipy import ndimage
from time import time
from functools import wraps

from utils.config import Config
from model import ICNet, ICNet_BN

model_config = {'train': ICNet, 'trainval': ICNet, 'train_bn': ICNet_BN, 'trainval_bn': ICNet_BN, 'others': ICNet_BN}

# Choose dataset here, but remember to use `script/downlaod_weight.py` first
dataset = 'cityscapes'
filter_scale = 1

SIZE_WEBOT = (64, 128, 3)
SIZE_HD = (1080,1920, 3)


def timer(func):
    @wraps(func)
    def wrapper(instance, *args, **kwargs):
        start_time = time()
        result = func(instance, *args, **kwargs)
        instance.cycle_time = time() - start_time
        if instance.average_cycle_time is None:
            instance.average_cycle_time = instance.cycle_time
        instance.average_cycle_time = instance.average_cycle_time * 0.95 + instance.cycle_time * 0.05
        return result
    return wrapper


class Brain:
    class InferenceConfig(Config):
        def __init__(self, dataset, is_training, filter_scale):
            Config.__init__(self, dataset, is_training, filter_scale)
        model_type = 'trainval'
        model_weight = './model/cityscapes/icnet_cityscapes_train_30k.npy'

    def __init__(self, inner_size=SIZE_HD, exponential_filter_alpha=0.9):
        self.last_theta = 0
        self.alpha = exponential_filter_alpha
        self.cycle_time = None
        self.average_cycle_time = None

        print('Configuring Brain')
        self.cfg = Brain.InferenceConfig(dataset, is_training=False, filter_scale=filter_scale)
        self.cfg.INFER_SIZE = inner_size
        self.cfg.display()

        print('Creating Model Graph')
        self.model = model_config[self.cfg.model_type]
        self.net = self.model(cfg=self.cfg, mode='inference')

        print('Loading Network')
        self.net.create_session()
        self.net.restore(self.cfg.model_weight)

    def exp_filter(self, theta):
        self.last_theta = self.last_theta * (1.0 - self.alpha) + theta * self.alpha
        return self.last_theta

    @timer
    def process(self, image, smooth_result=False):
        if image.shape != self.cfg.INFER_SIZE:
            print('[WARNING]: Image not in the correct size. Resizing...')
            image = cv2.resize(image, (self.cfg.INFER_SIZE[1], self.cfg.INFER_SIZE[0]))

        ##############################
        results1 = self.net.predict(image)
        a = results1[0].copy() / 255
        # my_im1 = image.copy()
        a[a[:, :, 0] > 0.502] = 0
        a[a[:, :, 0] < 0.501] = 0

        a[a[:, :, 1] > 0.26] = 0
        a[a[:, :, 1] < 0.24] = 0

        a[a[:, :, 2] > 0.502] = 0
        a[a[:, :, 2] < 0.501] = 0
        c = ndimage.measurements.center_of_mass(a)
        theta = (np.arctan2((int(c[0]) - image.shape[0]), (int(c[1]) - int(image.shape[1] / 2))) / np.pi) * 180
        theta = (theta + 90) / 90
        ##############################

        if smooth_result:
            return self.exp_filter(theta)
        return theta
