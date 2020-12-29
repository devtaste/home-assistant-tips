add_device:
  description: Enables the join permission of the Xiaomi Aqara Gateway for 30 seconds.
    A new device can be added afterwards by pressing the pairing button once.
  fields:
    gw_mac: {description: MAC address of the Xiaomi Aqara Gateway., example: 34ce00880088}
play_ringtone:
  description: Play a specific ringtone. The version of the gateway firmware must
    be 1.4.1_145 at least.
  fields:
    gw_mac: {description: MAC address of the Xiaomi Aqara Gateway., example: 34ce00880088}
    ringtone_id: {description: One of the allowed ringtone ids., example: 8}
    ringtone_vol: {description: The volume in percent., example: 30}
remove_device:
  description: Removes a specific device. The removal is required if a device shall
    be paired with another gateway.
  fields:
    device_id: {description: Hardware address of the device to remove., example: 158d0000000000}
    gw_mac: {description: MAC address of the Xiaomi Aqara Gateway., example: 34ce00880088}
stop_ringtone:
  description: Stops a playing ringtone immediately.
  fields:
    gw_mac: {description: MAC address of the Xiaomi Aqara Gateway., example: 34ce00880088}