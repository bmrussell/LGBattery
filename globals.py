import os
import configparser
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
    gameoverman     = False
    lgsocket        = None
    
    def load_prefs(self):
        if not os.path.exists(Shared.datadir):
            os.makedirs(Shared.datadir)
        
        config = configparser.ConfigParser()		
        config.read(f'{self.datadir}\\config.ini')
        if 'PREFS' in config:
            prefs = config['PREFS']
            if prefs != None and prefs['selected_device'] != None:
                self.selected_device = prefs['selected_device']
    
    def save_prefs(self):
        config = configparser.ConfigParser()
        if not config.has_section('PREFS'):
            config.add_section('PREFS')
        config.set('PREFS', 'selected_device', self.selected_device)
        with open(f'{self.datadir}\\config.ini', 'w') as configfile:
            config.write(configfile)
            
Shared = Shared()