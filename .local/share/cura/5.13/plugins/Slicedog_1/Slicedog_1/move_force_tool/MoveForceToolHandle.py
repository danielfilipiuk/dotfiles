from UM.Math.Vector import Vector
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Scene.ToolHandle import ToolHandle
from UM.Scene.Selection import Selection

import numpy as np

from Slicedog_1.utils.mesh_utils import paintArrow
from Slicedog_1.geometry_analyzer import geometry_analyzer

class MoveForceToolHandle(ToolHandle):
    """
    Slightly updated TranslateToolHandle - main difference is that it's aligned with the force vector.
    """
    def __init__(self, extension, parent = None):
        super().__init__(parent)
        self._name = "MoveForceToolHandle"
        self._enabled_axis = [self.XAxis, self.YAxis, self.ZAxis]

        self._extension = extension
        self._auto_scale = False

        self._arrow_head_length = 4
        self._arrow_tail_length = 30
        self._arrow_total_length = self._arrow_head_length + self._arrow_tail_length
        self._arrow_head_width = 2.8
        self._arrow_tail_width = 0.8

        self._x_axis_vector = None
        self._y_axis_vector = None
        self._z_axis_vector = None

    def _onSelectionCenterChanged(self) -> None:
        if self._enabled:
            obj = Selection.getSelectedObject(0) # which index to use?
            if obj:
                self.setTransformation(obj.getLocalTransformation())

    def buildMesh(self):
        if not self._extension.getCurrentForceFacesFlat():
        # if not self._extension.getCurrentlySelectedFacesHelper().current_force.facesFlat:
            return

        center = self._extension.getCurrentForceCenter()
        # center = self._extension.getCurrentlySelectedFacesHelper().current_force.center

        if self._extension.getHighlightManager().getMeshData() is None:
            return
        _, x = geometry_analyzer.getFacePlaneVectors(self._extension.getHighlightManager().getMeshData(),
                                                     self._extension.getCurrentForceFacesFlat()[0])

        # face plane divides space in two; a normal vector points to the first one, but we want our 'x' to point to second one
        x *= -1

        base = Vector(1, 0, 0)
        if (1 - np.abs(x.dot(base))) < 0.1:
            base = Vector(0, 1, 0)

        y = x.cross(base)
        z = x.cross(y)

        self._x_axis_vector = x
        self._y_axis_vector = y
        self._z_axis_vector = z

        mb = MeshBuilder()

        paintArrow(mb, self._x_axis_color, center, x, self._arrow_head_length, self._arrow_head_width,
                   self._arrow_tail_length, self._arrow_tail_width)
        paintArrow(mb, self._y_axis_color, center, y, self._arrow_head_length, self._arrow_head_width,
                   self._arrow_tail_length, self._arrow_tail_width)
        paintArrow(mb, self._z_axis_color, center, z, self._arrow_head_length, self._arrow_head_width,
                   self._arrow_tail_length, self._arrow_tail_width)
        self.setSolidMesh(mb.build())
        mb = MeshBuilder()
        paintArrow(mb, ToolHandle.XAxisSelectionColor, center, x, self._arrow_head_length, self._arrow_head_width,
                   self._arrow_tail_length, self._arrow_tail_width)
        paintArrow(mb, ToolHandle.YAxisSelectionColor, center, y, self._arrow_head_length, self._arrow_head_width,
                   self._arrow_tail_length, self._arrow_tail_width)
        paintArrow(mb, ToolHandle.ZAxisSelectionColor, center, z, self._arrow_head_length, self._arrow_head_width,
                   self._arrow_tail_length, self._arrow_tail_width)
        self.setSelectionMesh(mb.build())

    def getXAxisVector(self):
        return self._x_axis_vector

    def getYAxisVector(self):
        return self._y_axis_vector

    def getZAxisVector(self):
        return self._z_axis_vector
