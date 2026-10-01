from UM.Tool import Tool
from UM.Application import Application

class SlicedogDummyTool(Tool):
    """
    Dummy tool to get rid of 'ERROR - [MainThread] UM.Controller.getTool [263]: Unable to find Slicedog in tools'
    """
    def __init__(self, extension):
        super().__init__()
        self._extension = extension
        self._controller.activeToolChanged.connect(self._onActiveStateChanged)

    def _onActiveStateChanged(self):
        controller = Application.getInstance().getController()
        active_tool = controller.getActiveTool()
        if active_tool == self:
            if self._extension.getRotationActive():
                controller.setActiveTool('Slicedog_1_RotateForceTool')
            else:
                controller.setActiveTool('Slicedog_1_DefinitionTool')