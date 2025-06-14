import asyncio
import json
import logging

import websockets

from icons import get_icon
from prefs import Shared


def get_device_by_id(id):
    for dev in Shared.devices:
        if dev.id == id:
            return dev
    return None

class Device:
    def __init__(self, id, unitId, name, batteryLevel, charging):
        self.id = id
        self.unitId = unitId
        self.name = name
        self.batteryLevel = batteryLevel
        self.charging = charging
        

    def __repr__(self):
        return f"<Device(id:{self.id} unitId:{self.unitId} name:{self.name} batteryLevel:{self.batteryLevel} charging:{self.charging})>"

    def __str__(self):
        return f"Device(id:{self.id} unitId:{self.unitId} name:{self.name} batteryLevel:{self.batteryLevel} charging:{self.charging})>"


    async def get_battery(self):
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
            'path': f'/battery/{self.id}/state'
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
                Shared.logger.info(f'Received: {message}')
                if message['path'] == f'/battery/{self.id}/state':
                    self.batteryLevel = message['payload']['percentage']
                    self.charging = (message['payload']['charging'] == True)
                    break
    
    def select(self, tray):
        logger = logging.getLogger(Shared.appname)
        logger.info(f'Device.SELECT: Selected {self.id} {self.name}')
        Shared.selected_device = self
        Shared.selected_device_name = self.name
        asyncio.run(self.get_battery())
        if self.charging:
            tooltip = f'{self.name}: {self.batteryLevel}% (charging)'
        else:
            tooltip = f'{self.name}: {str(self.batteryLevel)}%' 
        icon = get_icon(self.batteryLevel)
        Shared.systray.update(hover_text=tooltip, icon=icon)
        
        if Shared.level_file != None:
            with open(Shared.level_file, 'w') as f:
                f.write(str(self.batteryLevel))
