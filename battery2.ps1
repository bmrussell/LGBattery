using namespace System.Net.WebSockets
using namespace System.Text
using namespace System.Threading

function Get-Devices {
    Write-Host "GET_DEVICES: Start"
    $uri = [Uri]::new("ws://localhost:9010")
    $client = [ClientWebSocket]::new()

    $client.Options.SetRequestHeader("Origin", "file://")
    $client.Options.SetRequestHeader("Pragma", "no-cache")
    $client.Options.SetRequestHeader("Cache-Control", "no-cache")
    $client.Options.SetRequestHeader("Sec-WebSocket-Extensions", "permessage-deflate; client_max_window_bits")
    $client.Options.AddSubProtocol("json")

    $ct = [CancellationToken]::None
    $client.ConnectAsync($uri, $ct).Wait()
    Write-Host "GET_DEVICES: Connected to LG Tray websocket"

    $request = @{
        msgId = ""
        verb  = "GET"
        path  = "/devices/list"
    } | ConvertTo-Json -Compress

    $requestBuffer = [Text.Encoding]::UTF8.GetBytes($request)
    $segment = [ArraySegment[byte]]::new($requestBuffer)
    $client.SendAsync($segment, [WebSocketMessageType]::Text, $true, $ct).Wait()

    $buffer = New-Object byte[] 4096
    $result = $client.ReceiveAsync([ArraySegment[byte]]::new($buffer), $ct).Result

    $response = [Text.Encoding]::UTF8.GetString($buffer, 0, $result.Count)
    $message = $response | ConvertFrom-Json

    if ($message.path -eq "/devices/list") {
        foreach ($d in $message.payload.deviceInfos) {
            $deviceId = $d.id
            $deviceName = $d.extendedDisplayName
            $hasBattery = if ($d.capabilities.hasBatteryStatus) { "with battery" } else { "with no battery" }
            Write-Host "GET_DEVICES: Found device: $deviceId ($deviceName), $hasBattery."

            if ($d.capabilities.hasBatteryStatus) {
                $device = [PSCustomObject]@{
                    id          = $d.id
                    unitId      = $d.deviceUnitId
                    name        = $d.extendedDisplayName
                    batteryLevel = $null
                    charging     = $false
                }

                # Simulate Shared.devices
                if (-not $script:SharedDevices) {
                    $script:SharedDevices = @()
                }
                $script:SharedDevices += $device

                # Select device
                if ($device.name -eq $script:SelectedDeviceName) {
                    $script:SelectedDevice = $device
                    Write-Host "GET_DEVICES: Selected device: $($device | ConvertTo-Json -Compress)"
                }
            }
        }
    }

    $client.Dispose()
}


Get-Devices 