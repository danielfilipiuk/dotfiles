import threading
import json

from PyQt6 import QtCore

from UM.Math.Vector import Vector

from Slicedog_1.utils.slicedog_dataclasses import CurrentForce

class SlicedogApiWrapper(QtCore.QObject):
    logInGoogleCompleted = QtCore.pyqtSignal(str, bool)
    accessTokenChanged = QtCore.pyqtSignal()
    currentForceChanged = QtCore.pyqtSignal(CurrentForce)
    surfaceSelectionChanged = QtCore.pyqtSignal(str)
    objectsChanged = QtCore.pyqtSignal('QVariant')
    anchorsChanged = QtCore.pyqtSignal('QVariant')
    forcesChanged = QtCore.pyqtSignal('QVariant')
    optimizationStrategyChanged = QtCore.pyqtSignal(str)
    optimizationSafetyRatioChanged = QtCore.pyqtSignal(float)
    optimizationAutoLowerSafetyChanged = QtCore.pyqtSignal(bool)
    currentStepChanged = QtCore.pyqtSignal(int)
    stepsConfirmedFlagsChanged = QtCore.pyqtSignal(list)
    rotationActiveChanged = QtCore.pyqtSignal(bool)
    selectMultipleAreasChanged = QtCore.pyqtSignal(bool)
    feedbackChanged = QtCore.pyqtSignal(str)
    iterationFeedbackChanged = QtCore.pyqtSignal(str)
    statusFeedbackChanged = QtCore.pyqtSignal(str)
    popupRequested = QtCore.pyqtSignal(str)

    def __init__(self, extension):
        super().__init__()
        self._extension = extension
        self.logInGoogleCompleted.connect(self._extension.onLogInGoogleCompleted)

        # TODO review signals - I think there might be more emitting than necessary
        extension.onChanged("current_force", self._onCurrentForceChanged)
        extension.onChanged("surface_selection", self._onSurfaceSelectionChanged)
        extension.onChanged("objects", self._onObjectsChanged)
        extension.onChanged("anchors", self._onAnchorsChanged)
        extension.onChanged("forces", self._onForcesChanged)
        extension.onChanged("optimization_strategy", self._onOptimizationStrategyChanged)
        extension.onChanged("optimization_safety_ratio", self._onOptimizationSafetyRatioChanged)
        extension.onChanged("optimization_auto_lower_safety_ratio", self._onOptimizationAutoLowerSafetyChanged)
        extension.onChanged("access_token", self._onAccessTokenChanged)
        extension.onChanged("current_step", self._onCurrentStepChanged)
        extension.onChanged("steps_confirmed_flags", self._onStepsConfirmedFlagsChanged)
        extension.onChanged("rotation_active", self._onRotationActiveChanged)
        extension.onChanged("select_multiple_areas", self._onSelectMultipleAreasChanged)
        extension.onChanged("feedback", self._onFeedbackChanged)
        extension.onChanged("iteration_feedback", self._onIterationFeedbackChanged)
        extension.onChanged("status_feedback", self._onStatusFeedbackChanged)
        extension.onChanged("popup_requested", self._onPopupRequested)

        # emit default values
        self.surfaceSelectionChanged.emit(self.surfaceSelection)
        self.optimizationStrategyChanged.emit(self.optimizationStrategy)
        self.optimizationSafetyRatioChanged.emit(self.optimizationSafetyRatio)
        self.optimizationAutoLowerSafetyChanged.emit(self.optimizationAutoLowerSafetyRatio)

    def _onCurrentForceChanged(self, val):
        self.currentForceChanged.emit(val)

    def _onSurfaceSelectionChanged(self, val):
        self.surfaceSelectionChanged.emit(val)

    def _onObjectsChanged(self, val):
        self.objectsChanged.emit(val)

    def _onAnchorsChanged(self, val):
        self.anchorsChanged.emit(val)

    def _onForcesChanged(self, val):
        self.forcesChanged.emit(val)

    def _onOptimizationStrategyChanged(self, val):
        self.optimizationStrategyChanged.emit(val)

    def _onOptimizationSafetyRatioChanged(self, val):
        self.optimizationSafetyRatioChanged.emit(val)

    def _onOptimizationAutoLowerSafetyChanged(self, val):
        self.optimizationAutoLowerSafetyChanged.emit(val)

    def _onAccessTokenChanged(self):
        self.accessTokenChanged.emit()

    def _onCurrentStepChanged(self, val):
        self.currentStepChanged.emit(val)

    def _onStepsConfirmedFlagsChanged(self, val):
        self.stepsConfirmedFlagsChanged.emit(val)

    def _onRotationActiveChanged(self, val):
        self.rotationActiveChanged.emit(val)

    def _onSelectMultipleAreasChanged(self, val):
        self.selectMultipleAreasChanged.emit(val)

    def _onFeedbackChanged(self, val):
        self.feedbackChanged.emit(val)

    def _onIterationFeedbackChanged(self, val):
        self.iterationFeedbackChanged.emit(val)

    def _onStatusFeedbackChanged(self, val):
        self.statusFeedbackChanged.emit(val)

    def _onPopupRequested(self, popup_type, message=None):
        self.popupRequested.emit(json.dumps({
            "type": popup_type,
            "message": message
        }))

    @QtCore.pyqtSlot()
    def resetCurrentForce(self):
        self._extension.resetCurrentForce()

    @QtCore.pyqtProperty('QVariant', notify=currentForceChanged)
    def currentForceAsDict(self):
        return self._extension.getCurrentForce().to_dict()
        # return self._extension.getCurrentForceAsDict()

    @QtCore.pyqtProperty(CurrentForce, notify=currentForceChanged)
    def currentForce(self):
        return self._extension.getCurrentForce()

    @currentForce.setter
    def currentForce(self, value):
        self._extension.setCurrentForce(value)

    @QtCore.pyqtProperty(list, notify=currentForceChanged)
    def currentForceFaces(self):
        return self._extension.getCurrentForceFaces()

    @QtCore.pyqtProperty(list, notify=currentForceChanged)
    def currentForceFacesFlat(self):
        return self._extension.getCurrentForceFacesFlat()

    @currentForceFaces.setter
    def currentForceFaces(self, f):
        self._extension.setCurrentForceFaces(f)

    @QtCore.pyqtProperty(bool, notify=currentForceChanged)
    def currentForcePush(self):
        return self._extension.getCurrentForcePush()

    @currentForcePush.setter
    def currentForcePush(self, push):
        self._extension.setCurrentForcePush(push)

    @QtCore.pyqtProperty(float, notify=currentForceChanged)
    def currentForceMagnitude(self):
        return self._extension.getCurrentForceMagnitude()

    @currentForceMagnitude.setter
    def currentForceMagnitude(self, m):
        self._extension.setCurrentForceMagnitude(m)

    @QtCore.pyqtProperty(str, notify=currentForceChanged)
    def currentForceUnit(self):
        return self._extension.getCurrentForceUnit()

    @currentForceUnit.setter
    def currentForceUnit(self, u):
        self._extension.setCurrentForceUnit(u)

    @QtCore.pyqtProperty(bool, notify=currentForceChanged)
    def isCurrentForcePrecise(self):
        return self._extension.isCurrentForcePrecise()

    @QtCore.pyqtProperty(Vector, notify=currentForceChanged)
    def currentForceCenter(self):
        return self._extension.getCurrentForceCenter()

    @currentForceCenter.setter
    def currentForceCenter(self, oc):
        self._extension.setCurrentForceCenter(oc)

    @QtCore.pyqtProperty(Vector, notify=currentForceChanged)
    def currentForceDirection(self):
        return self._extension.getCurrentForceDirection()

    @currentForceDirection.setter
    def currentForceDirection(self, of):
        self._extension.setCurrentForceDirection(of)

    @QtCore.pyqtProperty(str, notify=currentForceChanged)
    def currentForceId(self):
        return self._extension.getCurrentForceId()

    @currentForceId.setter
    def currentForceId(self, o):
        self._extension.setCurrentForceId(o)

    @QtCore.pyqtProperty(bool, notify=currentForceChanged)
    def currentForceConfirmed(self):
        return self._extension.getCurrentForceConfirmed()

    @currentForceConfirmed.setter
    def currentForceConfirmed(self, value):
        self._extension.setCurrentForceConfirmed(value)

    @QtCore.pyqtProperty(str, notify=surfaceSelectionChanged)
    def surfaceSelection(self):
        return self._extension.getSurfaceSelection()

    @surfaceSelection.setter
    def surfaceSelection(self, o):
        self._extension.setSurfaceSelection(o)

    @surfaceSelection.getter
    def surfaceSelection(self):
        return self._extension.getSurfaceSelection()

    @QtCore.pyqtProperty(list, notify=objectsChanged)
    def objectsAsList(self):
        return self._extension.getObjectsAsList()

    @QtCore.pyqtProperty(list, notify=anchorsChanged)
    def anchorsAsList(self):
        return self._extension.getAnchorsAsList()

    @QtCore.pyqtProperty(bool, notify=forcesChanged)
    def allForcesConfirmed(self):
        return self._extension.areAllForcesConfirmed()

    @QtCore.pyqtProperty(bool, notify=anchorsChanged)
    def allAnchorsConfirmed(self):
        return self._extension.areAllAnchorsConfirmed()

    @QtCore.pyqtProperty(list, notify=forcesChanged)
    def forcesAsList(self):
        return self._extension.getForcesAsList()

    @QtCore.pyqtSlot()
    def updateAnchorsWithCurrent(self):
        self._extension.updateAnchors(self._extension.getCurrentForce())

    @QtCore.pyqtSlot()
    def updateForcesWithCurrent(self):
        self._extension.updateForces(self._extension.getCurrentForce())

    @QtCore.pyqtSlot('QVariant')
    def updateForces(self, value):
        if hasattr(value, 'toVariant'):
            value = value.toVariant()
        self._extension.updateForces(value)

    @QtCore.pyqtSlot()
    def removeCurrentForce(self):
        self._extension.removeCurrentForce()

    @QtCore.pyqtSlot()
    def removeCurrentAnchor(self):
        self._extension.removeCurrentAnchor()

    @QtCore.pyqtSlot(str)
    def removeForce(self, force_id):
        self._extension.removeForce(force_id)

    @QtCore.pyqtSlot(str)
    def removeAnchor(self, anchor_id):
        self._extension.removeAnchor(anchor_id)

    @QtCore.pyqtSlot(str)
    def selectForce(self, force_id):
        self._extension.selectForce(force_id)

    @QtCore.pyqtSlot(str)
    def selectAnchor(self, anchor_id):
        self._extension.selectAnchor(anchor_id)

    @QtCore.pyqtProperty(str, notify=optimizationStrategyChanged)
    def optimizationStrategy(self):
        return self._extension.getOptimizationStrategy()

    @optimizationStrategy.getter
    def optimizationStrategy(self):
        return self._extension.getOptimizationStrategy()

    @optimizationStrategy.setter
    def optimizationStrategy(self, o):
        self._extension.setOptimizationStrategy(o)

    @QtCore.pyqtProperty(float, notify=optimizationSafetyRatioChanged)
    def optimizationSafetyRatio(self):
        return self._extension.getOptimizationSafetyRatio()

    @optimizationSafetyRatio.getter
    def optimizationSafetyRatio(self):
        return self._extension.getOptimizationSafetyRatio()

    @optimizationSafetyRatio.setter
    def optimizationSafetyRatio(self, o):
        self._extension.setOptimizationSafetyRatio(o)

    @QtCore.pyqtProperty(bool, notify=optimizationAutoLowerSafetyChanged)
    def optimizationAutoLowerSafetyRatio(self):
        return self._extension.getOptimizationAutoLowerSafetyRatio()

    @optimizationAutoLowerSafetyRatio.getter
    def optimizationAutoLowerSafetyRatio(self):
        return self._extension.getOptimizationAutoLowerSafetyRatio()

    @optimizationAutoLowerSafetyRatio.setter
    def optimizationAutoLowerSafetyRatio(self, o):
        self._extension.setOptimizationAutoLowerSafetyRatio(o)

    @QtCore.pyqtProperty(int, notify=currentStepChanged)
    def currentStep(self):
        return self._extension.getCurrentStep()

    @currentStep.getter
    def currentStep(self):
        return self._extension.getCurrentStep()

    @currentStep.setter
    def currentStep(self, step):
        self._extension.setCurrentStep(step)

    @QtCore.pyqtProperty(bool, notify=selectMultipleAreasChanged)
    def selectMultipleAreas(self):
        return self._extension.isSelectMultipleAreas()

    @selectMultipleAreas.getter
    def selectMultipleAreas(self):
        return self._extension.isSelectMultipleAreas()

    @selectMultipleAreas.setter
    def selectMultipleAreas(self, val):
        self._extension.setSelectMultipleAreas(val)

    @QtCore.pyqtProperty(str, notify=feedbackChanged)
    def lastFeedback(self):
        return self._extension.getLastFeedback()

    @QtCore.pyqtProperty(str, notify=statusFeedbackChanged)
    def lastStatusFeedback(self):
        return self._extension.getLastStatusFeedback()

    @QtCore.pyqtProperty(int, notify=statusFeedbackChanged)
    def lastFeedbackStatusIndex(self):
        return self._extension.getLastFeedbackStatusIndex()

    @QtCore.pyqtProperty(str, notify=iterationFeedbackChanged)
    def lastIterationFeedback(self):
        return self._extension.getLastIterationFeedback()

    @QtCore.pyqtProperty(str, notify=iterationFeedbackChanged)
    def currentIterationInfo(self):
        return self._extension.getCurrentIterationInfo()

    @QtCore.pyqtSlot(result=bool)
    def confirmCurrentStep(self):
        return self._extension.confirmCurrentStep()

    @QtCore.pyqtProperty(list, notify=currentStepChanged)
    def stepsConfirmedFlags(self):
        return self._extension.getStepsConfirmedFlags()

    @QtCore.pyqtSlot()
    def logInWithGoogle(self):
        # TODO: this is just quick fix of flow.run_local_server() hanging when browser is closed, but should be ok
        threading.Thread(target=lambda: self._extension.logInWithGoogle(self.logInGoogleCompleted.emit, False), daemon=True).start()

    @QtCore.pyqtSlot()
    def registerWithGoogle(self):
        # TODO: this is just quick fix of flow.run_local_server() hanging when browser is closed, but should be ok
        threading.Thread(target=lambda: self._extension.logInWithGoogle(self.logInGoogleCompleted.emit, True), daemon=True).start()

    @QtCore.pyqtSlot()
    def logOut(self):
        self._extension.logOut()

    @QtCore.pyqtProperty(bool, notify=accessTokenChanged)
    def isLoggedIn(self):
        return self._extension.isLoggedIn()

    @QtCore.pyqtProperty(bool, notify=rotationActiveChanged)
    def rotationActive(self):
        return self._extension.getRotationActive()

    @rotationActive.getter
    def rotationActive(self):
        return self._extension.getRotationActive()

    @rotationActive.setter
    def rotationActive(self, active):
        self._extension.setRotationActive(active)

    @QtCore.pyqtSlot(result=bool)
    def optimizeStl(self):
        return self._extension.exportStl()

    @QtCore.pyqtSlot()
    def importLastResult(self):
        self._extension.importLastResult()

    @QtCore.pyqtSlot(float, str, result=bool)
    def confirmCurrentForce(self, magnitude, unit):
        return self._extension.confirmCurrentForce(magnitude, unit)

    @QtCore.pyqtSlot(result=bool)
    def confirmCurrentAnchor(self):
        return self._extension.confirmCurrentAnchor()

    @QtCore.pyqtSlot(str)
    def cancelOptimization(self, action):
        self._extension.cancelOptimization(action)

    @QtCore.pyqtSlot()
    def updateExtruderSettings(self):
        return self._extension.updateExtruderSettings()