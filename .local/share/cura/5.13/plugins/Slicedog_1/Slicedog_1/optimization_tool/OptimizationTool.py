from UM.i18n import i18nCatalog
from UM.Tool import Tool
from UM.Application import Application
from UM.Scene.Selection import Selection

from Slicedog_1.extension.SlicedogExtension import CurrentForce

i18n_catalog = i18nCatalog("Slicedog_1")

class OptimizationTool(Tool):
    def __init__(self, extension):
        super().__init__()

        self._extension = extension
        self._controller.activeToolChanged.connect(self._onActiveStateChanged)

    def _onActiveStateChanged(self):
        controller = Application.getInstance().getController()
        active_tool = controller.getActiveTool()
        if active_tool == self:
            # optimization tool only allowed if both anchors and forces have at least one element
            if (len(self._extension.getAnchorsAsList()) == 0 or
                    len(self._extension.getForcesAsList()) == 0):
                controller.setActiveTool(controller.getFallbackTool())
                return
            Selection.clearFace()
            self._extension.setCurrentForce(CurrentForce())
            self._extension.getHighlightManager().drawSavedObjectsAndCurrentSelection()
            Selection.setFaceSelectMode(True)
