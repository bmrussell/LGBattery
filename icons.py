import os
import icoextract
import logging
from globals import Shared

def export_icons():

    extractor = icoextract.IconExtractor(
        'C:\\Windows\\SystemResources\\wpdshext.dll.mun')

    percents = ['00-20', '21-40', '41-60', '61-80', '81-100', 'unknown']
    for x in range(9, 15):
        iconfile = f'{Shared.datadir}\\battery-{percents[x-9]}.ico'
        if not os.path.exists(iconfile):
            extractor.export_icon(iconfile, x)

    logger = logging.getLogger(Shared.appname)
    logger.debug("EXPORT_ICONS: Got icons")
    
def get_icon(level):    
    if level >= 0 and level <= 20:
        icon = 'battery-00-20.ico'
    elif level >= 21 and level <= 40:
        icon = 'battery-21-40.ico'
    elif level >= 41 and level <= 60:
        icon = 'battery-41-60.ico'
    elif level >= 61 and level <= 80:
        icon = 'battery-61-80.ico'
    elif level >= 81 and level <= 100:
        icon = 'battery-81-100.ico'
    else:
        icon = 'battery-unknown.ico'
    return f"{Shared.datadir}\\{icon}"