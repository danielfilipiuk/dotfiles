from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("Slicedog_1")

from .stage import SlicedogStage
from .slicedog_dummy_tool import SlicedogDummyTool
from .definition_tool import DefinitionTool
from .optimization_tool import OptimizationTool
from .move_force_tool import MoveForceTool
from .rotate_force_tool import RotateForceTool
from .extension import SlicedogExtension
#
extension = SlicedogExtension.SlicedogExtension()
slicedog_dummy_tool = SlicedogDummyTool.SlicedogDummyTool(extension)
slicedog_dummy_tool._name = ""
definition_tool = DefinitionTool.DefinitionTool(extension)
definition_tool._name = "DefinitionTool"
optimization_tool = OptimizationTool.OptimizationTool(extension)
optimization_tool._name = "OptimizationTool"
move_force_tool = MoveForceTool.MoveForceTool(extension)
move_force_tool._name = "MoveForceTool"
rotate_force_tool = RotateForceTool.RotateForceTool(extension)
rotate_force_tool._name = "RotateForceTool"

def getMetaData():
    return {
        "stage": {
            "name": i18n_catalog.i18nc("@item:inmenu", "Slicedog\u00AE"),
            "weight": 11
        },
        "tool": [
            {
                "name": i18n_catalog.i18nc("@label", "Slicedog Definition"),
                "description": "TBD",
                # "icon": "resources/icons/Definition.svg", # add icon
                # "tool_panel": "definition_tool/DefinitionTool.qml",
                "weight": 10,
                "visible": False
            },
            {
                "name": i18n_catalog.i18nc("@label", "Slicedog Optimization"),
                "description": "TBD",
                # "icon": "resources/icons/Optimization.svg", #add icon
                # "tool_panel": "optimization_tool/OptimizationTool.qml",
                "weight": 20,
                "visible": False
            },
            {
                "name": i18n_catalog.i18nc("@label", "Slicedog Move Force Tool"),
                "description": "TBD",
                "weight": 30,
                "visible": False
            },
            {
                "name": i18n_catalog.i18nc("@label", "Slicedog Rotate Force Tool"),
                "description": "TBD",
                "weight": 30,
                "visible": False
            }
        ]
    }

def register(app):
    return {
        "extension": extension,
        "stage": SlicedogStage.SlicedogStage(extension),
        "tool": [
            slicedog_dummy_tool,
            definition_tool,
            optimization_tool,
            move_force_tool,
            rotate_force_tool,
        ]
    }
