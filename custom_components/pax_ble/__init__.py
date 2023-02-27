"""Support for Pax fans."""
import logging
import async_timeout

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_NAME,
    CONF_MAC,
    CONF_PIN,
    CONF_SCAN_INTERVAL,
    CONF_SCAN_INTERVAL_FAST
)
from .coordinator import PaxCalimaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry):
    # Set up platform from a ConfigEntry."""
    _LOGGER.debug("Setting up entry: %s", config_entry.data[CONF_NAME])
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = config_entry.data

    # Load config data
    name = config_entry.data[CONF_NAME]
    mac = config_entry.data[CONF_MAC]
    pin = config_entry.data[CONF_PIN]
    scan_interval = config_entry.data[CONF_SCAN_INTERVAL]
    scan_interval_fast = config_entry.data[CONF_SCAN_INTERVAL_FAST]

    # Set up coordinator
    coordinator = PaxCalimaCoordinator(hass, name, mac, pin, scan_interval, scan_interval_fast)
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    # Load device information data (model name etc)
    try:
        async with async_timeout.timeout(20):
            await coordinator.read_deviceinfo(disconnect=False)
    except Exception as err:
        _LOGGER.debug("Failed when loading device information: " + str(err))

    # Forward the setup to the platforms.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    )

    # Set up options listener
    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))

    return True


async def update_listener(hass, config_entry):
    _LOGGER.debug("Update entry: %s", config_entry.data[CONF_NAME])
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    _LOGGER.debug("Unload entry: %s", config_entry.data[CONF_NAME])

    # Make sure we are disconnected
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    await coordinator.disconnect()

    # Unload entries
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )

    return unload_ok
