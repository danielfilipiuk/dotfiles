import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import UM as UM
import Cura as Cura

ApplicationWindow {
    id: forceDialog
    visible: false
    width: sliderWidth
    height: maxHeight
    minimumWidth: Math.round(sliderWidth * 1.1)
    minimumHeight: Math.round(maxHeight * 1.1)
    color: "white"
    flags: Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool
    modality: Qt.NonModal // Ensures non-blocking behavior

    transientParent: parent

    readonly property var tickIcons: ["None.svg", "Light.svg", "Medium.svg", "Strong.svg", "UltraStrong.svg"]
    readonly property var tickPositions: [0.0, 0.25, 0.5, 0.75, 1.0]
    readonly property int tickWidth: Math.round(sliderWidth / 15)
    // TODO update if more rows added
    readonly property int sliderWidth: 400
    readonly property int maxHeight: 200
    readonly property int spacingMargin: Math.round(maxHeight / 20)
    readonly property string moveForce: "move_force"
    readonly property string rotateForce: "rotate_force"
    readonly property string switchForce: "switch_force"

    function setForceOtherOption(type) {
        moveForce.checked = type === moveForce
        rotateForce.checked = type === rotateForce
    }

    onClosing: {
        // TODO confirm that this is enough
        slicedog_api.currentForceFaces = [[]]
        highlight_manager.drawSavedObjectsAndCurrentSelection(slicedog_api.currentForceAsDict, false)
        UM.Controller.setActiveTool("Slicedog_1_DefinitionTool")
    }

    Rectangle {
        id: titleBar
        width: parent.width
        height: maxHeight / 10
        color: "lightgray"

        // Drag Area
        MouseArea {
            id: dragArea
            anchors.fill: parent
            property variant clickPos: "1,1"

            onPressed: {
                clickPos  = Qt.point(mouse.x,mouse.y)
            }

            onPositionChanged: {
                var delta = Qt.point(mouse.x-clickPos.x, mouse.y-clickPos.y)
                forceDialog.x += delta.x;
                forceDialog.y += delta.y;
            }
        }

        RoundButton {
            id: closeButton
            text: "X"
            height: maxHeight / 10
            width: maxHeight / 10
            radius: maxHeight / 20
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            hoverEnabled: true
            background: Rectangle {
                radius: closeButton.radius
                color: closeButton.hovered ? "red" : "transparent"
            }


            onClicked: {
                forceDialog.close()
            }
        }
    }

    Item {
        id: baseGrid
        visible: true
        anchors.leftMargin: UM.Theme.getSize("default_margin").width
        anchors.top: titleBar.bottom
        anchors.topMargin: spacingMargin
        anchors.horizontalCenter: parent.horizontalCenter

        Button {
            id: switchButton
            text: textPrefix + dynamicLoader.nextOption
            anchors.horizontalCenter: parent.horizontalCenter

            readonly property string textPrefix: "Switch to "

            onClicked: {
                if (dynamicLoader.currentOption === dynamicLoader.defaultOption) {
                    dynamicLoader.currentOption = dynamicLoader.preciseOption
                    dynamicLoader.nextOption = dynamicLoader.defaultOption
                    dynamicLoader.sourceComponent = preciseForceComponent
                } else {
                    dynamicLoader.currentOption = dynamicLoader.defaultOption
                    dynamicLoader.nextOption = dynamicLoader.preciseOption
                    dynamicLoader.sourceComponent = defaultForceComponent
                }
                text = textPrefix + " " + dynamicLoader.nextOption
            }
        }

        Row {
            id: forceOtherDefinition
            spacing: spacingMargin
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: switchButton.bottom
            anchors.topMargin: spacingMargin

//            UM.ToolbarButton {
//                id: moveForce
//                text: "Move"
//                toolItem: Image
//                {
//                    source: UM.Theme.getIcon("ArrowFourWay")
//                }
//                property bool needBorder: true
//                checkable: true
//                onClicked: {
//                    setForceOtherOption(moveForce)
//                    UM.Controller.setActiveTool("Slicedog_MoveForceTool")
//                }
//                checked: false
//            }

            UM.ToolbarButton {
                id: rotateForce
                text: "Rotate"
                toolItem: Image
                {
                    source: UM.Theme.getIcon("Rotate")
                }
                property bool needBorder: true
                checkable: true
                onClicked: {
                    setForceOtherOption(rotateForce)
                    UM.Controller.setActiveTool("Slicedog_1_RotateForceTool")
                }
                checked: false
            }

            UM.ToolbarButton {
                id: switchDirectionForce
                text: "Switch Direction"
                toolItem: Image
                {
                    id: imageItem
                    source: switchDirectionForce.iconSource
                }
                property bool needBorder: true

                property string iconSource: pushIcon
                readonly property string pushIcon: "../resources/icons/Push.svg"
                readonly property string pullIcon: "../resources/icons/Pull.svg"
                property bool pushDirection: true
                onClicked: {
                    setForceOtherOption(switchForce)
                    pushDirection = !pushDirection
                    if (pushDirection) {
                        iconSource = pushIcon
                    } else {
                        iconSource = pullIcon
                    }
                    slicedog_api.currentForcePush = pushDirection
                    highlight_manager.drawSavedObjectsAndCurrentSelection(slicedog_api.currentForceAsDict, true)
                }
            }
        }

        Loader {
            id: dynamicLoader
            sourceComponent: defaultForceComponent
            anchors.horizontalCenter: forceOtherDefinition.horizontalCenter
            anchors.top: forceOtherDefinition.bottom
            anchors.topMargin: spacingMargin

            readonly property string defaultOption: "Default"
            readonly property string preciseOption: "Precise Force"
            property string currentOption: defaultOption
            property string nextOption: preciseOption
        }

        Button {
            id: confirmButton
            text: "Confirm"
            anchors.horizontalCenter: dynamicLoader.horizontalCenter
            anchors.top: dynamicLoader.bottom
            anchors.topMargin: spacingMargin

            property string force_type: 'push'
            property real force_value: -1
            property string force_unit: ''

            onClicked: {
                if (dynamicLoader.currentOption === dynamicLoader.defaultOption) {
                    force_value = dynamicLoader.item.value
                    force_unit = '%'
                } else {
                    force_value = dynamicLoader.item.value
                    force_unit = 'N'
                }

                slicedog_api.currentForceUnit = force_unit
                slicedog_api.currentForceMagnitude = force_value

                if (force_value >= 0) {
                    slicedog_api.updateForces(slicedog_api.currentForceAsDict)
                }

                forceDialog.close()
            }
        }
    }

    Component {
        id: defaultForceComponent
        Item {
            id: defaultComponentBaseItem
            height: slider.height + ticksItem.height + spacingMargin
            property alias value: slider.value
            Slider {
                id: slider
                from: 0
                to: 100
                value: 50
                stepSize: 0.1
                width: sliderWidth
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Item {
                id: ticksItem
                width: slider.width
                height: tickWidth
                anchors.horizontalCenter: slider.horizontalCenter
                anchors.top: slider.bottom
                anchors.topMargin: spacingMargin

                Repeater {
                    model: tickIcons.length
                    delegate: Image {
                        source: "../resources/icons/" + forceDialog.tickIcons[index]
                        width: tickWidth
                        height: tickWidth
                        anchors.verticalCenter: parent.verticalCenter
                        x: parent.width * tickPositions[index] - width / 2
                    }
                }
            }
        }
    }

    Component {
        id: preciseForceComponent
        Row {
            spacing: spacingMargin
            property real value: -1

            UM.Label {
                id: forceLabel
                height: tickWidth
                text: "Force:"
            }

            TextField {
                id: numberField
                placeholderText: "Force"
                width: Math.round(sliderWidth / 3)
                height: tickWidth
                validator: RegularExpressionValidator{
                    regularExpression: /^[0-9./]+$/
                }

                onEditingFinished: {
                    value = parseFloat(text)
                }
            }

            UM.Label {
                id: unitLabel
                height: tickWidth
                text: "[N]"
            }
        }
    }
}
