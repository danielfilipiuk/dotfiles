from UM.Event import Event, MouseEvent, KeyEvent
from UM.Math.Plane import Plane
from UM.Math.Quaternion import Quaternion
from UM.Math.Vector import Vector
from UM.Scene.ToolHandle import ToolHandle
from UM.Tool import Tool
from UM.i18n import i18nCatalog
from UM.Application import Application
from UM.Scene.Selection import Selection

import math
import time
from copy import copy

from Slicedog_1.rotate_force_tool import RotateForceToolHandle

class RotateForceTool(Tool):
    """
    Slightly updated RotateTool - we don't apply rotation to the model, but we change orientation of the force vector.
    """
    def __init__(self, extension):
        super().__init__()
        self._extension = extension
        self._handle = RotateForceToolHandle.RotateForceToolHandle(self._extension)

        self._snap_rotation = True
        self._snap_angle = math.radians(1)

        self._angle = None
        self._angle_update_time = None

        self._rotating = False
        self._saved_node_positions = []
        Selection.selectedFaceChanged.connect(self._onSelectedFaceChanged)
        self._extension.onChanged("current_force", self._onCenterChanged)
        # self._extension.getCurrentlySelectedFacesHelper().currentForceChanged.connect(self.__onCenterChanged)

    # TODO: _onSomething methods conditions if active tool etc. revision
    def _onSelectedFaceChanged(self):
        application = Application.getInstance()
        controller = application.getController()
        if self == controller.getActiveTool():
            self._handle.setEnabled(not Selection.getFaceSelectMode())
            self._handle.buildMesh()

    def _onCenterChanged(self, _):
        self.getHandle().buildMesh()

    def event(self, event):
        super().event(event)

        if event.type == Event.MousePressEvent and self._controller.getToolsEnabled():
            # Start a rotate operation
            if MouseEvent.LeftButton not in event.buttons:
                return False

            selection_id = self._selection_pass.getIdAtPosition(event.x, event.y)
            if not selection_id:
                return False

            # workaround
            if self._handle.AllAxis == selection_id:
                self._extension.setCurrentForcePush(not self._extension.getCurrentForcePush())
                self._extension.getHighlightManager().drawSavedObjectsAndCurrentSelection(
                    current_selection=self._extension.getCurrentForce(),
                    plot_arrow=True
                )
                return True
            elif self._handle.isAxis(selection_id):
                self.setLockedAxis(selection_id)
            else:
                # Not clicked on an axis: do nothing.
                return False

            handle_position = self._handle.getMeshOrigin()

            # Save the current positions of the node, as we want to rotate around their current centres
            self._saved_node_positions = []
            for node in self._getSelectedObjectsWithoutSelectedAncestors():
                self._saved_node_positions.append((node, node.getPosition()))

            if selection_id == ToolHandle.XAxis:
                self.setDragPlane(Plane(Vector.Unit_X, handle_position.x))
            elif selection_id == ToolHandle.YAxis:
                self.setDragPlane(Plane(Vector.Unit_Y, handle_position.y))
            elif self._locked_axis == ToolHandle.ZAxis:
                self.setDragPlane(Plane(Vector.Unit_Z, handle_position.z))
            else:
                self.setDragPlane(Plane(Vector.Unit_Y, handle_position.y))

            self.setDragStart(event.x, event.y)
            self._rotating = False
            self._angle = 0
            return True

        if event.type == Event.MouseMoveEvent:
            if not self.getDragPlane():
                return False

            if not self.getDragStart():
                self.setDragStart(event.x, event.y)
                if not self.getDragStart():
                    return False

            if not self._rotating:
                self._rotating = True

            handle_position = self._handle.getMeshOrigin()

            drag_start = (self.getDragStart() - handle_position).normalized()
            drag_position = self.getDragPosition(event.x, event.y)
            if not drag_position:
                return False
            drag_end = (drag_position - handle_position).normalized()

            try:
                angle = math.acos(drag_start.dot(drag_end))
            except ValueError:
                angle = 0

            if self._snap_rotation:
                angle = int(angle / self._snap_angle) * self._snap_angle
                if angle == 0:
                    return False

            R = self._extension.getHighlightManager().getWorldOrientation().toMatrix().getInverse()
            if self.getLockedAxis() == ToolHandle.XAxis:
                direction = 1 if Vector.Unit_X.dot(drag_start.cross(drag_end)) > 0 else -1
                unit_vector = Vector.Unit_X
            elif self.getLockedAxis() == ToolHandle.YAxis:
                direction = 1 if Vector.Unit_Y.dot(drag_start.cross(drag_end)) > 0 else -1
                unit_vector = Vector.Unit_Y
            elif self.getLockedAxis() == ToolHandle.ZAxis:
                direction = 1 if Vector.Unit_Z.dot(drag_start.cross(drag_end)) > 0 else -1
                unit_vector = Vector.Unit_Z
            else:
                direction = -1
                unit_vector = Vector.Unit_X

            self._angle += direction * angle
            rotation = Quaternion.fromAngleAxis(self._angle, (unit_vector.preMultiply(R))).toMatrix()

            ov = self._extension.getCurrentForceDirection()
            # ov = self._extension.getCurrentlySelectedFacesHelper().force
            nv = ov.preMultiply(rotation)
            cfc = copy(self._extension.getCurrentForce())
            # cfc = copy(self._extension.getCurrentlySelectedFacesHelper().current_force)
            cfc.direction = nv
            self._extension.getHighlightManager().drawSavedObjectsAndCurrentSelection(
                current_selection=cfc,
                plot_arrow=True
            )

            self.setDragStart(event.x, event.y)

            # Rate-limit the angle change notification
            # This is done to prevent the UI from being flooded with property change notifications,
            # which in turn would trigger constant repaints.
            new_time = time.monotonic()
            if not self._angle_update_time or new_time - self._angle_update_time > 0.1:
                self._angle_update_time = new_time
                self.propertyChanged.emit()
            return True

        if event.type == Event.MouseReleaseEvent:
            R = self._extension.getHighlightManager().getWorldOrientation().toMatrix().getInverse()
            if self.getLockedAxis() == ToolHandle.XAxis:
                rotation = Quaternion.fromAngleAxis(self._angle, (Vector.Unit_X.preMultiply(R))).toMatrix()
            elif self.getLockedAxis() == ToolHandle.YAxis:
                rotation = Quaternion.fromAngleAxis(self._angle, (Vector.Unit_Y.preMultiply(R))).toMatrix()
            elif self.getLockedAxis() == ToolHandle.ZAxis:
                rotation = Quaternion.fromAngleAxis(self._angle, (Vector.Unit_Z.preMultiply(R))).toMatrix()
            else:
                rotation = Quaternion().toMatrix()

            ov = self._extension.getCurrentForceDirection()
            # ov = self._extension.getCurrentlySelectedFacesHelper().force
            nv = ov.preMultiply(rotation)
            self._extension.setCurrentForceDirection(nv)
            # self._extension.getCurrentlySelectedFacesHelper().setProperty('force', nv)

            # Finish a rotate operation
            if self.getDragPlane():
                self.setDragPlane(None)
                self.setLockedAxis(ToolHandle.NoAxis)
                self._angle = None
                self.propertyChanged.emit()
                return True

        return False