# https://pypi.org/project/infi.systray/
# https://pypi.org/project/websockets/
import sys
import time
import os
import json
import asyncio
import logging
import websockets

from logging.config import dictConfig
from infi.systray import SysTrayIcon

from device import Device, get_device
from icons import get_icon, export_icons
from globals import Shared



def quit(tray):
    """Bailing"""
    Shared.save_prefs()
    Shared.wait_task.cancel()


async def get_devices():
    """Get a list of devices from GHub by sending a /devices/list request to its websocket
    """
    logger = logging.getLogger(Shared.appname)

    headers = {'Origin': 'file://',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
            'Sec-WebSocket-Protocol': 'json'}

    devices_request = {
        'msgId': '',
        'verb': 'GET',
        'path': '/devices/list'
    }

    async with websockets.connect(uri="ws://localhost:9010",
                                extra_headers=headers,
                                subprotocols=['json'],
                                ) as websocket:

        logger.debug("Connected to LG Tray websocket")
        request = json.dumps(devices_request)
        await websocket.send(request)
        while True:            
            response = await websocket.recv()            
            message = json.loads(response)            
            if message['path'] == '/devices/list':
                logger.debug(f'Found {len(message['payload']['deviceInfos'])} devices')
                for d in message['payload']['deviceInfos']:
                    device = Device(id=d['id']
                                    ,unitId=d['deviceUnitId']
                                    ,name=d['extendedDisplayName']
                                    ,batteryLevel=None
                                    ,charging=False)
                    logger.debug(f'Status recieved for: {str(device)} (selected={Shared.selected_device})')
                    Shared.devices.append(device)
                break
        
        
    
async def watch_battery():
    """Subscribe to battery change notifications by sending a SUBSCRIBE for /battery/state/changed on the GHub websocket
    """
    logger = logging.getLogger(Shared.appname)

    headers = {'Origin': 'file://',
               'Pragma': 'no-cache',
               'Cache-Control': 'no-cache',
               'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
               'Sec-WebSocket-Protocol': 'json'}

    notifier_request = {
        'msgId': '',
        'verb': 'SUBSCRIBE',
        'path': '/battery/state/changed'
    }

    async with websockets.connect(uri="ws://localhost:9010",
                                  extra_headers=headers,
                                  subprotocols=['json'],
                                  ) as websocket:
        
        try:
            logger.debug("Connected to LG Tray websocket")
            request = json.dumps(notifier_request)
            await websocket.send(request)
            logger.debug(f"Sent request: {request}")
            done = False
            while done == False:
                Shared.wait_task = asyncio.create_task(websocket.recv())
                try:
                    response = await asyncio.gather(Shared.wait_task)
                    
                    if websocket.closed == False and response != None:                        
                        message = json.loads(response[0])
                        logger.debug(f"Received : {message}")
                        
                        if message['path'] != '/battery/state/changed':
                            continue
                            
                        device = get_device(message['payload']['deviceId'])
                        if None != device and device.id == Shared.selected_device:

                            device.charging = message['payload']['charging']
                            device.batteryLevel = message['payload']['percentage']
                            
                            if device.charging:
                                tooltip = f'{device.name}: {str(device.batteryLevel)}% (charging)'
                            else:
                                tooltip = f'{device.name}: {str(device.batteryLevel)}%' 
                            icon = get_icon(device.batteryLevel)
                            
                            logger.info(f"Level={device.batteryLevel}, Charging={device.charging}, Icon={icon}")
                            Shared.systray.update(hover_text=tooltip, icon=icon)

                            if Shared.level_file != None:
                                with open(Shared.level_file, 'w') as f:
                                    f.write(str(device.batteryLevel))
                                                                
                except asyncio.CancelledError:
                    logger.debug("await cancelled")
                    done = True
                    
        except websockets.ConnectionClosedOK as ex:
            return
        
if __name__ == '__main__':    
    Shared.load_prefs()
    Shared.init_logging()
    
    
    Shared.logger.debug('Started')
    export_icons()
    
    asyncio.run(get_devices())
    options = []
    for device in Shared.devices:
        t = (device.name, None, device.select)
        options.append(t)

    menu_options = tuple(options)

    Shared.systray = SysTrayIcon(get_icon(101), "...", menu_options=menu_options, on_quit=quit)
    Shared.systray.start()
    Shared.refresh_tray()
    
    asyncio.run(watch_battery())
    
    Shared.systray.shutdown()
    sys.exit(0)