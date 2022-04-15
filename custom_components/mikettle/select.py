from . import DOMAIN
from homeassistant.components.select import SelectEntity
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from mikettle.mikettle import MiKettle
from homeassistant.const import (
    CONF_FORCE_UPDATE,
    CONF_MAC,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    EVENT_HOMEASSISTANT_START,
)
from .const import(
    CONF_PRODUCT_ID,
    DEFAULT_PRODUCT_ID,
    DEFAULT_FORCE_UPDATE,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    SENSOR_TYPES,
)
from mikettle.mikettle import (
    MI_KW_TYPE,
    MI_KW_TYPE_MAP,
    MI_CURRENT_TEMPERATURE,
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities,
    discovery_info=None
) -> None:
    """Set up the MiKettle sensor."""
    _LOGGER.debug(f"Running setup_platform for `select` with config {config}")

    poller: MiKettle = hass.data[DOMAIN]["mikettle"]
    config: dict = hass.data[DOMAIN]["config"]
    force_update = config["force_update"]
    devs = []

    for parameter in config[CONF_MONITORED_CONDITIONS]:
        name = SENSOR_TYPES[parameter][0]
        unit = SENSOR_TYPES[parameter][1]
        icon = SENSOR_TYPES[parameter][2]

        prefix = config.get(CONF_NAME)
        if prefix:
            name = f"{prefix} {name}"
        
        if parameter == MI_KW_TYPE:
            _LOGGER.debug(f"Creating entity [{name = }] for {parameter = }")
            devs.append(
                MiKettleKwType(poller, parameter, name, unit, icon, force_update)
            )

    async_add_entities(devs)


class MiKettleKwType(SelectEntity):
    def __init__(self, poller, parameter, name, unit, icon, force_update):
        """Initialize the sensor."""
        self.poller = poller
        self.parameter = parameter
        self._unit = unit
        self._icon = icon
        self._name = name
        self._state = None
        self._force_update = force_update

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def current_option(self) -> str:
        return self._state

    @property
    def options(self) -> list[str]:
        return list(MI_KW_TYPE_MAP.values())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        kw_type_idx = [k for k, v in MI_KW_TYPE_MAP.items() if v == option][0]
        _LOGGER.debug(f"Will set KW type to [{option=}, value={kw_type_idx}], temperature={self.poller.parameter_value(MI_CURRENT_TEMPERATURE)}")
        self.poller.setKW(
            kw_type_idx,
            80 # temporary hardcode, because set temperature has been reset accidentally
            # self.poller.parameter_value(MI_SET_TEMPERATURE)
        )
        ## todo: invalidate cache? or update value in cache. should be done in the library

    async def async_update(self):
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
