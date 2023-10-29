class BatteryMonitoringError(Exception):
    pass

class UnknownDeviceError(BatteryMonitoringError):
    pass

class GracefulShutdown(BatteryMonitoringError):
    pass
