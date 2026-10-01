from UM.i18n import i18nCatalog
from UM.Application import Application
from UM.Event import Event, MouseEvent, KeyEvent
from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle
from UM.Tool import Tool
from UM.Math.Vector import Vector
from UM.Math.Plane import Plane

from typing import cast
from copy import copy
import time

from . import MoveForceToolHandle

i18n_catalog = i18nCatalog("Slicedog_1")

class MoveForceTool(Tool):
    """
    Slightly update TranslateTool - we need to correctly move the force vector regardless of its initial orientation.
    """
    def __init__(self, extension):
        super().__init__()
        self._extension = extension
        self._handle = MoveForceToolHandle.MoveForceToolHandle(self._extension)
        self._grid_snap = False
        self._grid_size = 10
        self._moved = False
        self._distance_update_time = None
        self._distance = None
        self._max_distance_length = 400
        self._extension.onChanged("current_force", self._onCenterChanged)
        # self._extension.getCurrentlySelectedFacesHelper().currentForceChanged.connect(self.__onCenterChanged)
        self._selected_axis_vector = None
        Selection.selectedFaceChanged.connect(self._onSelectedFaceChanged)

    # TODO: _onSomething methods conditions if active tool etc. revision
    def _onSelectedFaceChanged(self):
        application = Application.getInstance()
        controller = application.getController()
        if self == controller.getActiveTool():
            self.getHandle().setEnabled(not Selection.getFaceSelectMode())
            self.getHandle().buildMesh()

    def _onCenterChanged(self, _):
        self.getHandle().buildMesh()

    def event(self, event: Event) -> bool:
        super().event(event)

        if event.type == Event.KeyPressEvent and cast(KeyEvent, event).key == KeyEvent.ShiftKey:
            return False

        if event.type == Event.MousePressEvent and self._controller.getToolsEnabled():
            if MouseEvent.LeftButton not in cast(MouseEvent, event).buttons:
                return False

            if not self._selection_pass:
                return False
            selection_id = self._selection_pass.getIdAtPosition(cast(MouseEvent, event).x, cast(MouseEvent, event).y)
            if not selection_id:
                return False

            self._moved = False

            camera = self._controller.getScene().getActiveCamera()
            if not camera:
                return False

            camera_direction = camera.getPosition().normalized()

            W = self.getHandle().getWorldOrientation().toMatrix()

            if selection_id == ToolHandle.XAxis:
                n_w = self.getHandle().getXAxisVector().preMultiply(W)
                projection = (camera_direction.dot(n_w) / n_w.dot(n_w)) * n_w
                self._selected_axis_vector = ToolHandle.XAxis
            elif selection_id == ToolHandle.YAxis:
                n_w = self.getHandle().getYAxisVector().preMultiply(W)
                projection = (camera_direction.dot(n_w) / n_w.dot(n_w)) * n_w
                self._selected_axis_vector = ToolHandle.YAxis
            elif selection_id == ToolHandle.ZAxis:
                n_w = self.getHandle().getZAxisVector().preMultiply(W)
                projection = (camera_direction.dot(n_w) / n_w.dot(n_w)) * n_w
                self._selected_axis_vector = ToolHandle.ZAxis
            else:
                self._selected_axis_vector = None
                return False

            plane_vector = (camera_direction - projection).normalized()

            self.setDragPlane(Plane(plane_vector, 0))
            return True

        if event.type == Event.MouseMoveEvent:
            if not self.getDragPlane():
                return False

            x = cast(MouseEvent, event).x
            y = cast(MouseEvent, event).y

            if not self.getDragStart():
                self.setDragStart(x, y)
                return False

            drag = self.getDragVector(x, y)
            if drag:
                if self._grid_snap and drag.length() < self._grid_size:
                    return False

                W = self.getHandle().getWorldOrientation().toMatrix()

                if self._selected_axis_vector == ToolHandle.XAxis:
                    n_w = self.getHandle().getXAxisVector().preMultiply(W)
                elif self._selected_axis_vector == ToolHandle.YAxis:
                    n_w = self.getHandle().getYAxisVector().preMultiply(W)
                elif self._selected_axis_vector == ToolHandle.ZAxis:
                    n_w = self.getHandle().getZAxisVector().preMultiply(W)
                else:
                    self._selected_axis_vector = None
                    return False

                drag = (drag.dot(n_w) / n_w.dot(n_w)) * n_w
                drag = drag.preMultiply(W.getInverse())

                if not self._moved:
                    self._moved = True
                    self._distance = Vector(0, 0, 0)

                if not self._distance:
                    self._distance = Vector(0, 0, 0)
                self._distance += drag

                if self._distance.length() > self._max_distance_length:
                    self._distance = self._distance.normalized() * self._max_distance_length
                else:
                    self.setDragStart(x, y)

                oc = self._extension.getCurrentForceCenter()
                # oc = self._extension.getCurrentlySelectedFacesHelper().current_force.center
                noc = oc + self._distance
                cfc = copy(self._extension.getCurrentForce())
                # cfc = copy(self._extension.getCurrentlySelectedFacesHelper().current_force)
                cfc.center = noc
                self._extension.getHighlightManager().drawSavedObjectsAndCurrentSelection(
                    current_selection=cfc, plot_arrow=True
                )

            # Rate-limit the angle change notification
            # This is done to prevent the UI from being flooded with property change notifications,
            # which in turn would trigger constant repaints.
            new_time = time.monotonic()
            if not self._distance_update_time or new_time - self._distance_update_time > 0.1:
                self.propertyChanged.emit()
                self._distance_update_time = new_time

            return True

        if event.type == Event.MouseReleaseEvent:
            if self.getDragPlane():
                if self._distance is not None:
                    oc = self._extension.getCurrentForceCenter()
                    # oc = self._extension.getCurrentlySelectedFacesHelper().current_force.center
                    noc = oc + self._distance
                    self._extension.setCurrentForceCenter(noc)
                    # self._extension.getCurrentlySelectedFacesHelper().setProperty('center', noc)
                self._distance = None
                self.propertyChanged.emit()
                self.setDragPlane(None)
                self.setDragStart(cast(MouseEvent, event).x, cast(MouseEvent, event).y)
                return True

        return False
