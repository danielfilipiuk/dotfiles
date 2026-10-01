from PyQt6 import QtCore, QtWidgets

from UM.i18n import i18nCatalog
from UM.Tool import Tool
from UM.Scene.Selection import Selection
from UM.Application import Application
from UM.Message import Message
from UM.Math.Vector import Vector
from UM.Event import Event, MouseEvent, KeyEvent

from typing import cast

from Slicedog_1.message_manager.MessageType import MessageType

i18n_catalog = i18nCatalog("Slicedog_1")

class CalculationThread(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(str)

    def __init__(self, extension):
        super().__init__()
        self._extension = extension

    def run(self):
        self._extension.setProgressCallback(self._sendFeedback)
        self._extension.determineObjectFaces()
        if self._extension.getCurrentForceFacesFlat():
            self._extension.getHighlightManager().drawSavedObjectsAndCurrentSelection(
                current_selection=self._extension.getCurrentForce(),
                plot_arrow=self._extension.getCurrentStep() == 0 and not self._extension.getCurrentForceConfirmed()
            )
        self.finished.emit()

    def _sendFeedback(self, message):
        self.progress.emit(message)

class DefinitionTool(Tool):
    def __init__(self, extension):
        super().__init__()
        self._extension = extension
        Selection.selectedFaceChanged.connect(self._onSelectedFaceChanged)
        self._extension.onChanged("current_force", self._onSavedFaceSelected)
        self._calculation_thread = None

    def _onSelectedFaceChanged(self):
        application = Application.getInstance()
        controller = application.getController()
        if self == controller.getActiveTool():

            if self._calculation_thread and self._calculation_thread.isRunning():
                return

            # TODO: this allows users to redefine things
            # if self._extension.isOptimizationRunning():
            #     return

            self._extension.getMessageManager().hideAllMessages()
            if not Selection.getFaceSelectMode():
                Selection.setFaceSelectMode(True)
                return
            selected_face = Selection.getSelectedFace()

            self._extension.setFace(selected_face)
            if selected_face is None:
                return

            if self._extension.determineIfSaved():
                return

            if self._extension.getCurrentStep() > 1:
                return

            if not self._extension.isSelectedMeshCached():
                self._extension.getMessageManager().showMessage(MessageType.MESH_ANALYSIS_RUNNING)

            self._calculation_thread = CalculationThread(self._extension)
            self._calculation_thread.progress.connect(self.onFeedbackUpdated)
            self._calculation_thread.finished.connect(self.onCalculationFinished)
            self._calculation_thread.start()
        elif controller.getActiveTool() is None:
            self._extension.resetCurrentForce()
            self._extension.getHighlightManager().drawSavedObjectsAndCurrentSelection()

    def _onSavedFaceSelected(self, _):
        application = Application.getInstance()
        controller = application.getController()
        if self == controller.getActiveTool():
            if self._extension.getCurrentForceFacesFlat() and self._extension.getCurrentForceId():
                self._extension.getHighlightManager().drawSavedObjectsAndCurrentSelection(
                    current_selection=self._extension.getCurrentForce()
                )

    # def event(self, event):
    #     super().event(event)
    #     if event.type in [Event.KeyPressEvent, Event.KeyReleaseEvent] and cast(KeyEvent, event).key == KeyEvent.ControlKey:
    #         modifiers = QtWidgets.QApplication.keyboardModifiers()
    #         ctrl_active = not modifiers & QtCore.Qt.KeyboardModifier.ControlModifier
    #         self._is_ctrl_active = ctrl_active

    def onFeedbackUpdated(self, message):
        self._extension.getMessageManager().showMessage(MessageType.MESH_ANALYSIS_RUNNING, message)

    def onCalculationFinished(self):
        self._extension.getMessageManager().hideMessage(MessageType.MESH_ANALYSIS_RUNNING)

