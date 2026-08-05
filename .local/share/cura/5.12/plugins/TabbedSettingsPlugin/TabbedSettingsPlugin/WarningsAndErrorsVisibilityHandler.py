# Copyright (c) 2023 Aldo Hoeben / fieldOfView
# The TabbedSettingsPlugin is released under the terms of the AGPLv3 or higher.

from cura.CuraApplication import CuraApplication

from UM.Settings.Models.SettingVisibilityHandler import SettingVisibilityHandler
from UM.Settings.Validator import ValidatorState

from UM.Logger import Logger

from PyQt6.QtCore import pyqtProperty, pyqtSignal, QTimer


class WarningsAndErrorsVisibilityHandler(SettingVisibilityHandler):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)

        self._active = True
        self._visible_settings = set()

        self._machine_manager = CuraApplication.getInstance().getMachineManager()
        self._machine_manager.activeStackChanged.connect(self._delayedUpdate)
        self._machine_manager.activeStackValueChanged.connect(self._delayedUpdate)

        self._updating = False

        self._update_timer = QTimer()
        self._update_timer.setInterval(10)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._update)


    def setActive(self, active: bool) -> None:
        if active == self._active:
            return

        self._active = active
        self._delayedUpdate()

    activeChanged = pyqtSignal()

    @pyqtProperty(bool, notify=activeChanged, fset=setActive)
    def active(self) -> bool:
        return self._active

    def _delayedUpdate(self) -> None:
        if not self._active:
            return

        self._update_timer.start()

    def _update(self) -> None:
        if not self._active:
            return

        global_container_stack = self._machine_manager.activeMachine
        if not global_container_stack:
            Logger.log("w", "Tried to update model, but there is no global stack")
            return

        extruder_stack = self._machine_manager.activeStack
        if not extruder_stack:
            Logger.log("w", "Tried to update model, but there is no extruder stack")
            return

        if self._updating:
            return
        self._updating = True

        visible_settings = set()
        visible_categories = set()

        for stack in [global_container_stack, extruder_stack]:
            warning_keys = stack.getErrorKeys()

            for key in stack.getAllKeys():
                if not stack.getProperty(key, "enabled") or key in warning_keys:
                    continue

                validation_state = stack.getProperty(key, "validationState")
                if validation_state in (ValidatorState.MaximumWarning, ValidatorState.MinimumWarning):
                    warning_keys.append(key)

            visible_settings.update(set(warning_keys))

            # also make the categories of these settings visible
            for setting_key in warning_keys:
                category = stack.getSettingDefinition(setting_key)
                while category is not None and category.type != "category":
                    category = category.parent
                if category is not None:
                    visible_categories.add(category.key)
            visible_settings.update(visible_categories)

            
        if self._visible_settings != visible_settings:
            self._visible_settings = visible_settings

            self.setVisible(visible_settings)

        self._updating = False