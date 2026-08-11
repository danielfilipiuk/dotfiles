# Theme Creator Plugin for Cura
# Copyright (C) 2025 HellAholic
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


from UM.Extension import Extension
from UM.Logger import Logger
from UM.i18n import i18nCatalog

from .ThemeCreatorDialog import ThemeCreatorDialog

class ThemeCreator(Extension):
    """Main Theme Creator extension class."""
    
    def __init__(self):
        super().__init__()
        
        self._dialog = None
        
        # Set up menu item
        self.setMenuName(i18nCatalog("cura").i18nc("@item:inmenu", "Theme Creator"))
        self.addMenuItem(i18nCatalog("cura").i18nc("@item:inmenu", "Create Theme"), self.showDialog)
        
        Logger.info("Theme Creator extension loaded")
    
    def showDialog(self):
        """Show the theme creator dialog."""
        if self._dialog is None:
            self._dialog = ThemeCreatorDialog()
        
        self._dialog.show()
        Logger.info("Theme Creator dialog opened")
