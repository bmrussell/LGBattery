import configparser
import logging
import os
import sys

from dotenv import load_dotenv

APPNAME = 'lgbattery'
DATADIR = f'{os.getenv("APPDATA")}\\{APPNAME}'
LOG_LEVEL = "DEBUG"
LOG_FILE = None
SELECTED_DEVICE_NAME = None
logger = None

def init_logging():
    global logger
    
    # Set the default logging level to WARNING for the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level=logging.WARNING)    
    
    # Create a console handler with the specified log level
    logger = logging.getLogger(APPNAME)
    logger.setLevel(LOG_LEVEL)
    
    # Clear any existing handlers to prevent duplicate logging
    if logger.hasHandlers():
        logger.handlers.clear()
        
    # Stop duplicate output from the root logger
    logger.propagate = False
    
    # Set up console logging
    stdio_handler = logging.StreamHandler()        
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(funcName)s | line %(lineno)d | %(message)s')
    stdio_handler.setFormatter(formatter)
    logger.addHandler(stdio_handler)

    # Set up file logging if LOG_FILE is specified
    if LOG_FILE != None:
        file_handler = logging.FileHandler(f'{DATADIR}\\{LOG_FILE}')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
        
def load_prefs():
    global DATADIR, LOG_LEVEL, LOG_FILE, SELECTED_DEVICE_NAME, logger
    load_dotenv()
    
    if not os.path.exists(DATADIR):
        os.makedirs(DATADIR)
    
    config = configparser.ConfigParser()		
    config.read(f'{DATADIR}\\config.ini')
    prefs = None
    
    if 'PREFS' in config:
        prefs = config['PREFS']        
    
        if 'SELECTED_DEVICE_NAME' in prefs:
            SELECTED_DEVICE_NAME = prefs['SELECTED_DEVICE_NAME']

        if 'LOG_LEVEL' in prefs:
            switch = {
                'DEBUG':logging.DEBUG,
                'INFO':logging.INFO,
                'WARNING':logging.WARNING,
                'ERROR':logging.ERROR,
                'CRITICAL':logging.CRITICAL
            }
            LOG_LEVEL = switch.get(prefs['LOG_LEVEL'], "Invalid")


        if 'LOG_FILE' in prefs:
            LOG_FILE = prefs['LOG_FILE']
        
    init_logging()
    
def save_prefs():
    global DATADIR, LOG_LEVEL, LOG_FILE, SELECTED_DEVICE_NAME, logger
    
    config = configparser.ConfigParser()
    
    if not config.has_section('PREFS'):
        config.add_section('PREFS')
    
    config.set('PREFS', 'selected_device', SELECTED_DEVICE_NAME)

    if LOG_FILE != None:
        config.set('PREFS', 'LOG_FILE', LOG_FILE)


    switch = {
        logging.DEBUG:'DEBUG',
        logging.INFO:'INFO',
        logging.WARNING:'WARNING',
        logging.ERROR:'ERROR',
        logging.CRITICAL:'CRITICAL'
    }
    level = switch.get(LOG_LEVEL, "Invalid")
    config.set('PREFS', 'LOG_LEVEL', level)
    
    with open(f'{DATADIR}\\config.ini', 'w') as configfile:
        config.write(configfile)

