"""The mikettle component."""
from __future__ import annotations

import logging
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    CONF_FORCE_UPDATE,
    CONF_MAC,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    EVENT_HOMEASSISTANT_START,
    Platform
)
from .const import(
    CONF_PRODUCT_ID,
    DEFAULT_PRODUCT_ID,
    DEFAULT_FORCE_UPDATE,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    SENSOR_TYPES,
)
from homeassistant.helpers.typing import ConfigType
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import config_per_platform
from mikettle.mikettle import MiKettle

DOMAIN = 'mikettle'
_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        ),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PRODUCT_ID, default=DEFAULT_PRODUCT_ID): cv.positive_int,
        vol.Optional(CONF_FORCE_UPDATE, default=DEFAULT_FORCE_UPDATE): cv.boolean,
    }
)

async def async_setup(
    hass: HomeAssistant, 
    config: ConfigType
) -> bool:
    conf = list(filter(
        lambda d: d["platform"] == DOMAIN,
        config["sensor"]
    ))
    _LOGGER.debug(f"Found conf {conf}")
    conf = dict(conf[0])

    ## todo: figure out how to pass config with resolved defaults
    conf.update({
        "force_update": DEFAULT_FORCE_UPDATE,
        CONF_NAME: DEFAULT_NAME,
    })

    _LOGGER.debug(f"Setting up mikettle from conf {conf}")
    cache = conf.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL).total_seconds()
    _LOGGER.debug(f"Creating cache for {cache} seconds")
    force_update = conf.get(CONF_FORCE_UPDATE)
    poller = MiKettle(conf.get(CONF_MAC), conf.get(CONF_PRODUCT_ID), cache_timeout = cache)

    hass.data.setdefault(DOMAIN, {
        "mikettle": poller,
        "config": conf,
    })

    _LOGGER.debug(f"Will load platforms, {hass.config.components = }")
    hass.helpers.discovery.load_platform(Platform.SENSOR, DOMAIN, {}, config)
    hass.helpers.discovery.load_platform(Platform.SELECT, DOMAIN, {}, config)
    ## todo: switch for EWU, temperature input, KW time input

    return True
