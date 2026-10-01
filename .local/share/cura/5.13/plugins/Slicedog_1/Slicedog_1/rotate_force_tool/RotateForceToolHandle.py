from UM.Math.Vector import Vector
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Scene.ToolHandle import ToolHandle

import numpy as np

class RotateForceToolHandle(ToolHandle):
    """
    Slightly updated RotateToolHandle - main difference is change in centering.
    """
    def __init__(self, extension, parent = None):
        super().__init__(parent)

        self._extension = extension
        self._auto_scale = False

        self._name = "RotateForceToolHandle"
        self._inner_radius = 40
        self._outer_radius = 40.5
        self._line_width = 0.3
        self._active_inner_radius = 37
        self._active_outer_radius = 44
        self._active_line_width = 0.6
        self._mesh_origin = Vector()

    def getMeshOrigin(self):
        return self._mesh_origin

    def buildMesh(self):
        center = self._extension.getCurrentForceCenter()
        W = self._extension.getHighlightManager().getWorldOrientation().toMatrix()
        self._mesh_origin = center.preMultiply(W)

        #SOLIDMESH
        mb = MeshBuilder()

        mb.addDonut(
            inner_radius = self._inner_radius,
            outer_radius = self._outer_radius,
            width = self._line_width,
            color = self._z_axis_color,
            center = self._mesh_origin
        )

        mb.addDonut(
            inner_radius = self._inner_radius,
            outer_radius = self._outer_radius,
            width = self._line_width,
            axis = Vector.Unit_X,
            angle = np.pi / 2,
            color = self._y_axis_color,
            center = self._mesh_origin
        )

        mb.addDonut(
            inner_radius = self._inner_radius,
            outer_radius = self._outer_radius,
            width = self._line_width,
            axis = Vector.Unit_Y,
            angle = np.pi / 2,
            color = self._x_axis_color,
            center = self._mesh_origin
        )

        self.setSolidMesh(mb.build())

        #SELECTIONMESH
        mb = MeshBuilder()

        mb.addDonut(
            inner_radius = self._active_inner_radius,
            outer_radius = self._active_outer_radius,
            width = self._active_line_width,
            color = ToolHandle.ZAxisSelectionColor,
            center = self._mesh_origin
        )

        mb.addDonut(
            inner_radius = self._active_inner_radius,
            outer_radius = self._active_outer_radius,
            width = self._active_line_width,
            axis = Vector.Unit_X,
            angle = np.pi / 2,
            color = ToolHandle.YAxisSelectionColor,
            center = self._mesh_origin
        )

        mb.addDonut(
            inner_radius = self._active_inner_radius,
            outer_radius = self._active_outer_radius,
            width = self._active_line_width,
            axis = Vector.Unit_Y,
            angle = np.pi / 2,
            color = ToolHandle.XAxisSelectionColor,
            center = self._mesh_origin
        )

        self.setSelectionMesh(mb.build())
