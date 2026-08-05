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

class PluginConstants:
    """Constants and styling for the Theme Creator plugin."""
    
    # Default theme structure keys
    THEME_SECTIONS = {
        'METADATA': 'metadata',
        'FONTS': 'fonts',
        'BASE_COLORS': 'base_colors',
        'COLORS': 'colors',
        'SIZES': 'sizes'
    }
    
    # File extensions and filters
    FILE_FILTERS = {
        'THEME_FILES': "Cura Theme Files (*.curapackage);;JSON Files (*.json);;All Files (*)",
        'JSON_FILES': "JSON Files (*.json);;All Files (*)"
    }
    
    # Default theme metadata
    DEFAULT_THEME = {
        'name': 'Custom Theme',
        'inherits': 'cura-light'
    }
    
    # Color scheme (improved for better consistency)
    COLORS = {
        'background_primary': "#E9E9E9",
        'background_secondary': "#E5E5E5",
        'border_light': '#dee2e6',
        'border_medium': '#adb5bd',
        'border_dark': '#6c757d',
        'text_primary': '#212529',
        'text_secondary': '#6c757d',
        'text_muted': "#e5e6e8",
        'accent_blue': '#0d6efd',
        'accent_hover': '#0b5ed7',
        'success_green': '#198754',
        'warning_orange': '#fd7e14',
        'error_red': '#dc3545'
    }
    
    # UI Dimensions (optimized for better proportions)
    DIMENSIONS = {
        'border_radius': '4px',
        'padding_small': '4px',
        'padding_medium': '8px',
        'padding_large': '12px',
        'font_control_width': '140px',
        'input_height': '24px',
        'button_height': '24px',
        'color_button_size': '120px',
        # Dialog dimensions
        'dialog_width': 800,
        'dialog_height': 650,
        'loading_widget_width': 500,
        'loading_widget_height': 300,
        'color_button_width': 122,
        'color_button_height': 30
    }
    
    # Styling for different components
    STYLES = {
        'main_dialog': """
            QDialog {{
                background-color: {background_primary};
            }}
            QTabWidget::pane {{
                border: 1px solid {border_light};
                border-radius: {border_radius};
                background-color: {background_primary};
                padding: {padding_medium};
            }}
            QTabBar::tab {{
                background-color: {border_light};
                color: {text_primary};
                padding: {padding_small} {padding_medium};
                margin-right: 2px;
                border-top-left-radius: {border_radius};
                border-top-right-radius: {border_radius};
                border: 1px solid {border_light};
            }}
            QTabBar::tab:selected {{
                background-color: {background_primary};
                border-bottom: 2px solid {accent_blue};
            }}
        """,
        
        'loading_widget': """
            QWidget {{
                background-color: {background_primary};
                border: 1px solid {border_light};
                border-radius: {border_radius};
                padding: {padding_medium};
            }}
        """,
        
        'scale_frame': """
            QFrame {{
                background-color: {background_primary};
                border: 1px solid {border_light};
                border-radius: {border_radius};
                padding: {padding_medium};
                margin: 2px;
            }}
        """,
        
        'group_box': """
            QGroupBox {{
                font-weight: bold;
                font-size: 13px;
                color: {text_primary};
                border: 1px solid {border_light};
                border-radius: {border_radius};
                margin: 6px 2px;
                padding-top: 12px;
                background-color: transparent;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 6px 0 6px;
                color: {text_primary};
                background-color: {background_primary};
            }}
        """,
        
        'font_preview': """
            QFrame {{
                background-color: {background_secondary};
                border: 1px solid {border_light};
                border-radius: {border_radius};
                padding: {padding_medium};
            }}
            QFrame QLabel {{
                background-color: transparent;
                padding: 2px 4px;
                margin: 1px 0px;
                color: {text_primary};
            }}
            QFrame QFrame {{
                background-color: transparent;
                border: none;
                margin: 1px;
                padding: 1px;
            }}
        """,
        
        'scale_label': """
            QLabel {{
                font-weight: bold;
                font-size: 14px;
                color: {text_primary};
                margin: 0px 5px;
            }}
        """,
        
        'scale_value_label': """
            QLabel {{
                font-weight: bold;
                font-size: 14px;
                color: {accent_blue};
                min-width: 35px;
                margin: 0px 5px;
            }}
        """,
        
        'scale_info_label': """
            QLabel {{
                color: {text_secondary};
                font-style: italic;
                font-size: 12px;
                margin: 0px 5px;
            }}
        """,
        
        'slider': """
            QSlider::groove:horizontal {{
                border: 1px solid {border_medium};
                height: 6px;
                background: {background_primary};
                margin: 2px 0;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {accent_blue};
                border: 1px solid {border_dark};
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {accent_hover};
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {accent_blue};
                border: 1px solid {border_medium};
                height: 6px;
                border-radius: 3px;
            }}
        """,
        
        'scroll_area': """
            QScrollArea {{
                border: none;
                background-color: transparent;
                border-radius: {border_radius};
            }}
            QScrollArea QWidget {{
                background-color: {background_secondary};
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {background_secondary};
            }}
            QScrollBar:vertical {{
                background-color: {background_primary};
                width: 14px;
                border: 1px solid {border_light};
                border-radius: 7px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {border_medium};
                border: 1px solid {border_dark};
                border-radius: 6px;
                min-height: 20px;
                margin: 1px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {accent_blue};
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:pressed {{
                background-color: {accent_hover};
                border-radius: 6px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                border: none;
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            QScrollBar:horizontal {{
                background-color: {background_primary};
                height: 14px;
                border: 1px solid {border_light};
                border-radius: 7px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {border_medium};
                border: 1px solid {border_dark};
                border-radius: 6px;
                min-width: 20px;
                margin: 1px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {accent_blue};
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:pressed {{
                background-color: {accent_hover};
                border-radius: 6px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
                border: none;
                background: none;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: transparent;
            }}
        """,
        
        'tab_widget': """
            QTabWidget::pane {{
                border: 1px solid {border_light};
                border-radius: 6px;
                background-color: {background_secondary};
                padding: 5px;
            }}
            QTabBar::tab {{
                background-color: {background_primary};
                border: 1px solid {border_medium};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background-color: {background_secondary};
                border-bottom-color: {background_secondary};
            }}
            QTabBar::tab:hover {{
                background-color: {border_light};
            }}
        """,
        
        'button_primary': """
            QPushButton {{
                background-color: {accent_blue};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {accent_hover};
                border-radius: 4px;
            }}
            QPushButton:pressed {{
                background-color: {accent_hover};
                border-radius: 4px;
                padding: 9px 15px 7px 17px;
            }}
            QPushButton:disabled {{
                background-color: {border_medium};
                color: {text_muted};
            }}
        """,
        
        'button_secondary': """
            QPushButton {{
                background-color: {background_secondary};
                color: {text_primary};
                border: 1px solid {border_medium};
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {border_light};
                border-color: {accent_blue};
                border-radius: 4px;
            }}
            QPushButton:pressed {{
                background-color: {border_medium};
                padding: 9px 15px 7px 17px;
                border-radius: 4px;
            }}
        """,
        
        'line_edit': """
            QLineEdit {{
                border: 1px solid {border_medium};
                border-radius: 4px;
                padding: 6px;
                background-color: {background_secondary};
                selection-background-color: {accent_blue};
            }}
            QLineEdit:focus {{
                border-color: {accent_blue};
            }}
        """,
        
        'spin_box': """
            QDoubleSpinBox {{
                border: 1px solid {border_medium};
                border-radius: 4px;
                padding: 4px;
                background-color: {background_secondary};
            }}
            QDoubleSpinBox:focus {{
                border-color: {accent_blue};
            }}
        """,
        
        'combo_box': """
            QComboBox {{
                border: 1px solid {border_medium};
                border-radius: 4px;
                padding: 4px;
                background-color: {background_secondary};
                min-width: 6em;
            }}
            QComboBox:focus {{
                border-color: {accent_blue};
                border-radius: 4px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: {border_medium};
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}
        """,
        
        'progress_bar': """
            QProgressBar {{
                border: 1px solid {border_medium};
                border-radius: {border_radius};
                text-align: center;
                font-weight: bold;
                background-color: {background_primary};
                min-height: {input_height};
                color: {text_primary};
            }}
            QProgressBar::chunk {{
                background-color: {accent_blue};
                border-radius: 4px;
                margin: 1px;
            }}
        """,
        
        'input_controls': """
            QDoubleSpinBox, QComboBox, QLineEdit {{
                min-height: {input_height};
                max-width: {font_control_width};
                border: 1px solid {border_light};
                border-radius: {border_radius};
                padding: 2px 6px;
                background-color: {background_primary};
                color: {text_primary};
                font-size: 11px;
            }}
            QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus {{
                border: 2px solid {accent_blue};
            }}
            QFontComboBox {{
                min-height: {input_height};
                max-width: {font_control_width};
                border: 1px solid {border_light};
                border-radius: {border_radius};
                padding: 2px 6px;
                background-color: {background_primary};
                color: {text_primary};
                font-size: 11px;
            }}
            QFontComboBox:focus {{
                border: 2px solid {accent_blue};
            }}
        """,
        
        # Consolidated input controls with comprehensive styling
        'input': """
            QDoubleSpinBox, QComboBox, QLineEdit, QFontComboBox {{
                min-height: {input_height};
                max-width: {font_control_width};
                border: 1px solid {border_medium};
                border-radius: {border_radius};
                padding: 2px 6px;
                background-color: white;
                color: {text_primary};
                font-size: 11px;
            }}
            QDoubleSpinBox:focus, QComboBox:focus, QLineEdit:focus, QFontComboBox:focus {{
                border: 2px solid {accent_blue};
                background-color: white;
            }}
            QDoubleSpinBox {{
                padding-right: 18px;
            }}
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                width: 16px;
                height: 11px;
                border: 1px solid {border_medium};
                background-color: {border_light};
                border-radius: 2px;
                margin: 1px;
            }}
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {accent_blue};
                border-color: {accent_blue};
                border-radius: 2px;
            }}
            QDoubleSpinBox::up-button:pressed, QDoubleSpinBox::down-button:pressed {{
                background-color: {accent_hover};
                border-radius: 2px;
            }}
            QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {{
                width: 8px;
                height: 8px;
            }}
            QDoubleSpinBox::up-arrow {{
                image: url({up_arrow_path});
            }}
            QDoubleSpinBox::down-arrow {{
                image: url({down_arrow_path});
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 18px;
                border-left: 1px solid {border_medium};
                background-color: {border_light};
                border-radius: 0px 3px 3px 0px;
            }}
            QComboBox::drop-down:hover {{
                background-color: {accent_blue};
                border-radius: 3px;
            }}
            QComboBox::down-arrow {{
                width: 8px;
                height: 8px;
                image: url({down_arrow_path});
            }}
        """,
        
        'button': """
            QPushButton {{
                background-color: {accent_blue};
                color: white;
                border: none;
                border-radius: {border_radius};
                padding: {padding_small} {padding_medium};
                font-weight: bold;
                height: {button_height};
                font-size: 13px;
                min-width: 90px;
            }}
            QPushButton:hover {{
                background-color: {accent_hover};
                border-radius: {border_radius};
            }}
            QPushButton:pressed {{
                background-color: {border_dark};
                border-radius: {border_radius};
            }}
            QPushButton:disabled {{
                background-color: {border_medium};
                border-radius: {border_radius};
                color: {text_muted};
            }}
        """,

        'category_header': """
            QLabel {{
                font-weight: bold;
                font-size: 14px;
                color: #333;
                margin: 10px 0 5px 0;
            }}
        """,

        'font_container': """
            QFrame {{
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                margin: 2px 0;
            }}
        """,

        'controls_container': """
            QFrame {{
                background-color: #f8f9fa;
                border: none;
            }}
            QFrame QLabel {{
                background-color: transparent;
                border: none;
            }}
            QFrame QWidget {{
                background-color: transparent;
                border: none;
            }}
        """,

        'controls_widget': """
            QWidget {{
                background-color: transparent;
                border: none;
            }}
        """,

        'font_name_label': """
            QLabel {{
                font-weight: bold;
                border: none;
                color: #333;
                font-size: 13px;
                background-color: transparent;
            }}
        """,

        'control_label': """
            QLabel {{
                color: #333;
                border: none;
                background-color: transparent;
            }}
        """,

        'preview_container': """
            QFrame {{
                background-color: #f8f9fa;
                border-radius: 4px;
            }}
        """,

        'preview_header': """
            QLabel {{
                font-weight: bold;
                color: #6c757d;
                font-size: 11px;
                border: none;
            }}
        """,

        'preview_label': """
            QLabel {{
                color: #212529;
                padding: 8px 0;
                border: none;
            }}
        """,

        'font_preview_type_label': """
            QLabel {{
                font-weight: bold;
                color: #6c757d;
                font-size: 11px;
            }}
        """,

        'font_preview_text_label': """
            QLabel {{
                color: #212529;
            }}
        """,

        'color_label': """
            QLabel {{
                color: {text_primary};
                background-color: transparent;
                border: none;
                font-size: 12px;
            }}
        """
    }
    
    @classmethod
    def get_icon_path(cls, icon_name: str) -> str:
        """Get absolute path to an icon file."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "icons", icon_name).replace("\\", "/")
    
    @classmethod
    def get_style(cls, style_name: str) -> str:
        """Get a formatted style string with color and dimension values."""
        if style_name not in cls.STYLES:
            return ""
        
        try:
            style = cls.STYLES[style_name]
            
            # Combine colors, dimensions, and icon paths for formatting
            format_values = {
                **cls.COLORS, 
                **cls.DIMENSIONS,
                'up_arrow_path': cls.get_icon_path('ChevronSingleUp.svg'),
                'down_arrow_path': cls.get_icon_path('ChevronSingleDown.svg')
            }
            
            return style.format(**format_values)
        except (KeyError, ValueError) as e:
            # Silently return empty string for graceful degradation
            # Using print instead of Logger to avoid circular imports
            # This is a non-critical styling error that shouldn't crash the app
            return ""
    
    @classmethod
    def get_color(cls, color_name: str) -> str:
        """Get a color value by name."""
        return cls.COLORS.get(color_name, "#000000")
