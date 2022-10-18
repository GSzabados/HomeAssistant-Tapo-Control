from homeassistant.core import HomeAssistant

from homeassistant.components.button import ButtonDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER
from .tapo.entities import TapoButtonEntity
from .utils import syncTime, check_and_create


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    LOGGER.debug("Setting up buttons")
    entry = hass.data[DOMAIN][config_entry.entry_id]

    buttons = []
    buttons.append(TapoRebootButton(entry, hass, config_entry))
    buttons.append(TapoFormatButton(entry, hass, config_entry))
    buttons.append(TapoStartManualAlarmButton(entry, hass, config_entry))
    buttons.append(TapoStopManualAlarmButton(entry, hass, config_entry))
    buttons.append(TapoSyncTimeButton(entry, hass, config_entry))

    tapoCalibrateButton = await check_and_create(
        entry, hass, TapoCalibrateButton, "getPresets", config_entry
    )
    if tapoCalibrateButton:
        buttons.append(tapoCalibrateButton)
        buttons.append(TapoMoveUpButton(entry, hass, config_entry))
        buttons.append(TapoMoveDownButton(entry, hass, config_entry))
        buttons.append(TapoMoveRightButton(entry, hass, config_entry))
        buttons.append(TapoMoveLeftButton(entry, hass, config_entry))
    else:
        LOGGER.info("Buttons: Camera does not support movement.")

    async_add_entities(buttons)


class TapoRebootButton(TapoButtonEntity):
    def __init__(self, entry: dict, hass: HomeAssistant, config_entry):
        TapoButtonEntity.__init__(self, "Reboot", entry, hass)

    async def async_press(self) -> None:
        await self._hass.async_add_executor_job(self._controller.reboot)

    @property
    def device_class(self) -> str:
        return ButtonDeviceClass.RESTART


class TapoFormatButton(TapoButtonEntity):
    def __init__(self, entry: dict, hass: HomeAssistant, config_entry):
        TapoButtonEntity.__init__(self, "Format SD Card", entry, hass, "mdi:eraser")

    async def async_press(self) -> None:
        await self._hass.async_add_executor_job(self._controller.format)


class TapoSyncTimeButton(TapoButtonEntity):
    def __init__(self, entry: dict, hass: HomeAssistant, config_entry):
        self._entry_id = config_entry.entry_id
        TapoButtonEntity.__init__(
            self, "Sync Time", entry, hass, "mdi:timer-sync-outline",
        )

    async def async_press(self) -> None:
        await syncTime(self._hass, self._entry_id)


class TapoStartManualAlarmButton(TapoButtonEntity):
    def __init__(self, entry: dict, hass: HomeAssistant, config_entry):
        TapoButtonEntity.__init__(self, "Manual Alarm Start", entry, hass, "mdi:alarm")

    async def async_press(self) -> None:
        await self._hass.async_add_executor_job(self._controller.startManualAlarm)


class TapoStopManualAlarmButton(TapoButtonEntity):
    def __init__(self, entry: dict, hass: HomeAssistant, config_entry):
        TapoButtonEntity.__init__(
            self, "Manual Alarm Stop", entry, hass, "mdi:alarm-off",
        )

    async def async_press(self) -> None:
        await self._hass.async_add_executor_job(self._controller.stopManualAlarm)


class TapoCalibrateButton(TapoButtonEntity):
    def __init__(self, entry: dict, hass: HomeAssistant, config_entry):
        TapoButtonEntity.__init__(self, "Calibrate", entry, hass)

    async def async_press(self) -> None:
        await self._hass.async_add_executor_job(self._controller.calibrateMotor)


class TapoMoveUpButton(TapoButtonEntity):
    def __init__(self, entry: dict, hass: HomeAssistant, config_entry):
        TapoButtonEntity.__init__(self, "Move Up", entry, hass, "mdi:arrow-up")

    async def async_press(self) -> None:
        degrees = self._entry["movement_angle"]
        await self._hass.async_add_executor_job(self._controller.moveMotor, 0, degrees)
        await self._coordinator.async_request_refresh()


class TapoMoveDownButton(TapoButtonEntity):
    def __init__(self, entry: dict, hass: HomeAssistant, config_entry):
        TapoButtonEntity.__init__(self, "Move Down", entry, hass, "mdi:arrow-down")

    async def async_press(self) -> None:
        degrees = self._entry["movement_angle"]
        await self._hass.async_add_executor_job(self._controller.moveMotor, 0, -degrees)
        await self._coordinator.async_request_refresh()


class TapoMoveRightButton(TapoButtonEntity):
    def __init__(self, entry: dict, hass: HomeAssistant, config_entry):
        TapoButtonEntity.__init__(self, "Move Right", entry, hass, "mdi:arrow-right")

    async def async_press(self) -> None:
        degrees = self._entry["movement_angle"]
        await self._hass.async_add_executor_job(self._controller.moveMotor, degrees, 0)
        await self._coordinator.async_request_refresh()


class TapoMoveLeftButton(TapoButtonEntity):
    def __init__(self, entry: dict, hass: HomeAssistant, config_entry):
        TapoButtonEntity.__init__(self, "Move Left", entry, hass, "mdi:arrow-left")

    async def async_press(self) -> None:
        degrees = self._entry["movement_angle"]
        await self._hass.async_add_executor_job(self._controller.moveMotor, -degrees, 0)
        await self._coordinator.async_request_refresh()
