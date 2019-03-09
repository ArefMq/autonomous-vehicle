from vehicle import Driver

from webots.ai_controller import Controller, ControllerException
from webots.emergency_man import EmergencyManager
from webots.light_man import LightManager

driver = Driver()
timeStep = int(driver.getBasicTimeStep())

print 'hello'

ctl = Controller(driver)
lm = LightManager(driver)
em = EmergencyManager(driver)


def initialize_all():
    ctl.initialize()


def run():
    while driver.step() != -1:
        print('cycle')
        try:
            if not em.halt:
                # ctl.cycle()
                lm.set_setting(ctl.get_light_settings())
        except ControllerException as exp:
            print(str(exp))
            em.engage()
            lm.set_setting('emergency_flash')
        lm.cycle()


initialize_all()
run()
