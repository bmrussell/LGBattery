from __future__ import annotations

import asyncio
import json
import logging
import socket
import sys
import time
from dataclasses import dataclass
from functools import wraps

import websockets
from infi.systray import SysTrayIcon

from icons import export_icons, get_icon
from prefs import APPNAME, SELECTED_DEVICE_NAME, load_prefs, save_prefs

wait_task_holder = {}
main_event_loop = None


class Device:
    def __init__(self, parent, id, name):
        self.parent = parent
        self.id = id
        self.name = name
        self.battery_level = -1
        self.is_charging = False
        self.selected = False
        
            
    parent: list[Device]
    id: str
    name: str
    battery_level: int
    is_charging: bool
    selected: bool = False

    def __str__(self):
        return (f"Device(id={self.id}, name={self.name}, "
                f"battery_level={self.battery_level}%, "
                f"is_charging={'Yes' if self.is_charging else 'No'}, "
                f"selected={'Yes' if self.selected else 'No'})")
            
    def select(self, systray):
        for device in self.parent:
            device.selected = False
        self.selected = True
        
        refresh_by_selected_device(appinfo=None, devices=self.parent, systray=systray)
        
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
        
        devices = {}
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
                        devices[device.id] = device
                
                break
            
        devices_str = "Devices with batteries: "    
        for device_id, device in devices.items():
            devices_str = devices_str + f" // {device_id}: {device.name}"    
        logging.getLogger(APPNAME).debug(devices_str)
        
        return devices     


async def get_device_name(device_id):
    devices = await get_devices()
    
    for id, device in devices.items():
        if id == device_id:
            return device.name
    
    return None
  
def track_consecutive_calls(func):
    last_args = None
    last_kwargs = None

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal last_args, last_kwargs
        key = (args, tuple(sorted(kwargs.items())))
        is_repeat = (key == (last_args, last_kwargs))
        last_args, last_kwargs = args, tuple(sorted(kwargs.items()))
        
        # Pass _is_repeat to the decorated function
        return func(*args, _is_repeat=is_repeat, **kwargs)

    return wrapper

@track_consecutive_calls
def refresh_by_device_id(device_id, appinfo, is_charging, battery_level, _is_repeat=False):
    
    if _is_repeat:
        #logging.getLogger(APPNAME).debug(f"Called again wih the same parameters, skipping refresh for device_id={device_id}")
        return

    if device_id not in appinfo.devices:
        unknown_name = get_device_name(device_id)
        logging.getLogger(APPNAME).debug(f"Refresh called for unknown device_id={device_id}, name={unknown_name}")

    
    logging.getLogger(APPNAME).debug(f"device_id={device_id}, appinfo,is_charging={is_charging}, charge={battery_level}")    
    device = appinfo.devices[device_id]    
    if device.selected and (device.battery_level != battery_level or device.is_charging != is_charging):
        device.is_charging = is_charging
        device.battery_level = battery_level
        
        hover_text = f"{device.name}: {battery_level}%{' (charging)' if is_charging else ''}"
        logging.getLogger(APPNAME).info(f"appinfo.systray.update(hover_text={hover_text}")
        appinfo.systray.update(get_icon(battery_level), hover_text)

async def handle_monitor_message(response, websocket, appinfo):
    if websocket.closed or response is None:
        logging.getLogger(APPNAME).warning("WebSocket connection closed or no response received or quit selected.")
        return False

    if isinstance(response, list):
        message = json.loads(response[0])
    else:
        message = json.loads(response)

    if message['path'] != '/battery/state/changed':
        logging.getLogger(APPNAME).debug(f"message={message}")
        return True

    payload = message['payload']
    refresh_by_device_id(
        device_id=payload['deviceId'],
        appinfo=appinfo,
        is_charging=payload['charging'],
        battery_level=payload['percentage']
    )
    return True

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
    logging.getLogger(APPNAME).debug("monitoring...")
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
                monitoring = await handle_monitor_message(response, websocket, appinfo)
                if not monitoring:
                    break

            except asyncio.exceptions.CancelledError as ex:
                logging.getLogger(APPNAME).info("Task cancelled, stopping monitoring.")
                monitoring = False

            except websockets.ConnectionClosedError as ex:
                logging.getLogger(APPNAME).error("Connection closed. Probably came back from sleep")
                break

            except Exception as ex:
                logging.getLogger(APPNAME).warning(f"Exception {ex} - keep monitoring.")
                break

    logging.getLogger(APPNAME).debug(f"{'Keep monitoring' if monitoring else 'Stop monitoring'}")
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
        (_, device), = devices.items()
        device.selected = True
        logging.getLogger(APPNAME).info(f"Selected device: {device.name}")
    else:
        for device_id, device in devices.items():
            if device.name == SELECTED_DEVICE_NAME:
                device.selected = True
                logging.getLogger(APPNAME).info(f"Selected device: {device.name}")
            else:
                device.selected = False
    return devices

async def get_battery_level(id):
    level = None
    is_charging = False
    
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
                is_charging = (message['payload']['charging'] == True)
                logging.getLogger(APPNAME).info(f"device {id} has level={level}, charging={is_charging}")
                return level, is_charging
                
        return None
    
def refresh_by_selected_device(appinfo=None, devices=None, systray=None):
    logging.getLogger(APPNAME).debug("refreshing")
    
    if appinfo is not None:
        systray = appinfo.systray
        devices = appinfo.devices    
       
    for device_id, device in devices.items():
        if device.selected:
            logging.getLogger(APPNAME).debug(f"Selected device: {device.name} (id={device.id})")
            if device.battery_level == -1 or device.battery_level is None:
                # Fetch the battery level if not already set
                #level, charging = main_event_loop.run_until_complete(get_battery_level(device.id))
                logging.getLogger(APPNAME).debug(f"Fetching battery level for device {device.name} (id={device.id})")
                level, is_charging = asyncio.run(get_battery_level(device.id))                
                device.battery_level = level
                device.is_charging = is_charging
                logging.getLogger(APPNAME).debug(f"Device {device.name} (id={device.id}) has level={level}, charging={is_charging}")
           
            hover_text = f"{device.name}: {device.battery_level}%{' (charging)' if device.is_charging else ''}"
            icon = get_icon(device.battery_level)
            logging.getLogger(APPNAME).info(f"Updating systray icon={icon}, hover_text={hover_text}")
            systray.update(icon, hover_text)
            
            

def check_socket(address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((address, port))            
            return True
        except OSError:            
            return False

def wait_for_ghub(times=5, interval=30):
    for _ in range(times):
        if check_socket('localhost', 9010):
            return True
        time.sleep(interval)
    return False
    
if __name__ == "__main__":
    
    # Manually create an event loop so we can manage it and call cancel on the
    # task waiting for battery status in quit()
    
    load_prefs()
    if not wait_for_ghub():
        logging.getLogger(APPNAME).error("Could not connect to GHub. Is it running?")
        sys.exit(1)
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main_event_loop = loop
    
    devices = loop.run_until_complete(get_devices_a())
    export_icons()
    options = []
    for device_id, device in devices.items():
        menuitem_icon = None
        t = (device.name, menuitem_icon, device.select)
        options.append(t)
        
    menu_options = tuple(options)
    systray = SysTrayIcon(get_icon(101), "...", menu_options=menu_options, on_quit=quit)
    appinfo = appinfo(devices=devices, systray=systray)
    systray.start()


    keep_monitoring = True
    while keep_monitoring:
        
        try:
            wait_for_ghub()
            devices = loop.run_until_complete(get_devices_a())
            appinfo.devices = devices
            refresh_by_selected_device(appinfo=appinfo)
            keep_monitoring = loop.run_until_complete(monitor(appinfo))
            
        except Exception as ex:
            logging.getLogger(APPNAME).error(f"Error: {ex}")

        
        
    systray.shutdown()
    loop.close()
    save_prefs()
    sys.exit(0)
