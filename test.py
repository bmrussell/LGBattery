from __future__ import annotations

import asyncio
import json
import logging
import sys
from dataclasses import dataclass

import websockets
from infi.systray import SysTrayIcon

from icons import export_icons, get_icon

wait_task_holder = {}
main_event_loop = None


class Device:
    def __init__(self, parent, id, name):
        self.parent = parent
        self.id = id
        self.name = name
        self.battery_level = -1
        self.charging = False
        self.selected = False
        
            
    parent: list[Device]
    id: str
    name: str
    battery_level: int
    charging: bool
    selected: bool = False
    
    def select(self, systray):
        for device in self.parent:
            device.selected = False
        self.selected = True
        
        refresh_tray(devices, systray)

@dataclass
class appinfo:
    devices: list[Device]
    systray: SysTrayIcon
    


logging.basicConfig(level=logging.INFO)

async def get_devices():
    uri = "ws://localhost:9010"
    
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
            
    async with websockets.connect(uri,
                                extra_headers=headers,
                                subprotocols=['json']) as websocket:
        
        devices = []
        request = json.dumps(devices_request)
        await websocket.send(request)
        while True:
            response = await websocket.recv()
            message = json.loads(response)
            if message['path'] == '/devices/list':
                for d in message['payload']['deviceInfos']:
                    if d['capabilities']['hasBatteryStatus']:
                        device = Device(
                            parent=devices,
                            id=d['id'],
                            name=d['extendedDisplayName'],
                        )
                        devices.append(device)
                
                break
        return devices     


def set_status(device_id, appinfo, is_charging, charge):
    for device in appinfo.devices:
        if device.id == device_id and device.battery_level != charge and device.charging != is_charging:
            device.charging = is_charging
            device.battery_level = charge
            appinfo.systray.update(hover_text=f"{device.name}: {charge}%{' (charging)' if is_charging else ''}",icon=get_icon(charge))
            logging.getLogger("asyncio").info(f"{device.name} at {device.battery_level}%")
        

async def monitor(appinfo):
    
    global wait_task_holder
    
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
    
    monitoring = True
    async with websockets.connect(uri="ws://localhost:9010",
                                    extra_headers=headers,
                                    subprotocols=['json'],
                                    ) as websocket:     

        while monitoring:
            await websocket.send(request)

            socket_task = asyncio.create_task(websocket.recv())
            async with asyncio.Lock():
                wait_task_holder['task'] = socket_task
            
            try:
                response = await asyncio.gather(socket_task)

                if websocket.closed or response == None:
                    logging.getLogger("asyncio").warning("WebSocket connection closed or no response received or quit selected.")
                    break
                
                if isinstance(response, list):
                    message = json.loads(response[0])
                else:
                    message = json.loads(response)
                
                if message['path'] != '/battery/state/changed':
                    continue
                            
                payload = message['payload']
                
                
                set_status(
                    device_id=payload['deviceId'],
                    appinfo=appinfo,
                    is_charging=payload['charging'],
                    charge=payload['percentage']
                )
                
            except asyncio.exceptions.CancelledError as ex:
                logging.getLogger("asyncio").info("Task cancelled, stopping monitoring.")
                monitoring = False
            
            except websockets.ConnectionClosedError as ex:
                logging.getLogger("asyncio").error("Connection closed. Probably came back from sleep")

            except Exception as ex:
                logging.getLogger("asyncio").info(f"Exception {ex} - keep monitoring.")

    return monitoring

def quit(tray):
    global main_event_loop
    try:
        if 'task' in wait_task_holder:
            main_event_loop.call_soon_threadsafe(wait_task_holder['task'].cancel)
    except Exception as ex:
        logging.error(f"Error cancelling task: {ex}")
            
async def get_devices_a():
    devices = await get_devices()
    if len(devices) == 1:
        devices[0].selected = True
        
    return devices



async def get_battery_level(id):
    level = None
    charging = False
    
    headers = {'Origin': 'file://',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
            'Sec-WebSocket-Protocol': 'json'}
        
    battery_request = {
        'msgId': '',
        'verb': 'GET',
        'path': f'/battery/{id}/state'
    }
    
    async with websockets.connect(uri="ws://localhost:9010",
                                    extra_headers=headers,
                                    subprotocols=['json'],
                                    ) as websocket:    
        while True:
            request = json.dumps(battery_request)
            await websocket.send(request)
            response = await websocket.recv()
            message = json.loads(response)            
            if message['path'] == f'/battery/{id}/state':
                level = message['payload']['percentage']
                charging = (message['payload']['charging'] == True)
                return level, charging
                
        return None
    
def refresh_tray(appinfo):
    for device in appinfo.devices:
        if device.selected:
            if device.battery_level == -1 or device.battery_level is None:
                # Fetch the battery level if not already set
                #level, charging = main_event_loop.run_until_complete(get_battery_level(device.id))
                level, charging = asyncio.run(get_battery_level(device.id))                
                device.battery_level = level
                device.charging = charging

            charging_text = ", charging" if device.charging else ""
            tooltip = f'{device.name}: {str(device.battery_level)}%{charging_text}'
            icon = get_icon(device.battery_level)
            appinfo.systray.update(hover_text=tooltip, icon=icon)
            
    
if __name__ == "__main__":
    
    # Manually create an event loop so we can manage it and call cancel on the
    # task waiting for battery status in quit()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main_event_loop = loop
    
    keep_monitoring = True
    while keep_monitoring:
        try:
            devices = loop.run_until_complete(get_devices_a())

            export_icons()
            options = []
            for device in devices:
                menuitem_icon = None
                t = (device.name, menuitem_icon, device.select)
                options.append(t)
                
            menu_options = tuple(options)
            systray = SysTrayIcon(get_icon(101), "...", menu_options=menu_options, on_quit=quit)
            appinfo = appinfo(devices=devices, systray=systray)
            systray.start()
            refresh_tray(appinfo)

            keep_monitoring = loop.run_until_complete(monitor(appinfo))
            
            
        except Exception as ex:
            logging.getLogger("asyncio").error(f"Error cancelling task: {ex}")
    
    systray.shutdown()
    loop.close()
    sys.exit(0)
        
