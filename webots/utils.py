
def emergency_stop(driver):
    driver.setSteeringAngle(0.0)
    driver.setCruisingSpeed(0)


def stop(driver, frame=30):
    driver.setSteeringAngle(0.0)
    driver.setCruisingSpeed(0)


def print_all_devices(r):
    print('---------------------------------------')
    for i in range(r.getNumberOfDevices()):
        print('~ Device:', r.getDeviceByIndex(i).getName(), ' ===> ', r.getDeviceByIndex(i))
    print('---------------------------------------')
