
class LightManager:
    def __init__(self, driver):
        self.light_setting = None

        self.front_lights = driver.getLED('front_lights')
        self.right_indicators = driver.getLED('right_indicators')
        self.left_indicators = driver.getLED('left_indicators')
        self.antifog_lights = driver.getLED('antifog_lights')
        self.brake_ligths = driver.getLED('brake_ligths')
        self.rear_lights = driver.getLED('rear_lights')
        self.backwards_lights = driver.getLED('backwards_lights')
        self.interior_right_indicators = driver.getLED('interior_right_indicators')
        self.interior_left_indicators = driver.getLED('interior_left_indicators')

        self.flashing_rate = 30
        self._cycle_counter = 0
        self._current_flash = False

    def set_setting(self, setting):
        if isinstance(setting, str):
            setting = setting.split('|')
        self.light_setting = setting

    def cycle(self):
        if self.light_setting is None:
            return
        self._cycle_flash()

        if 'emergency_flash' in self.light_setting:
            self.front_lights.set(self._current_flash)
            self.rear_lights.set(self._current_flash)
            self.right_indicators.set(self._current_flash)
            self.left_indicators.set(self._current_flash)
            return

        if 'flashers' in self.light_setting:
            self.right_indicators.set(self._current_flash)
            self.left_indicators.set(self._current_flash)
        elif 'right_indc' in self.light_setting:
            self.right_indicators.set(self._current_flash)
        elif 'left_indc' in self.light_setting:
            self.left_indicators.set(self._current_flash)
        else:
            self.right_indicators.set(False)
            self.left_indicators.set(False)

        if 'breaks' in self.light_setting:
            self.brake_ligths(True)
        else:
            self.brake_ligths(False)

        if 'heads' in self.light_setting:
            self.front_lights.set(True)
            self.rear_lights.set(True)
        else:
            self.front_lights.set(False)
            self.rear_lights.set(False)

        if 'fog' in self.light_setting:
            self.antifog_lights(True)
        else:
            self.antifog_lights(False)

    def _cycle_flash(self):
        if self._cycle_counter == self.flashing_rate:
            self._current_flash = not self._current_flash
            self._cycle_counter = 0
        else:
            self._cycle_counter += 1

