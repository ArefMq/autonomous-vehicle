from utils import emergency_stop


class EmergencyManager:
    def __init__(self, driver):
        self.halt = False
        self.driver = driver

    def engage(self):
        self.halt = True
        emergency_stop(self.driver)

