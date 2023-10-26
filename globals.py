import configparser
import logging
import os
import sys

from dotenv import load_dotenv


class Shared:
    """_Configuration_

    Args:
        Singleton class for application configuration
    """
    
    load_dotenv()

    appname         = 'lgbattery'
    datadir         = f'{os.getenv("APPDATA")}\\{appname}'
    selected_device = ''
    devices         = []
    systray         = None
    logger          = None
    wait_task       = None
    log_level       = None
    log_file        = None
    level_file      = None

    def init_logging(self):
        rootlogger = logging.getLogger()
        rootlogger.setLevel(logging.WARNING)
        rootlogger.handlers[0].level = logging.WARNING
        
        self.logger = logging.getLogger(Shared.appname)
        self.logger.setLevel(self.log_level)
        if self.log_file == None:
            self.logger.addHandler(logging.StreamHandler(stream=sys.stdout))
        else:
            self.logger.addHandler(logging.FileHandler(f'{self.datadir}\\{self.log_file}'))
        formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
        self.logger.handlers[0].setFormatter(formatter)
        
    def load_prefs(self):
        if not os.path.exists(Shared.datadir):
            os.makedirs(Shared.datadir)
        
        config = configparser.ConfigParser()		
        config.read(f'{self.datadir}\\config.ini')
        prefs = None
        if 'PREFS' in config:
            prefs = config['PREFS']
            
        if prefs != None:
            if 'selected_device' in prefs:
                self.selected_device = prefs['selected_device']

            if 'level_file' in prefs:
                self.level_file = prefs['level_file']

            if 'log_file' in prefs:
                self.log_file = prefs['log_file']
            
            self.log_level = logging.WARNING
            
            if 'log_level' in prefs:
                switch = {
                    'DEBUG':logging.DEBUG,
                    'INFO':logging.INFO,
                    'WARNING':logging.WARNING,
                    'ERROR':logging.ERROR,
                    'CRITICAL':logging.CRITICAL
                }
                self.log_level = switch.get(prefs['log_level'].upper(), "Invalid")


    def save_prefs(self):
        config = configparser.ConfigParser()
        
        if not config.has_section('PREFS'):
            config.add_section('PREFS')
        
        config.set('PREFS', 'selected_device', self.selected_device)

        if self.level_file != None:
            config.set('PREFS', 'level_file', self.level_file)

        if self.log_file != None:
            config.set('PREFS', 'log_file', self.log_file)

        switch = {
            logging.DEBUG:'DEBUG',
            logging.INFO:'INFO',
            logging.WARNING:'WARNING',
            logging.ERROR:'ERROR',
            logging.CRITICAL:'CRITICAL'
        }
        log_level = switch.get(self.log_level, "Invalid")
        config.set('PREFS', 'log_level', log_level)
        
        with open(f'{self.datadir}\\config.ini', 'w') as configfile:
            config.write(configfile)

    def refresh_tray(self):
        if self.selected_device == '' or len(self.devices) == 0:
            return None
        
        for dev in self.devices:
            if dev.id == self.selected_device:
                dev.select(self.systray)
    
Shared = Shared()