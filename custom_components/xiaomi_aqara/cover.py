"""Support for Xiaomi curtain."""
import logging

from homeassistant.components.cover import CoverDevice, ATTR_POSITION
from homeassistant.components.xiaomi_aqara import (PY_XIAOMI_GATEWAY,
                                                   XiaomiDevice)

_LOGGER = logging.getLogger(__name__)

ATTR_CURTAIN_LEVEL = 'curtain_level'


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Perform the setup for Xiaomi devices."""
    devices = []
    for (_, gateway) in hass.data[PY_XIAOMI_GATEWAY].gateways.items():
        for device in gateway.devices['cover']:
            model = device['model']
            if model == 'curtain':
                devices.append(XiaomiGenericCover(device, "Curtain",
                                                  'status', gateway))
    add_entities(devices)


class XiaomiGenericCover(XiaomiDevice, CoverDevice):
    """Representation of a XiaomiGenericCover."""

    def __init__(self, device, name, data_key, xiaomi_hub):
        """Initialize the XiaomiGenericCover."""
        self._data_key = data_key
        self._pos = 0
        XiaomiDevice.__init__(self, device, name, xiaomi_hub)

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        return self._pos

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self.current_cover_position <= 0

    def close_cover(self, **kwargs):
        """Close the cover."""
        self._write_to_hub(self._sid, **{self._data_key: 'close'})

    def open_cover(self, **kwargs):
        """Open the cover."""
        self._write_to_hub(self._sid, **{self._data_key: 'open'})

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        self._write_to_hub(self._sid, **{self._data_key: 'stop'})

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs.get(ATTR_POSITION)
        self._write_to_hub(self._sid, **{ATTR_CURTAIN_LEVEL: str(position)})

    def parse_data(self, data, raw_data):
        """Parse data sent by gateway."""
        if ATTR_CURTAIN_LEVEL in data:
            self._pos = int(data[ATTR_CURTAIN_LEVEL])
            return True
        return False