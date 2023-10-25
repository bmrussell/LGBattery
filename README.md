
```json
{
    "msgId": "c0feb790-62cf-4c83-befb-bef979d2d12f",
    "verb": "BROADCAST",
    "path": "/battery/state/changed",
    "origin": "backend",
    "payload": {
        "@type": "type.googleapis.com/logi.protocol.wireless.Battery",
        "deviceId": "dev0000001e",
        "percentage": 63,
        "mileage": 16.2675762,
        "maxLifeSpan": 25.8215485,
        "charging": False,
        "consumption": {
            "value": 9.18245697,
            "details": {
                "system": 5.92066669,
                "sensor": 4.28,
                "mcu": 1.64066672,
                "roller": 0,
                "reportRate": 8.162673,
                "lighting": 5.4763155,
                "volume": 0
            },
            "useMw": True
        },
        "simpleBattery": False,
        "criticalLevel": False,
        "chargingError": False,
        "componentType": "INVALID_TYPE"
    }
}
```