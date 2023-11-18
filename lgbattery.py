import asyncio
import json
import os
import socket
import sys
import time

import websockets
from infi.systray import SysTrayIcon

from device import Device, get_device_by_id
from exceptions import BatteryMonitoringError, UnknownDeviceError
from globals import Shared
from icons import export_icons, get_icon


def quit(tray):
    Shared.logger.debug("QUIT: Quit called")
    """Bailing"""
    quit_selected = True
    Shared.save_prefs()
    Shared.wait_task.cancel()
    Shared.logger.debug("QUIT: Hard Exit.")
    os._exit(0)


async def get_devices():
    """Get a list of devices from GHub by sending a /devices/list request to its websocket
    """

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
    Shared.logger.debug("GET_DEVICES: Start")
    Shared.devices = []
    async with websockets.connect(uri="ws://localhost:9010",
                                extra_headers=headers,
                                subprotocols=['json'],
                                ) as websocket:

        Shared.logger.debug("GET_DEVICES: Connected to LG Tray websocket")
        request = json.dumps(devices_request)
        await websocket.send(request)
        while True:            
            response = await websocket.recv()            
            message = json.loads(response)            
            if message['path'] == '/devices/list':
                Shared.logger.debug(f'GET_DEVICES: Found {len(message['payload']['deviceInfos'])} devices')
                for d in message['payload']['deviceInfos']:
                    Shared.logger.debug(f'GET_DEVICES: Found device: {d['extendedDisplayName']} ({d['id']}). Battery={d['capabilities']['hasBatteryStatus']}')
                    if d['capabilities']['hasBatteryStatus']:
                        device = Device(id=d['id']
                                        ,unitId=d['deviceUnitId']
                                        ,name=d['extendedDisplayName']
                                        ,batteryLevel=None
                                        ,charging=False)
                        
                        Shared.devices.append(device)
                        
                        # Set the selected device on load
                        if device.name == Shared.selected_device_name:
                            Shared.selected_device = device
                            Shared.logger.info(f"GET_DEVICES: Selected device: {str(device)}")

                break
        
        
    
async def watch_battery():
    """Subscribe to battery change notifications by sending a SUBSCRIBE for /battery/state/changed on the GHub websocket
    """

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
    request = json.dumps(notifier_request)
    
    async with websockets.connect(uri="ws://localhost:9010",
                                    extra_headers=headers,
                                    subprotocols=['json'],
                                    ) as websocket:                
        Shared.logger.debug("WATCH_BATTERY: Connected to LG Tray websocket")            
        #raise ValueError('A very specific bad thing happened.')
        while True:
            await websocket.send(request)
            Shared.logger.debug(f"WATCH_BATTERY: Sent request {request}")
            
            
            Shared.wait_task = asyncio.create_task(websocket.recv())
            response = await asyncio.gather(Shared.wait_task)
            
            if websocket.closed or response == None:
                # Either the connection was closed or something went wrong
                # Deal with this in main
                message = f"Exiting as something went wrong. websocket.closed={websocket.closed} response={response}"
                Shared.logger.error(f'WATCH_BATTERY: {message}')
                raise BatteryMonitoringError(message)

            message = json.loads(response[0])
            Shared.logger.debug(f"WATCH_BATTERY: Received {message}")
            
            if message['path'] != '/battery/state/changed':
                continue
                
            device = get_device_by_id(message['payload']['deviceId'])
            if device == None:
                Shared.logger.debug(f"WATCH_BATTERY: get_device_by_id({message['payload']['deviceId']}) returned None")
                # May have resumed from sleep and LGHub changed the device IDs under us
                # So raise an exception to bubble up to the top and start the monitoring again at the top level
                message = f"Got a message from an unknown device with id {message['payload']['deviceId']}"
                Shared.logger.warning(f'WATCH_BATTERY: {message}')
                raise UnknownDeviceError(message)
            
            Shared.logger.debug(f"WATCH_BATTERY: get_device_by_id({message['payload']['deviceId']}) == (id={device.id}, name={device.name})")
                
            if device.id == Shared.selected_device.id:
                device.charging = message['payload']['charging']
                changed = device.batteryLevel != message['payload']['percentage'] or device.charging != message['payload']['charging']
                device.batteryLevel = message['payload']['percentage']
                
                if device.charging:
                    tooltip = f'{device.name}: {str(device.batteryLevel)}% (charging)'
                else:
                    tooltip = f'{device.name}: {str(device.batteryLevel)}%' 
                    
                icon = get_icon(device.batteryLevel)
                
                Shared.logger.info(f"WATCH_BATTERY: Level={device.batteryLevel}, Charging={device.charging}, Icon={icon}")
                if changed:
                    Shared.systray.update(hover_text=tooltip, icon=icon)

                if Shared.level_file != None:
                    with open(Shared.level_file, 'w') as f:
                        f.write(str(device.batteryLevel))



def check_socket(address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((address, port))            
            return True
        except:            
            return False

def wait_for_ghub():
    for i in range(5):
        if check_socket('localhost', 9010):
            return True
        time.sleep(30)
    return False

if __name__ == '__main__':
    
    Shared.load_prefs()
    Shared.init_logging()
    Shared.logger.debug('MAIN: Started')
    
    export_icons()
    
    # Get the devices on first run to set up the system tray
    asyncio.run(get_devices())
    options = []
    for device in Shared.devices:
        t = (device.name, None, device.select)
        options.append(t)

    menu_options = tuple(options)

    Shared.systray = SysTrayIcon(get_icon(101), "...", menu_options=menu_options, on_quit=quit)
    Shared.systray.start()
    Shared.refresh_tray()
   
    if wait_for_ghub() == False:
        Shared.systray.shutdown()
        sys.exit(0)
        
    while Shared.quit_selected == False:
        try:
            asyncio.run(watch_battery())
        except UnknownDeviceError as ex:
            # Device list changed when we were running so refresh the list of devices
            asyncio.run(get_devices())
            # Force update
            Shared.selected_device.select(None)
            
        except Exception as ex:            
            Shared.logger.info(f"MAIN(): Exception {ex.__class__.__name__}. PC maybe woke up from sleep {str(ex)}.")
            if wait_for_ghub() == False:
                break
            
    Shared.systray.shutdown()
    sys.exit(0)