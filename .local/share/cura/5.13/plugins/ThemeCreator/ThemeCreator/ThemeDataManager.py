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

from typing import Dict, Any
from .ThemeConfigLoader import ThemeConfigLoader

class ThemeDataManager:
    """
    Manages theme data operations including loading, saving, and validation.
    
    This class provides a high-level interface for theme data manipulation,
    built on top of ThemeConfigLoader. It handles:
    - Theme structure creation and validation
    - Default value population from configuration
    - Theme data merging and updates
    - Error handling for malformed data
    
    Attributes:
        config_loader: Instance of ThemeConfigLoader for configuration access
        default_theme_structure: Pre-built default theme structure
    """
    
    def __init__(self) -> None:
        self.config_loader = ThemeConfigLoader()
        self.default_theme_structure = self._getDefaultThemeStructure()
    
    def _getDefaultThemeStructure(self) -> Dict[str, Any]:
        """Get the default theme structure built from configuration file."""
        # Build structure from configuration instead of hardcoding
        structure = {
            "metadata": {
                "name": "Custom Theme",
                "inherits": "cura-light"
            },
            "fonts": {},
            "base_colors": {},
            "colors": {},
            "sizes": {}
        }
        
        # Initialize fonts using configuration defaults
        font_categories = self.config_loader.get_font_categories()
        for category_name, font_items in font_categories:
            for font_item in font_items:
                font_key = font_item["key"]
                structure["fonts"][font_key] = self.config_loader.get_default_font_value(font_key)
        
        # Initialize colors using configuration defaults
        color_categories = self.config_loader.get_color_categories()
        for category_name, color_items, is_base_colors in color_categories:
            target_section = "base_colors" if is_base_colors else "colors"
            
            for color_item in color_items:
                color_key = color_item["key"]
                structure[target_section][color_key] = self.config_loader.get_default_color_value(color_key)
        
        # Initialize sizes using configuration defaults
        size_categories = self.config_loader.get_size_categories()
        for category_name, size_items in size_categories:
            for size_item in size_items:
                size_key = size_item["key"]
                structure["sizes"][size_key] = self.config_loader.get_default_size_value(size_key)
        
        return structure
    
    def createNewTheme(self, name: str) -> Dict[str, Any]:
        """
        Create a new theme with the given name.
        
        Args:
            name: The name for the new theme
            
        Returns:
            Dictionary containing the complete theme structure with default values.
            If name is empty, uses a default name instead of raising an exception.
        """
        # Safely handle empty names without crashing
        safe_name = name.strip() if name and name.strip() else "Custom Theme"
        
        theme = self.default_theme_structure.copy()
        theme["metadata"]["name"] = safe_name
        return theme
    
    def validateThemeData(self, theme_data: Dict[str, Any]) -> bool:
        """
        Validate theme data structure and content.
        
        Args:
            theme_data: The theme data to validate
            
        Returns:
            True if the theme data is valid, False otherwise
        """
        if not isinstance(theme_data, dict):
            return False
        
        # Check for required sections
        required_sections = ["metadata", "fonts", "colors", "sizes"]
        for section in required_sections:
            if section not in theme_data:
                return False
        
        # Validate metadata
        metadata = theme_data.get("metadata", {})
        if not isinstance(metadata, dict) or "name" not in metadata:
            return False
        
        return True
