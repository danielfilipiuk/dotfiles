import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import UM as UM
import Cura as Cura
//import Slicedog as Slicedog

Item {
    id: base
    width: childrenRect.width
    height: childrenRect.height

    readonly property string cost: "cost"
    readonly property string strength: "strength"
    readonly property string time: "time"

    readonly property string sameStrength: "same_strength"
    readonly property string bestStrength: "best_strength"

    readonly property var ticks: ["Same Strength", "Best Strength"]

    UM.I18nCatalog {
        id: catalog;
        name: "Slicedog_1"
    }

    function setOptimizationStrategy(type) {
        costButton.checked = type === cost
        strengthButton.checked = type === strength
        timeButton.checked = type === time
        slicedog_api.optimizationStrategy = type
        if (type === strength) {
            min_strength_ratio.text = "1.5"
            max_strength_ratio.text = "6"
        } else {
            min_strength_ratio.text = "1"
            max_strength_ratio.text = "4"
        }
    }

    Column {
        id: items
        anchors.top: parent.top;
        anchors.left: parent.left;

        spacing: UM.Theme.getSize("default_margin").height

        UM.Label {
            id: optimizationLabel
            height: UM.Theme.getSize("setting").height
            text: catalog.i18nc("@label", "Optimization Strategy")
        }

        Row {
            id: optimizationButtons
            spacing: UM.Theme.getSize("default_margin").width

            UM.ToolbarButton {
                id: costButton
                text: catalog.i18nc("@label", "Cost")
                toolItem: Image
                {
                    source: "../resources/icons/optimize_cost.svg"
                }
                property bool needBorder: true
                checkable: true
                onClicked: setOptimizationStrategy(cost)
                z: 3
                checked: slicedog_api.optimizationStrategy === cost
//                checked: selected_objects_manager.optimization_strategy === cost
//                checked: Slicedog.Helper.optimization_strategy === cost
            }

            UM.ToolbarButton {
                id: strengthButton
                text: catalog.i18nc("@label", "Strength")
                toolItem: Image
                {
                    source: "../resources/icons/optimize_force.svg"
                }
                property bool needBorder: true
                checkable: true
                onClicked: setOptimizationStrategy(strength)
                z: 2
                checked: slicedog_api.optimizationStrategy === strength
//                checked: selected_objects_manager.optimization_strategy === strength
//                checked: Slicedog.Helper.optimization_strategy === strength
            }

            UM.ToolbarButton {
                id: timeButton
                text: catalog.i18nc("@label", "Time")
                toolItem: Image
                {
                    source: "../resources/icons/optimize_speed.svg"
                }
                property bool needBorder: true
                checkable: true
                onClicked: setOptimizationStrategy(time)
                z: 1
                checked: slicedog_api.optimizationStrategy === time
//                checked: selected_objects_manager.optimization_strategy === time
//                checked: Slicedog.Helper.optimization_strategy === time
            }
        }

        UM.Label {
            id: strengthLabel
            height: UM.Theme.getSize("setting").height
            text: catalog.i18nc("@label", "Strength")
        }

        Slider {
            id: slider
            from: 1
            to: 4
            value: slicedog_api.optimizationSafetyRatio
//            value: selected_objects_manager.optimization_safety_ratio
            stepSize: 0.01
            width: parent.width

            onValueChanged: {
                slicedog_api.optimizationSafetyRatio = slider.value
//                selected_objects_manager.optimization_safety_ratio = slider.value
            }
        }

        RowLayout {
            id: ticksRow
            width: parent.width
            UM.Label {
                id: min_strength_ratio
                height: 20
                text: "1"
                Layout.alignment: Qt.AlignLeft
            }

            Item {
                Layout.fillWidth: true
            }

            UM.Label {
                id: max_strength_ratio
                height: 20
                text: "4"
                Layout.alignment: Qt.AlignRight
            }
        }

        UM.CheckBox
        {
            id: autoLowerSafety
            //: Snap Rotation checkbox
            text: catalog.i18nc("@action:checkbox","Auto-lower safety factor")

            checked: slicedog_api.optimizationAutoLowerSafetyRatio
            onClicked: slicedog_api.optimizationAutoLowerSafetyRatio = checked
        }

        Cura.PrimaryButton {
            id: backToDefinitionButton
            text: catalog.i18nc("action:button", "Back to definition")
            visible: true
            height: UM.Theme.getSize("setting_control").height

            onClicked: {
                UM.Controller.setActiveTool("Slicedog_1_DefinitionTool")
            }
        }

        Cura.PrimaryButton {
            id: optimizeButton
            text: catalog.i18nc("action:button", "Optimize")
            visible: true
            height: UM.Theme.getSize("setting_control").height

            onClicked: {
                slicedog_api.optimizeStl()
//                selected_objects_manager.optimize_stl()
            }
        }
    }
}