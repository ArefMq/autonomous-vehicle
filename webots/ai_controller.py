import numpy as np

# from hamidreza import hamid_process


class Controller:
    def __init__(self, driver):
        self.light_settings = None
        self.driver = driver
        self.desired_speed = 0
        self.desired_angle = 0

        self.lidar = driver.getLidar('Sick LMS 291')
        self.camera = driver.getCamera('camera')
        self.gps = driver.getGPS('gps')
        self.gyro = driver.getGyro('gyro')
        self.display = driver.getDisplay('display')

        self.cvx = CVX()

    def initialize(self):
        self.driver.setSteeringAngle(0.0)
        self.driver.setCruisingSpeed(self.desired_speed)
        self.camera.enable(50)
        self.cvx.set_camera(self.camera)

    def get_light_settings(self):
        return self.light_settings

    def get_image(self):
        raw_image = self.camera.getImage()
        w = self.camera.getWidth()
        h = self.camera.getHeight()

        result = np.zeros([w, h, 3])
        for x in range(w):
            for y in range(h):
                result[x, y, 0] = ord(raw_image[y * w * 3 + x * 3 + 0])
                result[x, y, 1] = ord(raw_image[y * w * 3 + x * 3 + 1])
                result[x, y, 2] = ord(raw_image[y * w * 3 + x * 3 + 2])

        return result

    def apply(self):
        # apply acc
        self.driver.setCruisingSpeed(self.desired_speed)
        # brake if we need to reduce the desired_speed
        speed_diff = self.driver.getCurrentSpeed() - self.desired_speed
        if speed_diff > 0:
            if self.desired_speed > 0:
                self.driver.setBrakeIntensity(min(speed_diff / self.desired_speed, 1))
            else:
                self.driver.setBrakeIntensity(1)
        else:
            self.driver.setBrakeIntensity(0)

        # apply steering
        # self.desired_angle = hamid_process(self.get_image())
        print self.desired_angle
        self.driver.setSteeringAngle(self.desired_angle)

    def cycle(self):
        self.apply()


class ControllerException(Exception):
    pass
