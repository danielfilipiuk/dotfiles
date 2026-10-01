from UM.i18n import i18nCatalog
from UM.Application import Application
from UM.PluginRegistry import PluginRegistry
from UM.Message import Message
from UM.Scene.Selection import Selection
from UM.Logger import Logger

from cura.Stages.CuraStage import CuraStage

import os.path

from Slicedog_1.message_manager.MessageType import MessageType
from Slicedog_1.utils.cura_utils import getPrintableNodes

i18n_catalog = i18nCatalog("Slicedog_1")

class SlicedogStage(CuraStage):
    """Slicedog staged."""

    def __init__(self, extension, parent=None):
        super().__init__(parent)
        Application.getInstance().engineCreatedSignal.connect(self._engineCreated)
        Application.getInstance().activityChanged.connect(self._checkScene)
        Application.getInstance().getController().getScene().getRoot().childrenChanged.connect(self._onSceneChanged)

        self._extension = extension
        self._default_toolset = None
        self._default_fallback_tool = None
        self._previous_tool = None
        self._custom_toolset = (
            "Slicedog_1",
            "Slicedog_1_DefinitionTool",
            "Slicedog_1_OptimizationTool"
        )
        self._last_printable_node = None

    def _engineCreated(self):
        # TODO: _qml_engine is private, is there a better way?
        Application.getInstance()._qml_engine.rootContext().setContextProperty('slicedog_api', self._extension.getApiWrapper())
        Application.getInstance()._qml_engine.rootContext().setContextProperty('highlight_manager', self._extension.getHighlightManagerWrapper())
        # menu_component_path = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "stage", "SlicedogStageMenu.qml")
        main_component_path = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "stage", "SlicedogStageMain.qml")
        # test_component_path = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "stage", "test.qml")
        # self.addDisplayComponent("menu", menu_component_path)
        self.addDisplayComponent("main", main_component_path)
        # self.addDisplayComponent("test", test_component_path)

        self._default_toolset = self._getVisibleTools()
        for tool in self._default_toolset:
            if tool in self._custom_toolset:
                self._default_toolset.remove(tool)

        # Application.getInstance().getGlobalContainerStack().extruderList[0].getProperty('infill_sparse_density',
        #                                                                                 'value')
        # global_stack = Application.getInstance().getGlobalContainerStack()
        # infill_sparse_density = 20
        #
        # if not global_stack:
        #     Logger.log('e', 'Global container stack not found')
        # else:
        #     for extruder_stack in global_stack.extruderList:
        #         if 'infill_sparse_density' in extruder_stack.getAllKeys():
        #             extruder_stack.setProperty('infill_sparse_density', 'value', infill_sparse_density)
        #             Logger.log('i', f'Infill sparse density set to {infill_sparse_density} for extruder {extruder_stack.getId()}')
        #         else:
        #             Logger.log('w', f'Extruder {extruder_stack.getId()} does not contain "infill_sparse_density" settings')


        self._default_fallback_tool = Application.getInstance().getController().getFallbackTool()

        self._setToolVisibility(False)

        prefs = Application.getInstance().getPreferences()

        prefs.addPreference("slicedog/first_start", True)

        first_start = prefs.getValue("slicedog/first_start")

        if first_start:
            self._extension.getMessageManager().showMessage(
                message_type=MessageType.OPEN_SAMPLES,
                text="For the best first experience, run Slicedog on our sample model, it always works. Click on Open samples button",
                title="First-time tip"
            )
            prefs.setValue("slicedog/first_start", False)
            Application.getInstance().savePreferences()

    def onStageSelected(self):
        application = Application.getInstance()
        controller = application.getController()

        self._extension.getMessageManager().hideMessage(MessageType.SCENE_NOT_READY)
        self._extension.getHighlightManager().setEnabled(True)
        self._extension.resetImportTrack()

        Selection.clear()
        printable_node = self._exitStageIfInvalid()
        if not printable_node:
            # TODO double check (first in exitStage)
            if len(getPrintableNodes()) == 0:
                self._extension.getMessageManager().showMessage(
                    message_type=MessageType.OPEN_SAMPLES,
                    text="There's no model on the build plate. For the best first experience, use our sample part. Click on Open samples button",
                    title="No model loaded"
                )
            return

        if not Selection.hasSelection():
            Selection.add(printable_node)

        self._setToolVisibility(True)
        use_tool = self._custom_toolset[0]
        controller.setFallbackTool(use_tool)
        self._previous_tool = controller.getActiveTool()
        if self._previous_tool:
            controller.setActiveTool(use_tool)

    def onStageDeselected(self):
        application = Application.getInstance()
        controller = application.getController()

        # self._extension.getHighlightManager().setEnabled(False)
        self._extension.reset()

        self._setToolVisibility(False)
        controller.setFallbackTool(self._default_fallback_tool)
        if self._previous_tool:
            controller.setActiveTool(self._default_fallback_tool)

    def _getVisibleTools(self):
        visible_tools = []
        tools = Application.getInstance().getController().getAllTools()

        for name in tools:
            visible = True
            tool_metainfo = tools[name].getMetaData()

            if "visible" in tool_metainfo.keys():
                visible = tool_metainfo["visible"]

            if visible:
                visible_tools.append(name)

        return visible_tools

    def _setToolVisibility(self, custom_tool_visibility):
        tools = Application.getInstance().getController().getAllTools()
        for name in tools:
            tool_meta_data = tools[name].getMetaData()

            if name in self._custom_toolset:
                pass
                # tool_meta_data["visible"] = custom_tool_visibility
            elif name in self._default_toolset:
                tool_meta_data["visible"] = not custom_tool_visibility

        Application.getInstance().getController().toolsChanged.emit()

    def _sceneNotReady(self):
        app = Application.getInstance()
        if not self._extension.isImportSuccess():
            self._extension.getMessageManager().showMessage(MessageType.SCENE_NOT_READY)
            app.getController().setActiveStage("PrepareStage")
        else:
            app.getController().setActiveStage("PreviewStage")

    def _exitStageIfInvalid(self):
        current_stage = Application.getInstance().getController().getActiveStage()
        if current_stage == self:
            printable_nodes = getPrintableNodes()
            if len(printable_nodes) == 0:
                self._sceneNotReady()
                return None
            elif len(printable_nodes) > 1:
                if not self._extension.isImportSuccess():
                    if not self._extension.isImporting():
                        self._sceneNotReady()
                        return None
                else:
                    if not self._extension.isImporting():
                        self._sceneNotReady()
                        return None
            return printable_nodes[0]
        else:
            return False

    def _checkScene(self):
        active_stage = Application.getInstance().getController().getActiveStage()

        if active_stage and active_stage.getPluginId() == "Slicedog_1":
            self._exitStageIfInvalid()

    def _onSceneChanged(self, node):
        printable_node = self._exitStageIfInvalid()
        if self._last_printable_node != printable_node:
            self._last_printable_node = printable_node
            self._extension.setAnchors({})
            self._extension.setForces({})