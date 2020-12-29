"""Support for Xiaomi aqara binary sensors."""
import logging

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.components.xiaomi_aqara import (PY_XIAOMI_GATEWAY,
                                                   XiaomiDevice)
from homeassistant.core import callback
from homeassistant.helpers.event import async_call_later

_LOGGER = logging.getLogger(__name__)

NO_CLOSE = 'no_close'
ATTR_OPEN_SINCE = 'Open since'

MOTION = 'motion'
NO_MOTION = 'no_motion'
ATTR_LAST_ACTION = 'last_action'
ATTR_NO_MOTION_SINCE = 'No motion since'

DENSITY = 'density'
ATTR_DENSITY = 'Density'

HARDWARE_MODIFIED = True
NO_MOTION_TIMEOUT = 5

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Perform the setup for Xiaomi devices."""
    devices = []
    for (_, gateway) in hass.data[PY_XIAOMI_GATEWAY].gateways.items():
        for device in gateway.devices['binary_sensor']:
            model = device['model']
            if model in ['motion', 'sensor_motion', 'sensor_motion.aq2']:
                devices.append(XiaomiMotionSensor(device, hass, gateway,
                                                  HARDWARE_MODIFIED))
            elif model in ['magnet', 'sensor_magnet', 'sensor_magnet.aq2']:
                devices.append(XiaomiDoorSensor(device, gateway))
            elif model == 'sensor_wleak.aq1':
                devices.append(XiaomiWaterLeakSensor(device, gateway))
            elif model in ['smoke', 'sensor_smoke']:
                devices.append(XiaomiSmokeSensor(device, gateway))
            elif model in ['natgas', 'sensor_natgas']:
                devices.append(XiaomiNatgasSensor(device, gateway))
            elif model in ['switch', 'sensor_switch',
                           'sensor_switch.aq2', 'sensor_switch.aq3',
                           'remote.b1acn01']:
                if 'proto' not in device or int(device['proto'][0:1]) == 1:
                    data_key = 'status'
                else:
                    data_key = 'button_0'
                devices.append(XiaomiButton(device, 'Switch', data_key,
                                            hass, gateway))
            elif model in ['86sw1', 'sensor_86sw1', 'sensor_86sw1.aq1',
                           'remote.b186acn01']:
                if 'proto' not in device or int(device['proto'][0:1]) == 1:
                    data_key = 'channel_0'
                else:
                    data_key = 'button_0'
                devices.append(XiaomiButton(device, 'Wall Switch', data_key,
                                            hass, gateway))
            elif model in ['86sw2', 'sensor_86sw2', 'sensor_86sw2.aq1',
                           'remote.b286acn01']:
                if 'proto' not in device or int(device['proto'][0:1]) == 1:
                    data_key_left = 'channel_0'
                    data_key_right = 'channel_1'
                else:
                    data_key_left = 'button_0'
                    data_key_right = 'button_1'
                devices.append(XiaomiButton(device, 'Wall Switch (Left)',
                                            data_key_left, hass, gateway))
                devices.append(XiaomiButton(device, 'Wall Switch (Right)',
                                            data_key_right, hass, gateway))
                devices.append(XiaomiButton(device, 'Wall Switch (Both)',
                                            'dual_channel', hass, gateway))
            elif model in ['cube', 'sensor_cube', 'sensor_cube.aqgl01']:
                devices.append(XiaomiCube(device, hass, gateway))
            elif model in ['vibration', 'vibration.aq1']:
                devices.append(XiaomiVibration(device, 'Vibration',
                                               'status', gateway))
            else:
                _LOGGER.warning('Unmapped Device Model %s', model)

    add_entities(devices)


class XiaomiBinarySensor(XiaomiDevice, BinarySensorDevice):
    """Representation of a base XiaomiBinarySensor."""

    def __init__(self, device, name, xiaomi_hub, data_key, device_class):
        """Initialize the XiaomiSmokeSensor."""
        self._data_key = data_key
        self._device_class = device_class
        self._should_poll = False
        self._density = 0
        XiaomiDevice.__init__(self, device, name, xiaomi_hub)

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state."""
        return self._should_poll

    @property
    def is_on(self):
        """Return true if sensor is on."""
        return self._state

    @property
    def device_class(self):
        """Return the class of binary sensor."""
        return self._device_class

    def update(self):
        """Update the sensor state."""
        _LOGGER.debug('Updating xiaomi sensor (%s) by polling', self._sid)
        self._get_from_hub(self._sid)


class XiaomiNatgasSensor(XiaomiBinarySensor):
    """Representation of a XiaomiNatgasSensor."""

    def __init__(self, device, xiaomi_hub):
        """Initialize the XiaomiSmokeSensor."""
        self._density = None
        XiaomiBinarySensor.__init__(self, device, 'Natgas Sensor', xiaomi_hub,
                                    'alarm', 'gas')

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {ATTR_DENSITY: self._density}
        attrs.update(super().device_state_attributes)
        return attrs

    def parse_data(self, data, raw_data):
        """Parse data sent by gateway."""
        if DENSITY in data:
            self._density = int(data.get(DENSITY))

        value = data.get(self._data_key)
        if value is None:
            return False

        if value in ('1', '2'):
            if self._state:
                return False
            self._state = True
            return True
        if value == '0':
            if self._state:
                self._state = False
                return True
            return False


class XiaomiMotionSensor(XiaomiBinarySensor):
    """Representation of a XiaomiMotionSensor."""

    def __init__(self, device, hass, xiaomi_hub, hardware_modified):
        """Initialize the XiaomiMotionSensor."""
        self._hass = hass
        self._no_motion_since = 0
        self._unsub_set_no_motion = None
        self._hardware_modified = hardware_modified
        if 'proto' not in device or int(device['proto'][0:1]) == 1:
            data_key = 'status'
        else:
            data_key = 'motion_status'
        XiaomiBinarySensor.__init__(self, device, 'Motion Sensor', xiaomi_hub,
                                    data_key, 'motion')

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {ATTR_NO_MOTION_SINCE: self._no_motion_since}
        attrs.update(super().device_state_attributes)
        return attrs

    @callback
    def _async_set_no_motion(self, now):
        """Set state to False."""
        self._unsub_set_no_motion = None
        self._state = False
        self.async_schedule_update_ha_state()

    def parse_data(self, data, raw_data):
        """Parse data sent by gateway.

        Polling (proto v1, firmware version 1.4.1_159.0143)

        >> { "cmd":"read","sid":"158..."}
        << {'model': 'motion', 'sid': '158...', 'short_id': 26331,
            'cmd': 'read_ack', 'data': '{"voltage":3005}'}

        Multicast messages (proto v1, firmware version 1.4.1_159.0143)

        << {'model': 'motion', 'sid': '158...', 'short_id': 26331,
            'cmd': 'report', 'data': '{"status":"motion"}'}
        << {'model': 'motion', 'sid': '158...', 'short_id': 26331,
            'cmd': 'report', 'data': '{"no_motion":"120"}'}
        << {'model': 'motion', 'sid': '158...', 'short_id': 26331,
            'cmd': 'report', 'data': '{"no_motion":"180"}'}
        << {'model': 'motion', 'sid': '158...', 'short_id': 26331,
           'cmd': 'report', 'data': '{"no_motion":"300"}'}
        << {'model': 'motion', 'sid': '158...', 'short_id': 26331,
            'cmd': 'heartbeat', 'data': '{"voltage":3005}'}

        """
        if raw_data['cmd'] == 'heartbeat':
            _LOGGER.debug(
                'Skipping heartbeat of the motion sensor. '
                'It can introduce an incorrect state because of a firmware '
                'bug (https://github.com/home-assistant/home-assistant/pull/'
                '11631#issuecomment-357507744).')
            return

        if not self._hardware_modified and NO_MOTION in data:
            self._no_motion_since = data[NO_MOTION]
            self._state = False
            return True

        value = data.get(self._data_key)
        if value is None:
            return False

        if value == MOTION:
            if self._data_key == 'motion_status' or self._hardware_modified:
                delay = NO_MOTION_TIMEOUT if self._hardware_modified else 120
                if self._unsub_set_no_motion:
                    self._unsub_set_no_motion()
                self._unsub_set_no_motion = async_call_later(
                    self._hass,
                    delay,
                    self._async_set_no_motion
                )

            if self.entity_id is not None:
                self._hass.bus.fire('xiaomi_aqara.motion', {
                    'entity_id': self.entity_id
                })

            self._no_motion_since = 0
            if self._state:
                return False
            self._state = True
            return True


class XiaomiDoorSensor(XiaomiBinarySensor):
    """Representation of a XiaomiDoorSensor."""

    def __init__(self, device, xiaomi_hub):
        """Initialize the XiaomiDoorSensor."""
        self._open_since = 0
        if 'proto' not in device or int(device['proto'][0:1]) == 1:
            data_key = 'status'
        else:
            data_key = 'window_status'
        XiaomiBinarySensor.__init__(self, device, 'Door Window Sensor',
                                    xiaomi_hub, data_key, 'opening')

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {ATTR_OPEN_SINCE: self._open_since}
        attrs.update(super().device_state_attributes)
        return attrs

    def parse_data(self, data, raw_data):
        """Parse data sent by gateway."""
        self._should_poll = False
        if NO_CLOSE in data:  # handle push from the hub
            self._open_since = data[NO_CLOSE]
            return True

        value = data.get(self._data_key)
        if value is None:
            return False

        if value == 'open':
            self._should_poll = False
            if self._state:
                return False
            self._state = True
            return True
        if value == 'close':
            self._open_since = 0
            if self._state:
                self._state = False
                return True
            return False


class XiaomiWaterLeakSensor(XiaomiBinarySensor):
    """Representation of a XiaomiWaterLeakSensor."""

    def __init__(self, device, xiaomi_hub):
        """Initialize the XiaomiWaterLeakSensor."""
        if 'proto' not in device or int(device['proto'][0:1]) == 1:
            data_key = 'status'
        else:
            data_key = 'wleak_status'
        XiaomiBinarySensor.__init__(self, device, 'Water Leak Sensor',
                                    xiaomi_hub, data_key, 'moisture')

    def parse_data(self, data, raw_data):
        """Parse data sent by gateway."""
        self._should_poll = False

        value = data.get(self._data_key)
        if value is None:
            return False

        if value == 'leak':
            self._should_poll = True
            if self._state:
                return False
            self._state = True
            return True
        if value == 'no_leak':
            if self._state:
                self._state = False
                return True
            return False


class XiaomiSmokeSensor(XiaomiBinarySensor):
    """Representation of a XiaomiSmokeSensor."""

    def __init__(self, device, xiaomi_hub):
        """Initialize the XiaomiSmokeSensor."""
        self._density = 0
        XiaomiBinarySensor.__init__(self, device, 'Smoke Sensor', xiaomi_hub,
                                    'alarm', 'smoke')

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {ATTR_DENSITY: self._density}
        attrs.update(super().device_state_attributes)
        return attrs

    def parse_data(self, data, raw_data):
        """Parse data sent by gateway."""
        if DENSITY in data:
            self._density = int(data.get(DENSITY))
        value = data.get(self._data_key)
        if value is None:
            return False

        if value in ('1', '2'):
            if self._state:
                return False
            self._state = True
            return True
        if value == '0':
            if self._state:
                self._state = False
                return True
            return False


class XiaomiVibration(XiaomiBinarySensor):
    """Representation of a Xiaomi Vibration Sensor."""

    def __init__(self, device, name, data_key, xiaomi_hub):
        """Initialize the XiaomiVibration."""
        self._last_action = None
        super().__init__(device, name, xiaomi_hub, data_key, None)

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {ATTR_LAST_ACTION: self._last_action}
        attrs.update(super().device_state_attributes)
        return attrs

    def parse_data(self, data, raw_data):
        """Parse data sent by gateway."""
        value = data.get(self._data_key)
        if value is None:
            return False

        if value not in ('vibrate', 'tilt', 'free_fall'):
            _LOGGER.warning("Unsupported movement_type detected: %s",
                            value)
            return False

        self.hass.bus.fire('xiaomi_aqara.movement', {
            'entity_id': self.entity_id,
            'movement_type': value
        })
        self._last_action = value

        return True


class XiaomiButton(XiaomiBinarySensor):
    """Representation of a Xiaomi Button."""

    def __init__(self, device, name, data_key, hass, xiaomi_hub):
        """Initialize the XiaomiButton."""
        self._hass = hass
        self._last_action = None
        XiaomiBinarySensor.__init__(self, device, name, xiaomi_hub,
                                    data_key, None)

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {ATTR_LAST_ACTION: self._last_action}
        attrs.update(super().device_state_attributes)
        return attrs

    def parse_data(self, data, raw_data):
        """Parse data sent by gateway."""
        value = data.get(self._data_key)
        if value is None:
            return False

        if value == 'long_click_press':
            self._state = True
            click_type = 'long_click_press'
        elif value == 'long_click_release':
            self._state = False
            click_type = 'hold'
        elif value == 'click':
            click_type = 'single'
        elif value == 'double_click':
            click_type = 'double'
        elif value == 'both_click':
            click_type = 'both'
        elif value == 'double_both_click':
            click_type = 'double_both'
        elif value == 'shake':
            click_type = 'shake'
        elif value == 'long_click':
            click_type = 'long'
        elif value == 'long_both_click':
            click_type = 'long_both'
        else:
            _LOGGER.warning("Unsupported click_type detected: %s", value)
            return False

        self._hass.bus.fire('xiaomi_aqara.click', {
            'entity_id': self.entity_id,
            'click_type': click_type
        })
        self._last_action = click_type

        return True


class XiaomiCube(XiaomiBinarySensor):
    """Representation of a Xiaomi Cube."""

    def __init__(self, device, hass, xiaomi_hub):
        """Initialize the Xiaomi Cube."""
        self._hass = hass
        self._last_action = None
        self._state = False
        if 'proto' not in device or int(device['proto'][0:1]) == 1:
            data_key = 'status'
        else:
            data_key = 'cube_status'
        XiaomiBinarySensor.__init__(self, device, 'Cube', xiaomi_hub,
                                    data_key, None)

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {ATTR_LAST_ACTION: self._last_action}
        attrs.update(super().device_state_attributes)
        return attrs

    def parse_data(self, data, raw_data):
        """Parse data sent by gateway."""
        if self._data_key in data:
            self._hass.bus.fire('xiaomi_aqara.cube_action', {
                'entity_id': self.entity_id,
                'action_type': data[self._data_key]
            })
            self._last_action = data[self._data_key]

        if 'rotate' in data:
            self._hass.bus.fire('xiaomi_aqara.cube_action', {
                'entity_id': self.entity_id,
                'action_type': 'rotate',
                'action_value': float(data['rotate'].replace(",", "."))
            })
            self._last_action = 'rotate'

        if 'rotate_degree' in data:
            self._hass.bus.fire('xiaomi_aqara.cube_action', {
                'entity_id': self.entity_id,
                'action_type': 'rotate',
                'action_value': float(data['rotate_degree'].replace(",", "."))
            })
            self._last_action = 'rotate'

        return True