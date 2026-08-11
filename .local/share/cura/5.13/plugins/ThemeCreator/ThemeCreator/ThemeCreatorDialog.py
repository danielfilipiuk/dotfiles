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
from typing import List, Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QLabel, QPushButton, QLineEdit, QDoubleSpinBox,
                             QGroupBox, QGridLayout, QScrollArea, QWidget, QFrame,
                             QColorDialog, QFontComboBox, QMessageBox, QFileDialog,
                             QComboBox, QCheckBox, QProgressBar, QSlider, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QColor, QFont

from UM.Logger import Logger
from .ThemeDataManager import ThemeDataManager
from .ThemeConfigLoader import ThemeConfigLoader
from .PluginConstants import PluginConstants
from UM.Application import Application
from UM.Preferences import Preferences
from UM.Resources import Resources



class LoadingWidget(QWidget):
    """Loading widget with progress indicator."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(PluginConstants.DIMENSIONS['loading_widget_width'], 
                         PluginConstants.DIMENSIONS['loading_widget_height'])
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create a loading label
        self.loading_label = QLabel("Loading Theme Creator...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(PluginConstants.get_style('progress_bar'))
        layout.addWidget(self.progress_bar)
        
        # Create status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    def updateProgress(self, value, status=""):
        """Update the progress bar and status."""
        self.progress_bar.setValue(value)
        if status:
            self.status_label.setText(status)
    
    def stop(self):
        """Stop method for compatibility."""
        pass

class ColorButton(QPushButton):
    """Custom button that displays and allows editing of a color."""
    
    colorChanged = pyqtSignal(list)  # Emits [r, g, b, a] values
    
    def __init__(self, color: List[int] = [200, 200, 200, 255], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._color = color[:]  # Make a copy to avoid shared reference issues
        self.setFixedSize(PluginConstants.DIMENSIONS['color_button_width'], 
                         PluginConstants.DIMENSIONS['color_button_height'])
        # Set a unique object name to target specific styling
        self.setObjectName("ColorButton")
        self.clicked.connect(self._openColorDialog)
        self._updateButton()
    
    def setColor(self, color: List[int]) -> None:
        """Set the color as [r, g, b, a] values."""
        self._color = color[:]
        self._updateButton()
        self.colorChanged.emit(self._color)
    
    def getColor(self) -> List[int]:
        """Get the color as [r, g, b, a] values."""
        return self._color[:]
    
    def _updateButton(self) -> None:
        """Update the button appearance to show the current color."""
        r, g, b, a = self._color
        # Ensure values are integers
        r, g, b, a = int(r), int(g), int(b), int(a)
        self.setStyleSheet(f"""
            QPushButton#ColorButton {{
                background-color: rgba({r}, {g}, {b}, {a});
                border: 2px solid #ccc;
                border-radius: 3px;
                min-height: 28px;
                min-width: 120px;
            }}
            QPushButton#ColorButton:hover {{
                border: 2px solid #999;
            }}
            QPushButton#ColorButton:pressed {{
                border: 2px solid #666;
            }}
        """)
    
    def _openColorDialog(self) -> None:
        """Open a color dialog to select a new color."""
        r, g, b, a = self._color
        initial_color = QColor(r, g, b, a)
        
        color = QColorDialog.getColor(initial_color, self, "Select Color", 
                                    QColorDialog.ColorDialogOption.ShowAlphaChannel)
        
        if color.isValid():
            self.setColor([color.red(), color.green(), color.blue(), color.alpha()])
    
    def cleanup(self) -> None:
        """Clean up resources when the button is no longer needed."""
        try:
            self.clicked.disconnect()
        except (RuntimeError, TypeError):
            # Signal might already be disconnected or object might be deleted
            pass
        self._color = None


class FontPreviewWidget(QFrame):
    """Widget that shows a preview of how fonts will look in Cura."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setMinimumHeight(200)
        self.setStyleSheet(PluginConstants.get_style('font_preview'))
        
        layout = QVBoxLayout(self)
        
        # Sample text for different font sizes - expanded to cover all categories
        self.preview_texts = [
            ("Large Bold", "large_bold", "Main Menu Title"),
            ("Large", "large", "Dialog Title"),
            ("Huge Bold", "huge_bold", "Header Text"),
            ("Huge", "huge", "Large Header"),
            ("Medium Bold", "medium_bold", "Section Header"),
            ("Medium", "medium", "Button Text"),
            ("Medium Italic", "medium_italic", "Emphasized Text"),
            ("Default Bold", "default_bold", "Label Text"),
            ("Default", "default", "Regular content text"),
            ("Default Italic", "default_italic", "Italic content"),
            ("Small Bold", "small_bold", "Small Header"),
            ("Small", "small", "Small text"),
            ("Small Emphasis", "small_emphasis", "Small important"),
            ("Tiny Emphasis", "tiny_emphasis", "Tiny details")
        ]
        
        self.preview_labels = {}
        
        for display_name, font_key, sample_text in self.preview_texts:
            container = QFrame()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(5, 2, 5, 2)
            
            # Font type label
            type_label = QLabel(f"{display_name}:")
            type_label.setFixedWidth(100)
            type_label.setStyleSheet(PluginConstants.get_style('font_preview_type_label'))
            container_layout.addWidget(type_label)
            
            # Preview label
            preview_label = QLabel(sample_text)
            preview_label.setStyleSheet(PluginConstants.get_style('font_preview_text_label'))
            preview_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            preview_label.setWordWrap(True)
            self.preview_labels[font_key] = preview_label
            container_layout.addWidget(preview_label)
            
            container_layout.addStretch()
            layout.addWidget(container)
        
        layout.addStretch()
    
    def updateFontPreview(self, font_key, family, size, weight, italic=False):
        """Update the preview for a specific font."""
        if font_key in self.preview_labels:
            label = self.preview_labels[font_key]
            font = QFont(family)
            
            # Convert relative size to actual point size
            # Based on Cura's actual base font size (approximately 10-11 points)
            base_point_size = 10.5  # More accurate base size matching Cura's rendering
            point_size = base_point_size * size
            point_size = max(point_size, 7.0)  # Minimum readable size
            
            font.setPointSizeF(point_size)
            font.setWeight(QFont.Weight(weight))
            font.setItalic(italic)
            
            label.setFont(font)


class ThemeCreatorDialog(QDialog):
    """
    Main dialog for creating and editing Cura themes.
    
    This dialog provides a comprehensive interface for:
    - Font customization (family, size, weight)
    - Color management (UI colors and themes)
    - Size scaling (UI element dimensions)
    - Theme import/export functionality
    - Live preview of changes
    
    The dialog uses a tabbed interface to organize different theme aspects
    and loads configuration from theme_config.json for available options.
    
    Attributes:
        config_loader: Manages theme configuration loading and validation
        theme_data: Current theme data being edited
        _loading_timer: Timer for asynchronous UI loading
        tab_widget: Main tabbed interface container
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self.setWindowTitle("Cura Theme Creator")
        self.setModal(True)
        self.resize(PluginConstants.DIMENSIONS['dialog_width'], 
                   PluginConstants.DIMENSIONS['dialog_height'])
        
        # Apply main dialog styling
        self.setStyleSheet(PluginConstants.get_style('main_dialog'))
        
        # Initialize configuration loader
        try:
            self.config_loader = ThemeConfigLoader()
        except (FileNotFoundError, ValueError) as e:
            Logger.error(f"Failed to load theme configuration: {str(e)}")
            QMessageBox.critical(self, "Configuration Error", 
                               f"Failed to load theme configuration: {str(e)}\n\nUsing minimal defaults.")
            # Continue with a minimal configuration instead of stopping
            try:
                self.config_loader = ThemeConfigLoader()  # Will use defaults now
            except Exception:
                # If still failing, show error and close
                QMessageBox.critical(self, "Critical Error", 
                                   "Cannot initialize theme configuration. Please check the plugin installation.")
                self.close()
                return
        
        # Theme data storage
        self.theme_data = self._loadDefaultTheme()
        
        # Initialize async loading state
        self._loading_tasks = []
        self._current_task_index = 0
        self._loading_timer = QTimer()
        self._loading_timer.timeout.connect(self._processNextLoadingTask)
        
        # Setup basic UI structure first
        self._setupBasicUI()
        
        # Start async loading process
        self._startAsyncLoading()
        
        Logger.info("Theme Creator dialog initialized")
    
    def _setupBasicUI(self):
        """Setup the basic UI structure without heavy content."""
        layout = QVBoxLayout(self)
        
        # Header with theme name and load button
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Theme Name:"))
        self.theme_name_edit = QLineEdit("Custom Theme")
        self.theme_name_edit.setFixedWidth(220)
        self.theme_name_edit.setStyleSheet(PluginConstants.get_style('input'))
        header_layout.addWidget(self.theme_name_edit)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add loading widget to the center of the tab widget initially
        self.loading_widget = LoadingWidget()
        loading_container = QWidget()
        loading_layout = QVBoxLayout(loading_container)
        loading_layout.addStretch()
        loading_layout.addWidget(self.loading_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        loading_layout.addStretch()
        self.tab_widget.addTab(loading_container, "Loading...")
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        # Left side buttons (Load and Export)
        self.load_button = QPushButton("Import Theme")
        self.load_button.setStyleSheet(PluginConstants.get_style('button'))
        self.load_button.clicked.connect(self._loadTheme)
        self.load_button.setEnabled(False)  # Disable until loaded
        button_layout.addWidget(self.load_button)

        # Left side buttons (Load and Export)
        self.load_active_button = QPushButton("Load Active Theme")
        self.load_active_button.setStyleSheet(PluginConstants.get_style('button'))
        self.load_active_button.clicked.connect(self._loadActiveTheme)
        self.load_active_button.setEnabled(False)  # Disable until loaded
        button_layout.addWidget(self.load_active_button)
        
        self.export_button = QPushButton("Export Theme")
        self.export_button.setStyleSheet(PluginConstants.get_style('button'))
        self.export_button.clicked.connect(self._exportTheme)
        self.export_button.setEnabled(False)  # Disable until loaded
        button_layout.addWidget(self.export_button)

        self.export_activate_button = QPushButton("Export && Activate")
        self.export_activate_button.setStyleSheet(PluginConstants.get_style('button'))
        self.export_activate_button.clicked.connect(self._setActiveExport)
        self.export_activate_button.setEnabled(False)  # Disable until loaded
        button_layout.addWidget(self.export_activate_button)
        
        # Add stretch to push Close button to the right
        button_layout.addStretch()
        
        # Right side button (Close)
        close_button = QPushButton("Close")
        close_button.setStyleSheet(PluginConstants.get_style('button'))
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def _startAsyncLoading(self):
        """Initialize and start the async loading process."""
        # Define loading tasks with their progress weights
        self._loading_tasks = [
            ("Preparing fonts tab...", 20, self._createFontsTabAsync),
            ("Preparing colors tab...", 40, self._createColorsTabAsync),
            ("Preparing sizes tab...", 20, self._createSizesTabAsync),
            ("Loading theme data...", 20, self._loadThemeDataAsync),
        ]
        
        self._current_task_index = 0
        self._current_progress = 0
        
        # Start the loading process
        self.loading_widget.updateProgress(0, "Starting...")
        self._loading_timer.start(10)  # Process every 10ms to keep UI responsive
    
    def _processNextLoadingTask(self):
        """Process the next loading task in the queue."""
        if self._current_task_index >= len(self._loading_tasks):
            # All tasks completed
            self._finishLoading()
            return
        
        task_name, task_weight, task_function = self._loading_tasks[self._current_task_index]
        
        # Update progress
        self.loading_widget.updateProgress(self._current_progress, task_name)
        
        try:
            # Execute the task
            task_function()
            
            # Update progress
            self._current_progress += task_weight
            self._current_task_index += 1
            
        except Exception as e:
            # Handle errors gracefully
            Logger.error(f"Error during async loading task '{task_name}': {str(e)}")
            QMessageBox.warning(self, "Loading Error", 
                              f"Error loading {task_name}: {str(e)}")
            self._finishLoading()
    
    def _finishLoading(self):
        """Complete the loading process and finalize UI."""
        self._loading_timer.stop()
        
        # Update progress to complete
        self.loading_widget.updateProgress(100, "Complete!")
        
        # Small delay before removing loading screen
        QTimer.singleShot(300, self._removeLoadingScreen)
    
    def _removeLoadingScreen(self):
        """Remove the loading screen and enable UI."""
        # Remove the loading tab
        self.tab_widget.clear()
        
        # Add the actual content tabs
        self.tab_widget.addTab(self.fonts_widget, "Fonts")
        self.tab_widget.addTab(self.colors_widget, "Colors") 
        self.tab_widget.addTab(self.sizes_widget, "Sizes")
        
        # Clean up loading widget
        self.loading_widget.stop()
        
        # Enable export and load buttons
        self.export_button.setEnabled(True)
        self.load_button.setEnabled(True)
        self.load_active_button.setEnabled(True)
        self.export_activate_button.setEnabled(True)
        
        Logger.info("Theme Creator UI loading completed")
    
    def _createFontsTabAsync(self):
        """Create the fonts configuration tab asynchronously."""
        self.fonts_widget = QWidget()
        layout = QVBoxLayout(self.fonts_widget)
        
        # Add font scale factor slider
        font_scale_frame = QFrame()
        font_scale_frame.setStyleSheet(PluginConstants.get_style('group_box'))
        font_scale_layout = QHBoxLayout(font_scale_frame)
        font_scale_frame.setMinimumHeight(70)
        
        font_scale_label = QLabel("Font Scale Factor:")
        font_scale_label.setStyleSheet(PluginConstants.get_style('color_label'))
        font_scale_layout.addWidget(font_scale_label)
        
        # Value display label
        self.font_scale_value_label = QLabel("1.0")
        font_scale_layout.addWidget(self.font_scale_value_label)
        
        # Slider control
        self.font_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_scale_slider.setRange(1, 50)  # 0.1 to 5.0 in steps of 0.1
        self.font_scale_slider.setValue(10)  # Default 1.0
        self.font_scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.font_scale_slider.setTickInterval(5)  # Tick every 0.5
        self.font_scale_slider.setMinimumWidth(200)
        self.font_scale_slider.valueChanged.connect(self._onFontSliderChanged)
        font_scale_layout.addWidget(self.font_scale_slider)
        
        font_scale_info = QLabel("(Multiplies all font size values)")
        font_scale_info.setStyleSheet(PluginConstants.get_style('color_label'))
        font_scale_layout.addWidget(font_scale_info)
        
        font_scale_layout.addStretch()
        layout.addWidget(font_scale_frame)
        
        # Main scroll area for all fonts
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        self.font_controls = {}
        self.font_preview_labels = {}  # Store individual preview labels for each font
        self._base_font_values = {}  # Store original font size values for scaling
        
        # Get font categories from configuration
        font_categories = self.config_loader.get_font_categories()
        
        for category_name, font_items in font_categories:
            # Category header
            category_header = QLabel(category_name)
            category_header.setStyleSheet(PluginConstants.get_style('category_header'))
            scroll_layout.addWidget(category_header)
            
            for font_item in font_items:
                font_key = font_item["key"]
                font_label = font_item.get("label", font_key)
                font_description = font_item.get("description", "")
                
                # Create container for this font row
                font_container = QFrame()
                font_container.setStyleSheet(PluginConstants.get_style('font_container'))
                font_container.setMinimumHeight(120)
                font_container_layout = QHBoxLayout(font_container)
                font_container_layout.setContentsMargins(5, 5, 5, 5)
                font_container_layout.setSpacing(10)
                font_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                
                # Left side - font controls without border
                controls_container = QFrame()
                controls_container.setStyleSheet(PluginConstants.get_style('controls_container'))
                controls_container.setFixedWidth(320)
                controls_container_layout = QVBoxLayout(controls_container)
                controls_container_layout.setContentsMargins(5, 5, 5, 5)
                controls_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                
                controls_widget = QWidget()
                controls_widget.setStyleSheet(PluginConstants.get_style('controls_widget'))
                controls_layout = QGridLayout(controls_widget)
                controls_layout.setSpacing(8)
                
                # Font name label
                name_label = QLabel(f"{font_label}:")
                name_label.setStyleSheet(PluginConstants.get_style('font_name_label'))
                if font_description:
                    name_label.setToolTip(font_description)
                controls_layout.addWidget(name_label, 0, 0, 1, 2)
                
                # Font family
                family_label = QLabel("Family:")
                family_label.setStyleSheet(PluginConstants.get_style('control_label'))
                controls_layout.addWidget(family_label, 1, 0)
                family_combo = QFontComboBox()
                family_combo.setFixedWidth(200)
                family_combo.setStyleSheet(PluginConstants.get_style('input'))
                family_combo.currentFontChanged.connect(
                    lambda font, key=font_key: self._updateSingleFont(key, family=font.family())
                )
                self.font_controls[f"{font_key}_family"] = family_combo
                controls_layout.addWidget(family_combo, 1, 1)
                
                # Font size
                size_label = QLabel("Size:")
                size_label.setStyleSheet(PluginConstants.get_style('control_label'))
                controls_layout.addWidget(size_label, 2, 0)
                size_spin = QDoubleSpinBox()
                size_spin.setFixedWidth(200)
                size_spin.setStyleSheet(PluginConstants.get_style('input'))
                size_spin.setRange(0.5, 5.0)
                size_spin.setSingleStep(0.05)
                size_spin.setDecimals(2)
                size_spin.valueChanged.connect(
                    lambda value, key=font_key: self._updateSingleFont(key, size=value)
                )
                self.font_controls[f"{font_key}_size"] = size_spin
                controls_layout.addWidget(size_spin, 2, 1)
                
                # Font weight
                weight_label = QLabel("Weight:")
                weight_label.setStyleSheet(PluginConstants.get_style('control_label'))
                controls_layout.addWidget(weight_label, 3, 0)
                weight_combo = QComboBox()
                weight_combo.setFixedWidth(200)
                weight_combo.setStyleSheet(PluginConstants.get_style('input'))
                weight_combo.addItems(["100", "200", "300", "400", "500", "600", "700", "800", "900"])
                weight_combo.currentTextChanged.connect(
                    lambda text, key=font_key: self._updateSingleFont(key, weight=int(text))
                )
                self.font_controls[f"{font_key}_weight"] = weight_combo
                controls_layout.addWidget(weight_combo, 3, 1)
                
                # Font italic (checkbox)
                italic_label = QLabel("Italic:")
                italic_label.setStyleSheet(PluginConstants.get_style('control_label'))
                controls_layout.addWidget(italic_label, 4, 0)
                italic_check = QCheckBox()
                italic_check.toggled.connect(
                    lambda checked, key=font_key: self._updateSingleFont(key, italic=checked)
                )
                self.font_controls[f"{font_key}_italic"] = italic_check
                controls_layout.addWidget(italic_check, 4, 1)
                
                controls_container_layout.addWidget(controls_widget)
                controls_container_layout.addStretch()  # Push content to top
                font_container_layout.addWidget(controls_container)
                
                # Right side - individual font preview without border
                preview_container = QFrame()
                preview_container.setStyleSheet(PluginConstants.get_style('preview_container'))
                preview_container.setMinimumWidth(280)
                preview_layout = QVBoxLayout(preview_container)
                preview_layout.setContentsMargins(5, 5, 5, 5)
                preview_layout.setSpacing(8)
                preview_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                
                # Preview header
                preview_header = QLabel("Preview")
                preview_header.setStyleSheet(PluginConstants.get_style('preview_header'))
                preview_layout.addWidget(preview_header)
                
                # Preview text
                preview_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. 1234567890"
                preview_label = QLabel(preview_text)
                preview_label.setStyleSheet(PluginConstants.get_style('preview_label'))
                preview_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
                preview_label.setWordWrap(True)
                preview_label.setAlignment(Qt.AlignmentFlag.AlignTop)
                self.font_preview_labels[font_key] = preview_label
                preview_layout.addWidget(preview_label)
                
                preview_layout.addStretch()
                font_container_layout.addWidget(preview_container, 1)
                
                scroll_layout.addWidget(font_container)
            
            # Add some spacing between categories
            scroll_layout.addSpacing(15)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(PluginConstants.get_style('scroll_area'))
        layout.addWidget(scroll_area)
    
    def _createColorsTabAsync(self):
        """Create the colors configuration tab asynchronously."""
        self.colors_widget = QWidget()
        layout = QVBoxLayout(self.colors_widget)
        
        # Add search bar at the top
        search_frame = QFrame()
        search_frame.setStyleSheet(PluginConstants.get_style('group_box'))
        search_layout = QHBoxLayout(search_frame)
        search_frame.setMinimumHeight(50)
        
        # Add Reset Colors button on the left
        reset_colors_button = QPushButton("Reset Colors")
        reset_colors_button.setStyleSheet(PluginConstants.get_style('button'))
        reset_colors_button.clicked.connect(self._resetColors)
        reset_colors_button.setFixedWidth(120)
        search_layout.addWidget(reset_colors_button)
        
        # Add stretch to push search elements to the right
        search_layout.addStretch()
        
        search_label = QLabel("Search Colors:")
        search_label.setStyleSheet(PluginConstants.get_style('color_label'))
        search_layout.addWidget(search_label)
        
        self.colors_search = QLineEdit()
        self.colors_search.setPlaceholderText("Type to filter colors...")
        self.colors_search.setStyleSheet(PluginConstants.get_style('input'))
        self.colors_search.textChanged.connect(self._filterColors)
        self.colors_search.setFixedWidth(300)  # Set fixed width for consistency
        search_layout.addWidget(self.colors_search)
        
        layout.addWidget(search_frame)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        self.color_controls = {}
        self.color_groups = {}  # Store group boxes for filtering
        
        # Get color categories from configuration
        color_categories = self.config_loader.get_color_categories()
        
        for category_name, color_items, is_base_colors in color_categories:
            group = QGroupBox(category_name)
            group.setStyleSheet(PluginConstants.get_style('group_box'))
            group_layout = QVBoxLayout(group)
            
            # Store group box for filtering
            self.color_groups[category_name] = {
                'group': group,
                'items': []
            }
            
            for color_item in color_items:
                color_key = color_item["key"]
                color_label = color_item.get("label", color_key)
                color_description = color_item.get("description", "")
                
                # Create horizontal layout for each color (similar to sizes)
                color_row = QHBoxLayout()
                
                # Color name label
                label_widget = QLabel(f"{color_label}:")
                label_widget.setMinimumWidth(200)
                label_widget.setStyleSheet(PluginConstants.get_style('color_label'))
                if color_description:
                    label_widget.setToolTip(color_description)
                color_row.addWidget(label_widget)
                
                # Add stretch to push color button to the right
                color_row.addStretch()
                
                # Color button
                color_button = ColorButton()
                color_button.colorChanged.connect(
                    lambda color, key=color_key: self._updateColor(key, color)
                )
                self.color_controls[color_key] = color_button
                color_row.addWidget(color_button)
                
                # Create row widget
                row_widget = QWidget()
                row_widget.setLayout(color_row)
                group_layout.addWidget(row_widget)
                
                # Store item info for filtering
                self.color_groups[category_name]['items'].append({
                    'key': color_key,
                    'label': color_label,
                    'description': color_description,
                    'widget': row_widget
                })
            
            scroll_layout.addWidget(group)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(PluginConstants.get_style('scroll_area'))
        layout.addWidget(scroll_area)
    
    def _resetColors(self):
        """Reset all colors to their default values without changing other inputs."""
        try:
            # Get default colors from ThemeDataManager
            theme_manager = ThemeDataManager()
            default_theme = theme_manager.default_theme_structure
            
            # Replace only the color sections in theme data
            self.theme_data["base_colors"] = default_theme.get("base_colors", {})
            self.theme_data["colors"] = default_theme.get("colors", {})

            self._loadColorsToUI()

            QMessageBox.information(self, "Success", "All colors have been reset to their default values.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset colors:\n{str(e)}")
            Logger.logException("e", f"Error resetting colors: {str(e)}")
    
    def _filterColors(self, search_text):
        """Filter colors based on search text."""
        search_text = search_text.lower().strip()
        
        for category_name, category_data in self.color_groups.items():
            group = category_data['group']
            items = category_data['items']
            visible_items = 0
            
            for item in items:
                # Check if item matches search
                matches = (
                    not search_text or  # Show all if no search text
                    search_text in item['key'].lower() or
                    search_text in item['label'].lower() or
                    search_text in item['description'].lower()
                )
                
                # Show/hide the item widget
                item['widget'].setVisible(matches)
                if matches:
                    visible_items += 1
            
            # Show/hide the entire group based on whether it has visible items
            group.setVisible(visible_items > 0)
    
    def _createSizesTabAsync(self):
        """Create the sizes configuration tab asynchronously."""
        self.sizes_widget = QWidget()
        layout = QVBoxLayout(self.sizes_widget)
        
        # Add scale factor slider
        scale_frame = QFrame()
        scale_frame.setStyleSheet(PluginConstants.get_style('group_box'))
        scale_layout = QHBoxLayout(scale_frame)
        scale_frame.setMinimumHeight(70)
        
        scale_label = QLabel("Scale Factor:")
        scale_label.setStyleSheet(PluginConstants.get_style('color_label'))
        scale_layout.addWidget(scale_label)
        
        # Value display label
        self.scale_value_label = QLabel("1.0")
        scale_layout.addWidget(self.scale_value_label)
        
        # Slider control
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(1, 50)  # 0.1 to 5.0 in steps of 0.1
        self.scale_slider.setValue(10)  # Default 1.0
        self.scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.scale_slider.setTickInterval(5)  # Tick every 0.5
        self.scale_slider.setMinimumWidth(200)
        self.scale_slider.valueChanged.connect(self._onSliderChanged)
        scale_layout.addWidget(self.scale_slider)
        
        scale_info = QLabel("(Multiplies all size values)")
        scale_info.setStyleSheet(PluginConstants.get_style('color_label'))
        scale_layout.addWidget(scale_info)
        
        scale_layout.addStretch()
        layout.addWidget(scale_frame)

        # Add search bar at the top
        search_frame = QFrame()
        search_frame.setStyleSheet(PluginConstants.get_style('group_box'))
        search_layout = QHBoxLayout(search_frame)
        search_frame.setMinimumHeight(50)
        
        # Add stretch to push search elements to the right
        search_layout.addStretch()
        
        search_label = QLabel("Search Sizes:")
        search_label.setStyleSheet(PluginConstants.get_style('color_label'))
        search_layout.addWidget(search_label)
        
        self.sizes_search = QLineEdit()
        self.sizes_search.setPlaceholderText("Type to filter sizes...")
        self.sizes_search.setStyleSheet(PluginConstants.get_style('input'))
        self.sizes_search.textChanged.connect(self._filterSizes)
        self.sizes_search.setFixedWidth(300)  # Set fixed width for consistency
        search_layout.addWidget(self.sizes_search)
        
        layout.addWidget(search_frame)
        
        # Scroll area for size items
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        self.size_controls = {}
        self._base_size_values = {}  # Store original values for scaling
        self.size_groups = {}  # Store group boxes for filtering
        
        # Get size categories from configuration
        size_categories = self.config_loader.get_size_categories()
        
        for category_name, size_items in size_categories:
            group = QGroupBox(category_name)
            group.setStyleSheet(PluginConstants.get_style('group_box'))
            group_layout = QVBoxLayout(group)
            
            # Store group box for filtering
            self.size_groups[category_name] = {
                'group': group,
                'items': []
            }
            
            for size_item in size_items:
                size_key = size_item["key"]
                size_label = size_item.get("label", size_key)
                size_description = size_item.get("description", "")
                
                # Create horizontal layout for each size
                size_row = QHBoxLayout()
                
                # Size name label
                label_widget = QLabel(f"{size_label}:")
                label_widget.setMinimumWidth(200)
                label_widget.setStyleSheet(PluginConstants.get_style('color_label'))
                if size_description:
                    label_widget.setToolTip(size_description)
                size_row.addWidget(label_widget)
                
                # Add stretch to push width and height labels to the right
                size_row.addStretch()
                
                # Width controls
                width_label = QLabel("Width:")
                width_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                width_label.setStyleSheet(PluginConstants.get_style('color_label'))
                size_row.addWidget(width_label)
                
                width_spin = QDoubleSpinBox()
                width_spin.setRange(0.0, 999.0)
                width_spin.setSingleStep(0.1)
                width_spin.setDecimals(1)
                width_spin.setFixedWidth(80)
                width_spin.setStyleSheet(PluginConstants.get_style('input'))
                width_spin.valueChanged.connect(
                    lambda value, key=size_key: self._updateSize(key, width=value)
                )
                self.size_controls[f"{size_key}_width"] = width_spin
                size_row.addWidget(width_spin)
                
                # Initialize base value storage
                if size_key not in self._base_size_values:
                    self._base_size_values[size_key] = [0.0, 0.0]
                
                # Height controls
                height_label = QLabel("Height:")
                height_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                height_label.setStyleSheet(PluginConstants.get_style('color_label'))
                size_row.addWidget(height_label)
                
                height_spin = QDoubleSpinBox()
                height_spin.setRange(0.0, 999.0)
                height_spin.setSingleStep(0.1)
                height_spin.setDecimals(1)
                height_spin.setFixedWidth(80)
                height_spin.setStyleSheet(PluginConstants.get_style('input'))
                height_spin.valueChanged.connect(
                    lambda value, key=size_key: self._updateSize(key, height=value)
                )
                self.size_controls[f"{size_key}_height"] = height_spin
                size_row.addWidget(height_spin)
                
                # Create row widget
                row_widget = QWidget()
                row_widget.setLayout(size_row)
                group_layout.addWidget(row_widget)
                
                # Store item info for filtering
                self.size_groups[category_name]['items'].append({
                    'key': size_key,
                    'label': size_label,
                    'description': size_description,
                    'widget': row_widget
                })
            
            scroll_layout.addWidget(group)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(PluginConstants.get_style('scroll_area'))
        layout.addWidget(scroll_area)
    
    def _filterSizes(self, search_text):
        """Filter sizes based on search text."""
        search_text = search_text.lower().strip()
        
        for category_name, category_data in self.size_groups.items():
            group = category_data['group']
            items = category_data['items']
            visible_items = 0
            
            for item in items:
                # Check if item matches search
                matches = (
                    not search_text or  # Show all if no search text
                    search_text in item['key'].lower() or
                    search_text in item['label'].lower() or
                    search_text in item['description'].lower()
                )
                
                # Show/hide the item widget
                item['widget'].setVisible(matches)
                if matches:
                    visible_items += 1
            
            # Show/hide the entire group based on whether it has visible items
            group.setVisible(visible_items > 0)
    
    def _loadColorsToUI(self):
        """Load colors from theme_data into UI controls."""
        base_colors = self.theme_data.get("base_colors", {})
        colors = self.theme_data.get("colors", {})
        
        # Load base colors first
        for color_key, color_value in base_colors.items():
            if color_key in self.color_controls:
                if isinstance(color_value, list) and len(color_value) >= 3:
                    color = color_value[:4]  # Ensure max 4 values (RGBA)
                    if len(color) == 3:
                        color.append(255)  # Add alpha if missing
                    self.color_controls[color_key].setColor(color)
        
        # Load regular colors
        for color_key, color_value in colors.items():
            if color_key in self.color_controls:
                if isinstance(color_value, list) and len(color_value) >= 3:
                    color = color_value[:4]  # Ensure max 4 values (RGBA)
                    if len(color) == 3:
                        color.append(255)  # Add alpha if missing
                    self.color_controls[color_key].setColor(color)
                elif isinstance(color_value, str):
                    # String reference to base color
                    if color_value in base_colors:
                        base_color = base_colors[color_value]
                        if isinstance(base_color, list) and len(base_color) >= 3:
                            color = base_color[:4]
                            if len(color) == 3:
                                color.append(255)
                            self.color_controls[color_key].setColor(color)
    
    def _loadThemeDataAsync(self):
        """Load theme data into controls asynchronously."""
        # Reset font scale factor to 1.0 when loading a theme
        if hasattr(self, 'font_scale_slider'):
            self.font_scale_slider.blockSignals(True)
            self.font_scale_slider.setValue(10)  # 1.0 scale factor
            self.font_scale_value_label.setText("1.0")
            self.font_scale_slider.blockSignals(False)
        
        # Clear font base values before reloading to ensure clean state
        if hasattr(self, '_base_font_values'):
            self._base_font_values.clear()
        
        # Load fonts - only load fonts that have corresponding controls
        fonts_data = self.theme_data.get("fonts", {})
        for font_key, font_data in fonts_data.items():
            # Only load if we have controls for this font
            if (f"{font_key}_family" in self.font_controls or 
                f"{font_key}_size" in self.font_controls or 
                f"{font_key}_weight" in self.font_controls or 
                f"{font_key}_italic" in self.font_controls):
                
                if f"{font_key}_family" in self.font_controls:
                    family_combo = self.font_controls[f"{font_key}_family"]
                    family_combo.setCurrentFont(QFont(font_data.get("family", "Noto Sans")))
                
                if f"{font_key}_size" in self.font_controls:
                    size_spin = self.font_controls[f"{font_key}_size"]
                    size = font_data.get("size", 1.0)
                    size_spin.setValue(size)
                    
                    # Store base font size values (these are the original unscaled values)
                    if hasattr(self, '_base_font_values'):
                        self._base_font_values[font_key] = size
                
                if f"{font_key}_weight" in self.font_controls:
                    weight_combo = self.font_controls[f"{font_key}_weight"]
                    weight_combo.setCurrentText(str(font_data.get("weight", 400)))
                
                if f"{font_key}_italic" in self.font_controls:
                    italic_check = self.font_controls[f"{font_key}_italic"]
                    italic_check.setChecked(font_data.get("italic", False))
                
                # Update font preview if preview widget exists
                if hasattr(self, 'font_preview_labels'):
                    family = font_data.get("family", "Noto Sans")
                    size = font_data.get("size", 1.0)
                    weight = font_data.get("weight", 400)
                    italic = font_data.get("italic", False)
                    self._updateSingleFontPreview(font_key, font_data)
        
        self._loadColorsToUI()
        
        # Load sizes - only load sizes that have corresponding controls
        sizes_data = self.theme_data.get("sizes", {})
        
        # Reset scale factor to 1.0 when loading a theme
        if hasattr(self, 'scale_slider'):
            self.scale_slider.blockSignals(True)
            self.scale_slider.setValue(10)  # 1.0 scale factor
            self.scale_value_label.setText("1.0")
            self.scale_slider.blockSignals(False)
        
        for size_key, size_value in sizes_data.items():
            # Only load if we have controls for this size
            if (f"{size_key}_width" in self.size_controls or 
                f"{size_key}_height" in self.size_controls):
                
                if isinstance(size_value, list) and len(size_value) >= 2:
                    width, height = size_value[0], size_value[1]
                    
                    # Store base values (these are the original unscaled values)
                    if hasattr(self, '_base_size_values'):
                        self._base_size_values[size_key] = [width, height]
                    
                    # Temporarily block signals to avoid triggering updates during load
                    if f"{size_key}_width" in self.size_controls:
                        self.size_controls[f"{size_key}_width"].blockSignals(True)
                        self.size_controls[f"{size_key}_width"].setValue(width)
                        self.size_controls[f"{size_key}_width"].blockSignals(False)
                    
                    if f"{size_key}_height" in self.size_controls:
                        self.size_controls[f"{size_key}_height"].blockSignals(True)
                        self.size_controls[f"{size_key}_height"].setValue(height)
                        self.size_controls[f"{size_key}_height"].blockSignals(False)
    
    def _loadDefaultTheme(self):
        """Load a minimal default theme structure."""
        # Use a fast, minimal theme structure instead of loading from files
        theme_manager = ThemeDataManager()
        return theme_manager.createNewTheme("Custom Theme")
    
    def _loadTheme(self, file_path=None):
        """Load an existing theme from disk."""
        # Prevent loading while interface is still being built
        if not self.load_button.isEnabled():
            return
        
        # Open file dialog to select theme.json file
        if file_path is None:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Load Theme File",
                "",
                "Theme Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Load the theme file
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_theme_data = json.load(f)
            
            # Validate that it's a theme file (check for basic structure)
            if not isinstance(loaded_theme_data, dict):
                QMessageBox.warning(self, "Invalid File", "Invalid theme file format")
                return
            
            # Start with default theme structure to ensure all required elements exist
            merged_theme = self._loadDefaultTheme()
            
            # Merge loaded theme data with defaults
            self._mergeThemeData(merged_theme, loaded_theme_data)
            
            # Update theme data
            self.theme_data = merged_theme
            
            # Update theme name from metadata if available
            if "metadata" in loaded_theme_data and "name" in loaded_theme_data["metadata"]:
                theme_name = loaded_theme_data["metadata"]["name"]
                self.theme_name_edit.setText(theme_name)
            else:
                # Extract name from filename
                theme_name = os.path.splitext(os.path.basename(file_path))[0]
                self.theme_name_edit.setText(theme_name)
            
            # Clear base size values before reloading to ensure clean state
            if hasattr(self, '_base_size_values'):
                self._base_size_values.clear()
            
            # Reload all UI controls with the new theme data
            self._loadThemeDataAsync()
            
            QMessageBox.information(self, "Success", 
                                  f"Theme loaded successfully from:\n{file_path}")
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", 
                               f"Invalid JSON file:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Failed to load theme:\n{str(e)}")
    
    def _mergeThemeData(self, base_theme, loaded_theme):
        """Merge loaded theme data with base theme, preserving structure and adding new data."""
        for section_key, section_data in loaded_theme.items():
            if section_key in base_theme:
                if isinstance(section_data, dict) and isinstance(base_theme[section_key], dict):
                    # Merge dictionaries (fonts, base_colors, colors, sizes, metadata)
                    for item_key, item_value in section_data.items():
                        base_theme[section_key][item_key] = item_value
                else:
                    # Replace non-dict values directly
                    base_theme[section_key] = section_data
            else:
                # Add new sections that don't exist in base theme
                base_theme[section_key] = section_data
    
    def _updateFont(self, font_key, family=None, size=None, weight=None, italic=None):
        """Update font data when UI controls change."""
        if "fonts" not in self.theme_data:
            self.theme_data["fonts"] = {}
        
        if font_key not in self.theme_data["fonts"]:
            self.theme_data["fonts"][font_key] = {"size": 1.0, "weight": 400, "family": "Noto Sans"}
        
        font_data = self.theme_data["fonts"][font_key]
        
        if family is not None:
            font_data["family"] = family
        if size is not None:
            font_data["size"] = size
            # Store base font size value (divide by current scale to get original)
            scale_factor = getattr(self, 'font_scale_slider', None)
            current_scale = (scale_factor.value() / 10.0) if scale_factor else 1.0
            if hasattr(self, '_base_font_values'):
                self._base_font_values[font_key] = size / current_scale
        if weight is not None:
            font_data["weight"] = weight
        if italic is not None:
            if italic:
                font_data["italic"] = True
            elif "italic" in font_data:
                del font_data["italic"]  # Remove italic property if False
        
        # Update individual preview if it exists
        self._updateSingleFontPreview(font_key, font_data)
    
    def _updateSingleFont(self, font_key, family=None, size=None, weight=None, italic=None):
        """Update font data and preview for a single font."""
        self._updateFont(font_key, family, size, weight, italic)
    
    def _updateSingleFontPreview(self, font_key, font_data):
        """Update the individual preview for a specific font."""
        if hasattr(self, 'font_preview_labels') and font_key in self.font_preview_labels:
            label = self.font_preview_labels[font_key]
            font = QFont(font_data["family"])
            
            # Convert relative size to actual point size
            # Based on Cura's actual base font size (approximately 10-11 points)
            base_point_size = 10.5  # More accurate base size matching Cura's rendering
            point_size = base_point_size * font_data["size"]
            point_size = max(point_size, 7.0)  # Minimum readable size
            
            font.setPointSizeF(point_size)
            font.setWeight(QFont.Weight(font_data["weight"]))
            font.setItalic(font_data.get("italic", False))
            
            label.setFont(font)
    
    def _updateColor(self, color_key, color):
        """Update color data when UI controls change."""
        # Use configuration loader to determine if this should go in base_colors or colors
        if self.config_loader.is_base_color(color_key):
            if "base_colors" not in self.theme_data:
                self.theme_data["base_colors"] = {}
            self.theme_data["base_colors"][color_key] = color
        else:
            if "colors" not in self.theme_data:
                self.theme_data["colors"] = {}
            self.theme_data["colors"][color_key] = color
    
    def _updateSize(self, size_key, width=None, height=None):
        """Update size data when UI controls change."""
        if "sizes" not in self.theme_data:
            self.theme_data["sizes"] = {}
        
        if size_key not in self.theme_data["sizes"]:
            self.theme_data["sizes"][size_key] = [0.0, 0.0]
        
        if not isinstance(self.theme_data["sizes"][size_key], list):
            self.theme_data["sizes"][size_key] = [0.0, 0.0]
        
        if len(self.theme_data["sizes"][size_key]) < 2:
            self.theme_data["sizes"][size_key] = [0.0, 0.0]
        
        # Update base values (unscaled values)
        if size_key not in self._base_size_values:
            self._base_size_values[size_key] = [0.0, 0.0]
        
        scale_factor = getattr(self, 'scale_slider', None)
        current_scale = (scale_factor.value() / 10.0) if scale_factor else 1.0
        
        if width is not None:
            # Store the base value (divide by current scale to get original)
            self._base_size_values[size_key][0] = width / current_scale
            self.theme_data["sizes"][size_key][0] = width
        if height is not None:
            # Store the base value (divide by current scale to get original)
            self._base_size_values[size_key][1] = height / current_scale
            self.theme_data["sizes"][size_key][1] = height
    
    def _onSliderChanged(self, value):
        """Handle slider value changes and convert to scale factor."""
        scale_factor = value / 10.0  # Convert slider value (1-50) to scale (0.1-5.0)
        self.scale_value_label.setText(f"{scale_factor:.1f}")
        self._onScaleFactorChanged(scale_factor)
    
    def _onScaleFactorChanged(self, scale_factor):
        """Handle scale factor changes by updating all size controls."""
        if not hasattr(self, 'size_controls') or not hasattr(self, '_base_size_values'):
            return
        
        # Temporarily disconnect signals to avoid infinite loops
        for control in self.size_controls.values():
            control.blockSignals(True)
        
        # Update all size controls with scaled values
        for size_key, base_values in self._base_size_values.items():
            if len(base_values) >= 2:
                scaled_width = base_values[0] * scale_factor
                scaled_height = base_values[1] * scale_factor
                
                # Update UI controls
                if f"{size_key}_width" in self.size_controls:
                    self.size_controls[f"{size_key}_width"].setValue(scaled_width)
                if f"{size_key}_height" in self.size_controls:
                    self.size_controls[f"{size_key}_height"].setValue(scaled_height)
                
                # Update theme data
                if "sizes" not in self.theme_data:
                    self.theme_data["sizes"] = {}
                self.theme_data["sizes"][size_key] = [scaled_width, scaled_height]
        
        # Re-enable signals
        for control in self.size_controls.values():
            control.blockSignals(False)
    
    def _onFontSliderChanged(self, value):
        """Handle font slider value changes and convert to scale factor."""
        scale_factor = value / 10.0  # Convert slider value (1-50) to scale (0.1-5.0)
        self.font_scale_value_label.setText(f"{scale_factor:.1f}")
        self._onFontScaleFactorChanged(scale_factor)
    
    def _onFontScaleFactorChanged(self, scale_factor):
        """Handle font scale factor changes by updating all font size controls."""
        if not hasattr(self, 'font_controls') or not hasattr(self, '_base_font_values'):
            return
        
        # Temporarily disconnect signals to avoid infinite loops
        for control_name, control in self.font_controls.items():
            if control_name.endswith('_size'):
                control.blockSignals(True)
        
        # Update all font size controls with scaled values
        for font_key, base_size in self._base_font_values.items():
            scaled_size = base_size * scale_factor
            
            # Update UI control
            if f"{font_key}_size" in self.font_controls:
                self.font_controls[f"{font_key}_size"].setValue(scaled_size)
            
            # Update theme data
            if "fonts" not in self.theme_data:
                self.theme_data["fonts"] = {}
            if font_key not in self.theme_data["fonts"]:
                self.theme_data["fonts"][font_key] = {"size": 1.0, "weight": 400, "family": "Noto Sans"}
            self.theme_data["fonts"][font_key]["size"] = scaled_size
            
            # Update individual preview if it exists
            if font_key in self.theme_data["fonts"]:
                self._updateSingleFontPreview(font_key, self.theme_data["fonts"][font_key])
        
        # Re-enable signals
        for control_name, control in self.font_controls.items():
            if control_name.endswith('_size'):
                control.blockSignals(False)
    
    def _exportTheme(self, show_message=True) -> Optional[str]:
        """Export the current theme to Cura's themes directory."""
        theme_name = self.theme_name_edit.text().strip()
        if not theme_name:
            QMessageBox.warning(self, "Warning", "Please enter a theme name.")
            return
        
        # Update metadata
        if "metadata" not in self.theme_data:
            self.theme_data["metadata"] = {}
        self.theme_data["metadata"]["name"] = theme_name
        
        try:            
            # Get Cura's data storage path and add themes subdirectory
            user_data_path = Resources.getDataStoragePath()
            if not user_data_path:
                Logger.error("Could not determine Cura's data storage directory")
                QMessageBox.critical(self, "Error", "Could not determine Cura's data storage directory")
                return
            themes_dir = os.path.join(user_data_path, "themes")
            
            # Create themes directory if it doesn't exist
            os.makedirs(themes_dir, exist_ok=True)
            
            # Create sanitized theme directory name
            sanitized_name = theme_name.lower().replace(' ', '-').replace('_', '-')
            # Remove invalid characters
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                sanitized_name = sanitized_name.replace(char, '-')
            
            theme_dir = os.path.join(themes_dir, sanitized_name)
            
            # Create theme directory
            os.makedirs(theme_dir, exist_ok=True)
            
            # Save theme.json
            theme_file = os.path.join(theme_dir, "theme.json")
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(self.theme_data, f, indent=4, ensure_ascii=False)
            
            if show_message:
                QMessageBox.information(self, "Success", 
                                      f"Theme '{theme_name}' exported successfully!\n\n" +
                                      f"Location: {theme_dir}\n\n" +
                                      "Open preferences and select the new theme.\n"
                                      "Restart Cura for the theme to be applied.")
            return sanitized_name
        except ImportError:
            QMessageBox.critical(self, "Error", 
                               "Could not access Cura's Resources API. This plugin must be run within Cura.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export theme: {str(e)}")

    def _setActiveExport(self):
        """Export the theme and set it as active in Cura's preferences."""
        sanitized_name = self._exportTheme(show_message=False)
        if not sanitized_name:
            QMessageBox.critical(self, "Error", f"Failed to export and set theme.")
            return
        cura_app = Application.getInstance()
        preferences = cura_app.getPreferences()
        preferences.setValue("general/theme", sanitized_name)
        QMessageBox.information(self, "Success",
                                f"Theme exported and set as active successfully! Restart Cura for the theme to be applied.")

    def _loadActiveTheme(self):
        """Load the currently active theme from Cura's preferences."""
        cura_app = Application.getInstance()
        preferences = cura_app.getPreferences()
        active_theme_name = preferences.getValue("general/theme")
        if not active_theme_name:
            QMessageBox.warning(self, "Warning", "No active theme found in preferences.")
            return
        themes_dir = os.path.join(Resources.getDataStoragePath(), "themes")
        theme_dir = os.path.join(themes_dir, active_theme_name)
        if not os.path.exists(theme_dir):
            QMessageBox.warning(self, "Warning", "Active theme directory not found. Plugin cannot load default themes.")
            return
        theme_file = os.path.join(theme_dir, "theme.json")
        self._loadTheme(theme_file)
        return
