"""Support for Xiaomi Mi Kettle BLE."""
from . import DOMAIN
from datetime import timedelta
import logging

from mikettle.mikettle import MiKettle
from mikettle.mikettle import (
    MI_KW_TYPE,
)
from .const import(
    CONF_PRODUCT_ID,
    DEFAULT_PRODUCT_ID,
    DEFAULT_FORCE_UPDATE,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    SENSOR_TYPES,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import (
    CONF_FORCE_UPDATE,
    CONF_MAC,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    EVENT_HOMEASSISTANT_START,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities,
    discovery_info=None
) -> None:
    """Set up the MiKettle sensor."""
    _LOGGER.debug(f"Running setup_platform with config {config}")

    poller: MiKettle = hass.data[DOMAIN]["mikettle"]
    config: dict = hass.data[DOMAIN]["config"]
    _LOGGER.debug(f"Actually using config {config}")
    force_update = config["force_update"]
    devs = []

    for parameter in config[CONF_MONITORED_CONDITIONS]:
        name = SENSOR_TYPES[parameter][0]
        unit = SENSOR_TYPES[parameter][1]
        icon = SENSOR_TYPES[parameter][2]

        prefix = config.get(CONF_NAME)
        if prefix:
            name = f"{prefix} {name}"
        
        if parameter != MI_KW_TYPE:
            _LOGGER.debug(f"Creating entity [{name = }] for {parameter = }")
            devs.append(
                MiKettleSensor(poller, parameter, name, unit, icon, force_update)
            )

    async_add_entities(devs)


class MiKettleSensor(Entity):
    """Implementing the MiKettle sensor."""

    def __init__(self, poller: MiKettle, parameter, name, unit, icon, force_update):
        """Initialize the sensor."""
        self.poller = poller
        self.parameter = parameter
        self._unit = unit
        self._icon = icon
        self._name = name
        self._state = None
        self.data = []
        self._force_update = force_update

    async def async_added_to_hass(self):
        """Set initial state."""

        @callback
        def on_startup(_):
            self.async_schedule_update_ha_state(True)

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, on_startup)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the units of measurement."""
        return self._unit

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def force_update(self):
        """Force update."""
        return self._force_update

    def update(self):
        """
        Update current conditions.
        """
        try:
            _LOGGER.debug("Polling data for %s", self.name)
            data = self.poller.parameter_value(self.parameter)
        except OSError as ioerr:
            _LOGGER.info("Polling error %s", ioerr)
            return
        except Exception as bterror:
            _LOGGER.info("Polling error %s", bterror)
            return

        if data is not None:
            _LOGGER.debug("%s = %s", self.name, data)
            self._state = data
        else:
            _LOGGER.info("Did not receive any data from Mi kettle %s", self.name)
            # Remove old data from median list or set sensor value to None
            # if no data is available anymore
            self._state = None
            return
