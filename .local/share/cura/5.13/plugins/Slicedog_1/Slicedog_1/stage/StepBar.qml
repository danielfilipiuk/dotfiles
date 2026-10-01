import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import UM as UM

Item {
    id: stepBar
    property int currentStep: slicedog_api.currentStep
    property real scaleFactor: 1.0
    signal stepSelected(int index)

    property Rectangle step1Dot
    property Rectangle step2Dot
    property Rectangle step3Dot
    property Rectangle step4Dot

    width: parent.width
    height: 60 * scaleFactor

    function updateConnectorLine() {
        if (!step1Dot || !step4Dot) return;

        const startX = step1Dot.mapToItem(stepBar, step1Dot.width / 2, 0).x;
        const endX = step4Dot.mapToItem(stepBar, step4Dot.width / 2, 0).x;
        const y = step1Dot.mapToItem(stepBar, 0, step1Dot.height / 2).y - connectorLine.height / 2;

        connectorLine.x = startX;
        connectorLine.width = endX - startX;
        connectorLine.y = y;
    }

    function updateProgressLine() {
        if (!step1Dot || !step4Dot) return;

        const startX = step1Dot.mapToItem(stepBar, step1Dot.width / 2, 0).x;

        const endDot = currentStep === 0 ? step1Dot :
                       currentStep === 1 ? step2Dot :
                       currentStep === 2 ? step3Dot :
                       step4Dot;

        const endX = endDot.mapToItem(stepBar, endDot.width / 2, 0).x;
        const y = step1Dot.mapToItem(stepBar, 0, step1Dot.height / 2).y - progressLine.height / 2;

        progressLine.x = startX;
        progressLine.width = endX - startX;
        progressLine.y = y;
    }

    Rectangle {
        id: connectorLine
        color: "#CCC"
        height: 2 * scaleFactor
        z: 0

        Timer {
            interval: 100
            running: true
            repeat: false
            onTriggered: updateConnectorLine()
        }
    }

    Rectangle {
        id: progressLine
        color: "#FC8938"
        height: 3 * scaleFactor
        z: 1

        Timer {
            id: progressLineTimer
            interval: 100
            running: true
            repeat: false
            onTriggered: updateProgressLine()
        }
    }

    Connections {
        target: stepBar
        function onCurrentStepChanged() {
            updateProgressLine()
        }
    }

    RowLayout {
        id: stepRow
        anchors.fill: parent
        anchors.margins: 16 * scaleFactor
        spacing: 0
        z: 1

        Repeater {
            model: 4
            delegate: Item {
                id: stepItem
                Layout.fillWidth: true
                height: stepRow.height * scaleFactor
                property double lastClickTime: 0
                property int cooldownPeriod: 3000

                Column {
                    anchors.centerIn: parent
                    spacing: 4 * scaleFactor

                    Rectangle {
                        anchors.horizontalCenter: parent.horizontalCenter
                        id: dot
                        width: 14 * scaleFactor
                        height: 14 * scaleFactor
                        radius: 7 * scaleFactor
                        color: index < currentStep ? "#FC8938" : (index === currentStep ? "#000" : "#CCC")
                        border.color: "#00000000"

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if ((slicedog_api.currentStep != 3) || (Date.now() - stepItem.lastClickTime > stepItem.cooldownPeriod)) {
                                    stepSelected(index)
                                    stepItem.lastClickTime = Date.now()
                                }
                            }
                            cursorShape: Qt.PointingHandCursor
                        }
                    }

                    Row {
                        spacing: 4 * scaleFactor
                        Text {
                            text: "Step " + (index + 1)
                            font.pixelSize: 12 * scaleFactor
                        }

                        Rectangle {
                            width: 14 * scaleFactor
                            height: 14 * scaleFactor
                            radius: 2 * scaleFactor
                            color: "#4CAF50"
                            visible: slicedog_api.stepsConfirmedFlags[index]
//                            visible: index < currentStep
                            anchors.verticalCenter: parent.verticalCenter

                            Image {
                                anchors.centerIn: parent
                                source: "../resources/icons/CheckWhite.svg"
                                width: 10 * scaleFactor
                                height: 10 * scaleFactor
                                mipmap: true
                            }
                        }
                    }
                }

                Component.onCompleted: {
                    if (index === 0) step1Dot = dot;
                    if (index === 1) step2Dot = dot;
                    if (index === 2) step3Dot = dot;
                    if (index === 3) step4Dot = dot;
                    if (step1Dot && step4Dot) updateConnectorLine();
                }
            }
        }
    }

    Timer {
        id: resizeUpdateTimer
        interval: 50
        running: false
        repeat: false
        onTriggered: {
            updateConnectorLine()
            updateProgressLine()
        }
    }

    Connections {
        target: stepBar
        function onWidthChanged() {
            updateConnectorLine()
            updateProgressLine()
            resizeUpdateTimer.restart()
        }
        function onHeightChanged() {
            updateConnectorLine()
            updateProgressLine()
            resizeUpdateTimer.restart()
        }
    }

    Component.onCompleted: updateConnectorLine()
}
