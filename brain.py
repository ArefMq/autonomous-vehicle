import numpy as np
import cv2
import json
import os
from time import time
from scipy import ndimage
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

    class HotReloadConfigs:
        def __init__(self, config_file_path='config.json'):
            self.last_modified = 0
            self.config = None
            self.path = config_file_path
            self.reload()

        def reload(self):
            stat = os.stat(self.path)
            if stat.st_mtime != self.last_modified:
                print 'reloading'
                try:
                    with open(self.path) as f:
                        self.config = json.load(f)
                    self.last_modified = stat.st_mtime
                    return True
                except (IOError, ValueError, KeyError):
                    print('can not reload config')
            return False

        def __getattr__(self, name):
            return self.config[name]

    def __init__(self, inner_size=SIZE_HD, exponential_filter_alpha=0.9):
        self.last_theta = 0
        self.alpha = exponential_filter_alpha
        self.cycle_time = None
        self.average_cycle_time = None
        self.config = Brain.HotReloadConfigs()

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
    def process(self, image):
        if image.shape != self.cfg.INFER_SIZE:
            print('[WARNING]: Image not in the correct size. Resizing...')
            image = cv2.resize(image, (self.cfg.INFER_SIZE[1], self.cfg.INFER_SIZE[0]))

        self.config.reload()
        c = self.run_network(image)

        # calculate theta
        theta = np.arctan2((int(c[0]) - image.shape[0]), (int(c[1]) - int(image.shape[1] / 2)))
        if self.config.output_type == "one_to_one":
            theta = (np.arctan2((int(c[0]) - image.shape[0]), (int(c[1]) - int(image.shape[1] / 2))) / np.pi)
        elif self.config.output_type == "degree":
            theta = (theta / np.pi) * 180.0
            theta = (theta + 90.0) / 90.0
        elif self.config.output_type == "radian":
            pass

        # apply gain and offset
        theta = theta * self.config.gain + self.config.offset

        if self.config.smooth_result:
            return self.exp_filter(theta)
        return theta

    def run_network(self, image):
        results1 = self.net.predict(image)
        a = results1[0].copy() / 255
        a[a[:, :, 0] > 0.502] = 0
        a[a[:, :, 0] < 0.501] = 0
        a[a[:, :, 1] > 0.26] = 0
        a[a[:, :, 1] < 0.24] = 0
        a[a[:, :, 2] > 0.502] = 0
        a[a[:, :, 2] < 0.501] = 0
        c = ndimage.measurements.center_of_mass(a)
        return c
