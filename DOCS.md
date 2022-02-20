# Home Assistant Add-on: Bluetooth LE to MQTT

## Installation

This plugin requires the Mosquitto MQTT Broker plugin installed and running.

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Configuration** -> Add-ons, backups and Supervisor -> **Add-on Store**.
2. Select **Repositories** from menu, and add new repository: https://github.com/blizniukp/ha_addon_ble2mqtt
3. Find the "Bluetooth LE to MQTT" add-on and click it.
4. Click on the "INSTALL" button.

## How to use

After installing the add-on, go to the configuration page.

Fill in your Mqtt broker details (user name and password) there.

Next, you must provide Roundpad device information to the `devices` array. 

Due to the limit of bluetooth devices on the gateway, the maximum number of supported devices is 4.

Example of add-on configuration:
<pre>      
address: homeassistant
port: 1883
qos: 1
username: mqttuser
password: mqttpassword
anonymous: false
sub_topic: /ble2mqtt/app/#
pub_topic: /ble2mqtt/dev/
devices:
  - name: ROUND_PAD_1
    address_type: random
    address: DA:D5:10:DC:D0:3A
    service_uuid: 71F1BB00-1C43-5BAC-B24B-FDABEEC53913
    char_uuid: 71F1BB01-1C43-5BAC-B24B-FDABEEC53913
  - name: ROUND_PAD_2
    address_type: random
    address: DF:E2:FB:80:50:3E
    service_uuid: 71F1BB00-1C43-5BAC-B24B-FDABEEC53913
    char_uuid: 71F1BB01-1C43-5BAC-B24B-FDABEEC53913
</pre>

## Description

The add-on works with the [esp32_ble2mqtt](https://github.com/blizniukp/esp32_ble2mqtt) gateway and the device [Roundpad](https://github.com/piotrvvilk).

Used to create `switch` buttons in Home Assistant that are controlled from Bluetooth devices.

The RoundPad has 6 buttons each capable of transmitting single, double click and long key press information.
Therefore, the add-on creates 18 buttons (6 buttons * 3 functionalities).

The name of each button consists of the device name, button number, and click type.

Examples:

                -- Button number
                |  -- Click type
                |  |
    ROUND_PAD_2_B1_F1 << device named ROUND_PAD_2, button 1, single click type
    
    ROUND_PAD_2_B4_F2 << device named ROUND_PAD_2, button 4, double click type

    ROUND_PAD_2_B4_F3 << device named ROUND_PAD_2, button 4, long click type

The entity name, on the other hand, contains the MAC address of the device (colon replaced by an underscore character), the button number, and the click type.

Examples:

                       -- Button number                                                                   
                       |  -- Click type                                                              
                       |  |                                                                                  
    DF_E2_FB_80_50_3E_B1_F1 << device with MAC address DF:E2:FB:80:50:3E, button 1, single click type
                                                                                                      
    DF_E2_FB_80_50_3E_B4_F2 << device with MAC address DF:E2:FB:80:50:3E, button 4, double click type  
                                                                                                  
    DF_E2_FB_80_50_3E_B4_F3 << device with MAC address DF:E2:FB:80:50:3E, button 4, long click type  

The data sent from the ble2mqtt gateway has information about the MAC address of the device from which the data was sent, and the data sent from the button.

Example:

    {"address": "DA:D5:10:DC:D0:3A", "is_notify": true, "val_len": 8, "val": "0202000000000000"}

The value in 'val' contains data about the status of the device and the status of the buttons.

    D7   D6   D5   D4   D3   D2   D1   D0   << Byte numbering
    02 | 02 | 00 | 00 | 00 | 00 | 00 | 00   << Data from the Roundpad

In `D7` there is information containing the number of the button pressed and type of click.

Possible values are:

    0x11 - Button 1 / one click
    0x12 - Button 1 / two clicks
    0x13 - Button 1 / long click
    0x21 - Button 2 / one click
    0x22 - Button 2 / two clicks
    0x23 - Button 2 / long click
    ...
    0x61 - Button 6 / one click
    0x62 - Button 6 / two clicks
    0x63 - Button 6 / long click

In `D6` is the type of click/event. 

Possible values are:

    0x00 - Button is not pressed
    0x01 - Button is pressed
