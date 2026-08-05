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

import os
import json
from typing import Dict, List, Any, Tuple
from UM.Logger import Logger

class ThemeConfigLoader:
    """Loads and manages theme configuration from JSON files."""
    
    def __init__(self, config_file_path: str = None):
        """Initialize the config loader.
        
        Args:
            config_file_path: Path to the theme configuration JSON file.
                             If None, looks for theme_config.json in the same directory.
        """
        if config_file_path is None:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_file_path = os.path.join(script_dir, "theme_config.json")
        
        self.config_file_path = config_file_path
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load the configuration from the JSON file."""
        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
                self._validate_config()
        except FileNotFoundError as e:
            # Log the error and provide a default configuration
            Logger.error(f"Theme configuration file not found: {self.config_file_path}")
            self._config = self._get_default_config()
        except json.JSONDecodeError as e:
            # Log the error and provide a default configuration
            Logger.error(f"Invalid JSON in theme configuration file: {e}")
            self._config = self._get_default_config()
        except Exception as e:
            # Catch any other unexpected errors and use defaults
            Logger.error(f"Unexpected error loading configuration: {e}")
            self._config = self._get_default_config()
    
    def _validate_config(self) -> None:
        """Validate the loaded configuration structure and fix issues automatically."""
        # Safely handle invalid config without raising exceptions
        if not isinstance(self._config, dict):
            Logger.warning("Configuration is not a dictionary, using defaults")
            self._config = self._get_default_config()
            return
        
        required_sections = ["fonts", "colors", "sizes"]
        for section in required_sections:
            if section not in self._config:
                Logger.warning(f"Missing section '{section}' in configuration, using defaults")
                self._config[section] = {"items": []}
            elif not isinstance(self._config[section], dict) or "items" not in self._config[section]:
                Logger.warning(f"Invalid section '{section}' structure, using defaults")
                self._config[section] = {"items": []}
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get a minimal default configuration when config file is not available."""
        return {
            "fonts": {
                "items": [
                    {"key": "default", "label": "Default Font", "category": "Standard Fonts", 
                     "value": {"size": 1.0, "weight": 400, "family": "Noto Sans"}}
                ]
            },
            "colors": {
                "items": [
                    {"key": "primary", "label": "Primary Color", "category": "General Colors", 
                     "type": "base_color", "value": [50, 50, 50, 255]}
                ]
            },
            "sizes": {
                "items": [
                    {"key": "default_size", "label": "Default Size", "category": "General Sizes", 
                     "value": [1.0, 1.0]}
                ]
            }
        }
    
    def get_font_categories(self) -> List[Tuple[str, List[Dict[str, str]]]]:
        """Get font categories with their items.
        
        Returns:
            List of tuples containing (category_name, font_items_list)
            where font_items_list contains dicts with 'key', 'label', and other properties
        """
        categories = []
        if "fonts" in self._config and "items" in self._config["fonts"]:
            # Group items by category
            categorized_items = {}
            for item in self._config["fonts"]["items"]:
                category = item.get("category", "Standard Fonts")
                if category not in categorized_items:
                    categorized_items[category] = []
                categorized_items[category].append(item)
            
            # Convert to list of tuples
            for category_name, items in categorized_items.items():
                categories.append((category_name, items))
        return categories
    
    def get_color_categories(self) -> List[Tuple[str, List[Dict[str, str]], bool]]:
        """Get color categories with their items.
        
        Returns:
            List of tuples containing (category_name, color_items_list, is_base_colors)
            where color_items_list contains dicts with 'key', 'label', and other properties
            and is_base_colors indicates if these should go in base_colors section
        """
        categories = []
        if "colors" in self._config and "items" in self._config["colors"]:
            # Group items by category
            categorized_items = {}
            for item in self._config["colors"]["items"]:
                category = item.get("category", "General Colors")
                if category not in categorized_items:
                    categorized_items[category] = []
                categorized_items[category].append(item)
            
            # Convert to list of tuples, check if category contains base colors
            for category_name, items in categorized_items.items():
                # Determine if this category contains base colors by checking item types
                is_base_colors = any(item.get("type") == "base_color" for item in items)
                categories.append((category_name, items, is_base_colors))
        return categories
    
    def get_size_categories(self) -> List[Tuple[str, List[Dict[str, str]]]]:
        """Get size categories with their items.
        
        Returns:
            List of tuples containing (category_name, size_items_list)
            where size_items_list contains dicts with 'key', 'label', and other properties
        """
        categories = []
        if "sizes" in self._config and "items" in self._config["sizes"]:
            # Group items by category
            categorized_items = {}
            for item in self._config["sizes"]["items"]:
                category = item.get("category", "General Sizes")
                if category not in categorized_items:
                    categorized_items[category] = []
                categorized_items[category].append(item)
            
            # Convert to list of tuples
            for category_name, items in categorized_items.items():
                categories.append((category_name, items))
        return categories
    
    def get_font_info(self, font_key: str) -> Dict[str, str]:
        """Get information about a specific font key.
        
        Args:
            font_key: The font key to look up
            
        Returns:
            Dict with 'label' and 'description' for the font, or default values if not found
        """
        for category_name, items in self.get_font_categories():
            for item in items:
                if item.get("key") == font_key:
                    return {
                        "label": item.get("label", font_key),
                        "description": item.get("description", f"Font: {font_key}")
                    }
        return {"label": font_key, "description": f"Font: {font_key}"}
    
    def get_color_info(self, color_key: str) -> Dict[str, str]:
        """Get information about a specific color key.
        
        Args:
            color_key: The color key to look up
            
        Returns:
            Dict with 'label' and 'description' for the color, or default values if not found
        """
        for category_name, items, is_base_colors in self.get_color_categories():
            for item in items:
                if item.get("key") == color_key:
                    return {
                        "label": item.get("label", color_key),
                        "description": item.get("description", f"Color: {color_key}")
                    }
        return {"label": color_key, "description": f"Color: {color_key}"}
    
    def get_size_info(self, size_key: str) -> Dict[str, str]:
        """Get information about a specific size key.
        
        Args:
            size_key: The size key to look up
            
        Returns:
            Dict with 'label' and 'description' for the size, or default values if not found
        """
        for category_name, items in self.get_size_categories():
            for item in items:
                if item.get("key") == size_key:
                    return {
                        "label": item.get("label", size_key),
                        "description": item.get("description", f"Size: {size_key}")
                    }
        return {"label": size_key, "description": f"Size: {size_key}"}
    
    def get_default_font_value(self, font_key: str) -> Dict[str, Any]:
        """Get default value for a font key.
        
        Args:
            font_key: The font key to get default for
            
        Returns:
            Dictionary with font properties (size, weight, family, etc.)
        """
        # Look for the font in the items array
        if "fonts" in self._config and "items" in self._config["fonts"]:
            for item in self._config["fonts"]["items"]:
                if item.get("key") == font_key:
                    return item.get("value", {"size": 1.0, "weight": 400, "family": "Noto Sans"})
        
        return {"size": 1.0, "weight": 400, "family": "Noto Sans"}
    
    def get_default_color_value(self, color_key: str) -> List[int]:
        """Get default value for a color key.
        
        Args:
            color_key: The color key to get default for
            
        Returns:
            List of RGBA values [r, g, b, a]
        """
        # Look for the color in the items array
        if "colors" in self._config and "items" in self._config["colors"]:
            for item in self._config["colors"]["items"]:
                if item.get("key") == color_key:
                    return item.get("value", [128, 128, 128, 255])
        
        return [128, 128, 128, 255]  # Default gray
    
    def get_default_size_value(self, size_key: str) -> List[float]:
        """Get default value for a size key.
        
        Args:
            size_key: The size key to get default for
            
        Returns:
            List of [width, height] values
        """
        # Look for the size in the items array
        if "sizes" in self._config and "items" in self._config["sizes"]:
            for item in self._config["sizes"]["items"]:
                if item.get("key") == size_key:
                    return item.get("value", [1.0, 1.0])
        
        return [1.0, 1.0]

    def is_base_color(self, color_key: str) -> bool:
        """Check if a color key should be stored in base_colors section.
        
        Args:
            color_key: The color key to check
            
        Returns:
            True if the color should go in base_colors, False otherwise
        """
        if "colors" in self._config and "items" in self._config["colors"]:
            for item in self._config["colors"]["items"]:
                if item.get("key") == color_key:
                    return item.get("type") == "base_color"
        return False
    
    def get_all_font_keys(self) -> List[str]:
        """Get all available font keys."""
        keys = []
        if "fonts" in self._config and "items" in self._config["fonts"]:
            for item in self._config["fonts"]["items"]:
                if "key" in item:
                    keys.append(item["key"])
        return keys
    
    def get_all_color_keys(self) -> List[str]:
        """Get all available color keys."""
        keys = []
        if "colors" in self._config and "items" in self._config["colors"]:
            for item in self._config["colors"]["items"]:
                if "key" in item:
                    keys.append(item["key"])
        return keys
    
    def get_all_size_keys(self) -> List[str]:
        """Get all available size keys."""
        keys = []
        if "sizes" in self._config and "items" in self._config["sizes"]:
            for item in self._config["sizes"]["items"]:
                if "key" in item:
                    keys.append(item["key"])
        return keys
