from PyQt6 import QtCore

from UM.i18n import i18nCatalog
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Color import Color
from UM.Math.Vector import Vector
from UM.Scene.Selection import Selection
from UM.Scene.ToolHandle import ToolHandle

from Slicedog_1.extension.SlicedogExtension import CurrentForce
from Slicedog_1.utils.mesh_utils import paintArrow, paintLock

i18n_catalog = i18nCatalog("Slicedog_1")

# TODO is there a better way to draw overlay mesh?

class QtHighlightManagerWrapper(QtCore.QObject):
    managerChanged = QtCore.pyqtSignal(object)

    def __init__(self, parent=None, manager=None):
        super(QtHighlightManagerWrapper, self).__init__(parent)
        self._highlight_manager = manager

    @QtCore.pyqtProperty(object, notify=managerChanged)
    def highlightManager(self):
        return self._highlight_manager

    @highlightManager.setter
    def highlightManager(self, hm):
        if self._highlight_manager != hm:
            self._highlight_manager = hm
            self.managerChanged.emit(hm)

    @QtCore.pyqtSlot('QVariantMap', bool)
    def drawSavedObjectsAndCurrentSelection(self, current_selection: dict = None, plot_arrow: bool = False):
        if hasattr(current_selection, 'toVariant'):
            current_selection = current_selection.toVariant()
        if isinstance(current_selection, dict):
            current_selection = CurrentForce(**current_selection)
        self._highlight_manager.drawSavedObjectsAndCurrentSelection(current_selection, plot_arrow)


class SlicedogHighlightManager(ToolHandle):
    def __init__(self, extension, parent=None):
        super().__init__(parent)

        self._name = "HighlightsObject"
        self._cached_meshes = {}
        # self._cached_objects = {}
        self._mesh_data = None
        self._extension = extension
        self._auto_scale = False

        self._arrow_head_length = 8
        self._arrow_tail_length = 66
        self._arrow_total_length = self._arrow_head_length + self._arrow_tail_length
        self._arrow_head_width = 2.8
        self._arrow_tail_width = 0.8

    def setEnabled(self, enable: bool):
        super().setEnabled(enable)
        if not enable:
            self.drawSavedObjectsAndCurrentSelection()

    def getMeshData(self):
        return self._mesh_data

    def _addFaceToMeshBuilder(self, mesh_builder, face, color):
        triangle = []
        for vertex in self._mesh_data.getFaceNodes(face):
            triangle.append(Vector(vertex[0], vertex[1], vertex[2]))
        mesh_builder.addFace(triangle[0], triangle[1], triangle[2], color=color)

    def _addSavedObjectsToMeshBuilder(self, mesh_builder, objects, current_selection, color):
        for k, values in objects.items():
            faces = values.facesFlat
            for face in faces:
                if current_selection is None or k != current_selection.id:
                # if current_selection is None or face not in current_selection.facesFlat:
                    self._addFaceToMeshBuilder(mesh_builder, face, color)

    def _addCurrentSelectionToMeshBuilder(self, mesh_builder, current_selection, selection_color, arrow_color,
                                          plot_arrow=False):
        if current_selection is not None and current_selection.facesFlat:
            for face in current_selection.facesFlat:
                self._addFaceToMeshBuilder(mesh_builder, face, selection_color)
            if plot_arrow:
                center = current_selection.center
                direction = current_selection.direction

                if current_selection.id.startswith('anchor'):
                    paintLock(mesh_builder, Color(255, 0, 255, 255), center, direction, self._arrow_head_width)
                else:
                    paintArrow(mesh_builder, arrow_color, center, direction, self._arrow_head_length, self._arrow_head_width,
                               self._arrow_tail_length, self._arrow_tail_width, not current_selection.push)
                    selection_mesh_builder = MeshBuilder()
                    paintArrow(selection_mesh_builder, ToolHandle.AllAxisSelectionColor, center, direction,
                               self._arrow_head_length, self._arrow_head_width, self._arrow_tail_length,
                               self._arrow_tail_width, not current_selection.push)
                    self.setSelectionMesh(selection_mesh_builder.build())

    def drawSavedObjectsAndCurrentSelection(self, current_selection: CurrentForce = None, plot_arrow: bool = False):
        if not self._enabled:
            mb = MeshBuilder()
            self.setSolidMesh(mb.build())
            return


        self.setEnabled(True)
        self._auto_scale = False

        if current_selection is not None:
        # if current_selection is not None and not current_selection.confirmed:
            plot_arrow = True

        anchors_dict = self._extension.getAnchors()
        forces_dict = self._extension.getForces()
        mb = MeshBuilder()
        self._addSavedObjectsToMeshBuilder(mb, anchors_dict, current_selection, Color(0, 255, 0, 255))
        self._addSavedObjectsToMeshBuilder(mb, forces_dict, current_selection, Color(255, 0, 0, 255))
        self._addCurrentSelectionToMeshBuilder(mb, current_selection, Color(0, 0, 0, 255), Color(0, 0, 255, 255),
                                               plot_arrow)

        # last, we want to add arrows etc. so that they are visible
        for k, values in anchors_dict.items():
            center = values.center
            vector = values.direction
            paintLock(mb, Color(255, 0, 255, 255), center, vector, self._arrow_head_width)

        for k, values in forces_dict.items():
            if current_selection is None or k != current_selection.id:
                center = values.center
                vector = values.direction
                pull = not values.push
                paintArrow(mb, Color(0, 0, 255, 255), center, vector, self._arrow_head_length, self._arrow_head_width,
                           self._arrow_tail_length, self._arrow_tail_width, pull)

        self.setSolidMesh(mb.build())

    def _onSelectionCenterChanged(self) -> None:
        if self._enabled:
            obj = Selection.getSelectedObject(0) # which index to use?
            if obj:
                self.setTransformation(obj.getLocalTransformation())
