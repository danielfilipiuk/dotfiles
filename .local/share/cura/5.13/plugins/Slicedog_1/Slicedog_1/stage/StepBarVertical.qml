import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import UM as UM

Item {
    id: stepBar
    property int currentStep: slicedog_api.lastFeedbackStatusIndex
//    property int currentStep: slicedog_api.currentStep
    property real scaleFactor: 1.0
    signal stepSelected(int index)

    property Item step1Dot
    property Item step2Dot
    property Item step3Dot
    property Item step4Dot
//    property Rectangle step1Dot
//    property Rectangle step2Dot
//    property Rectangle step3Dot
//    property Rectangle step4Dot

    property var steps: ["Preparing task", "Model analysis", "Optimization feasibility", "Optimization progress"]

//    implicitWidth: 260 * scaleFactor
//    implicitHeight: stepRow.implicitHeight

    readonly property real indicatorSize: 16 * scaleFactor
    readonly property real checkOvershoot: 0.4 * indicatorSize

    FontMetrics { id: titleFm;  font.pixelSize: 13 * scaleFactor }
    FontMetrics { id: detailFm; font.pixelSize: 13 * scaleFactor }

    function updateConnectorLine() {
        if (!step1Dot || !step4Dot) return;

        const startY = step1Dot.mapToItem(stepBar, 0, step1Dot.height / 2).y;
        const endY = step4Dot.mapToItem(stepBar, 0, step4Dot.height / 2).y;
        const x = step1Dot.mapToItem(stepBar, step1Dot.width / 2, 0).x - connectorLine.width / 2;

        connectorLine.y = startY;
        connectorLine.height = endY - startY;
        connectorLine.x = x;
    }

//    function updateProgressLine() {
//        if (!step1Dot || !step4Dot) return;
//
//        const startY = step1Dot.mapToItem(stepBar, 0, step1Dot.height / 2).y;
//
//        const endDot = currentStep === 0 ? step1Dot :
//                       currentStep === 1 ? step2Dot :
//                       currentStep === 2 ? step3Dot :
//                       step4Dot;
//
//        const endY = endDot.mapToItem(stepBar, 0, endDot.height / 2).y;
//        const x = step1Dot.mapToItem(stepBar, step1Dot.width / 2, 0).x - progressLine.width / 2;
//
//        progressLine.y = startY;
//        progressLine.height = endY - startY;
//        progressLine.x = x;
//    }

    Rectangle {
        id: connectorLine
        color: "#000"
        width: 2 * scaleFactor
        z: 0

        Timer {
            interval: 100
            running: true
            repeat: false
            onTriggered: updateConnectorLine()
        }
    }

//    Rectangle {
//        id: progressLine
//        color: "#FC8938"
//        width: 3 * scaleFactor
//        z: 1
//
//        Timer {
//            id: progressLineTimer
//            interval: 100
//            running: true
//            repeat: false
//            onTriggered: updateProgressLine()
//        }
//    }

//    Connections {
//        target: stepBar
//        function onCurrentStepChanged() {
//            console.log(stepBar.currentStep)
//            resizeUpdateTimer.restart()
//        }
//    }

    ColumnLayout {
        id: stepRow
        anchors.fill: parent
        anchors.margins: 16 * scaleFactor
        spacing: 4 * scaleFactor
        width: parent.width
        z: 1

        Repeater {
            model: steps.length
            delegate: Item {
                id: stepItem
//                Layout.fillHeight: true
//                implicitHeight: Math.max(stepBar.indicatorSize, title.implicitHeight + detail.implicitHeight)// * scaleFactor
                implicitHeight: Math.max(indicatorSize, titleFm.height + detailFm.height * detail.maximumLineCount + 2 * scaleFactor)
//                width: stepRow.width// * scaleFactor
                width: parent.width
                property double lastClickTime: 0
                property int cooldownPeriod: 3000
                onImplicitHeightChanged: {
                    updateConnectorLine()
                    resizeUpdateTimer.restart()
                }

                Row {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8 * scaleFactor
                    width: stepBar.width

                    // fixed gutter so all indicators share the same X
                    Item {
                        id: gutterCell
                        width: stepBar.indicatorSize + stepBar.checkOvershoot
                        height: width
//                        anchors.verticalCenter: parent.verticalCenter

                        // ring (white fill, black border) – shown for done + future
                        Rectangle {
                            id: ring
                            anchors.fill: parent
//                            anchors.left: parent.left
//                            anchors.verticalCenter: parent.verticalCenter
                            radius: width / 2
                            color: "white"
                            border.width: 2 * scaleFactor
                            border.color: "black"
                            visible: index !== currentStep
                        }

                        // current step: show your spinner instead of the ring
                        Loader {
//                            anchors.fill: parent
                            anchors.left: ring.left
                            anchors.verticalCenter: ring.verticalCenter
                            width: ring.width
                            height: ring.height
                            active: index === currentStep
                            sourceComponent: LoadingSpinner {
                                size: stepBar.indicatorSize
                                anchors.fill: parent
                            }
                        }

                        Canvas {
                            id: check
                            anchors.left: ring.left
                            anchors.verticalCenter: ring.verticalCenter
                            width: ring.width + stepBar.checkOvershoot  // room to overshoot
                            height: ring.height
                            visible: index < currentStep
                            antialiasing: true
                            onPaint: {
                                const ctx = getContext("2d");
                                const r  = ring.width/2;
                                const cx = r, cy = height/2;
                                ctx.clearRect(0,0,width,height);
                                ctx.lineWidth  = Math.max(2, Math.round(height/5));
                                ctx.lineCap    = "round";
                                ctx.strokeStyle = "black";
                                ctx.beginPath();
                                // start inside circle, end outside (~40% radius past edge)
                                ctx.moveTo(cx - 0.45*r, cy - 0.05*r);
                                ctx.lineTo(cx - 0.10*r, cy + 0.30*r);
                                ctx.lineTo(cx + 0.95*r, cy - 0.60*r); // overshoots to the right
                                ctx.stroke();
                            }
                        }

                        // done steps: checkmark inside the ring
//                        Text {
//                            anchors.centerIn: parent
//                            visible: index < currentStep
//                            text: "\u2713"                         // ✓
//                            font.pixelSize: 12 * scaleFactor
//                            color: "black"
//                        }
                    }

                    Column {
                        id: labels
                        width: stepBar.width - gutterCell.width - parent.spacing
                        height: stepItem.height
                        clip: true

                        Text {
                            id: title
                            text: index < steps.length - 1 ? steps[index] : steps[index] + " " + slicedog_api.currentIterationInfo
                            font.pixelSize: titleFm.font.pixelSize
                            font.bold: true
                            width: parent.width - 8 * scaleFactor
                            wrapMode: Text.WordWrap
                            maximumLineCount: 1
                            elide: Text.ElideRight
                        }

                        Text {
                            id: detail
                            text: {
                                if (index === 3) {
                                    if (index <= currentStep) {
                                        return slicedog_api.lastIterationFeedback
                                    } else {
                                        return ""
                                    }
                                } else {
                                    if (index < currentStep) {
                                        return "Done"
                                    } else if (index === currentStep) {
                                        return slicedog_api.lastStatusFeedback
                                    } else {
                                        return ""
                                    }
                                }
                            }
//                            text: index < currentStep ? "Done" : (index === currentStep ? slicedog_api.lastFeedback : "")
                            width: parent.width - 8 * scaleFactor
                            wrapMode: Text.WordWrap
                            font.pixelSize: detailFm.font.pixelSize
                            maximumLineCount: {
                                switch (index) {
                                    case 0: return 2
                                    case 1: return 3
                                    case 2: return 4
                                    case 3: return 8
                                    default: return 4 // fallback
                                }
                            }
                            elide: Text.ElideRight
                        }
                    }
                }

//                Row {
//                    anchors.left: parent.left
//                    anchors.verticalCenter: parent.verticalCenter
////                    anchors.centerIn: parent
//                    spacing: 4 * scaleFactor
//
//                    Rectangle {
////                        anchors.horizontalCenter: parent.horizontalCenter
//                        id: dot
//                        width: 14 * scaleFactor
//                        height: 14 * scaleFactor
//                        radius: 7 * scaleFactor
//                        color: index < currentStep ? "#FC8938" : (index === currentStep ? "#000" : "#CCC")
//                        border.color: "#00000000"
//
//                        MouseArea {
//                            anchors.fill: parent
//                            onClicked: {
//                                console.log(currentStep)
//                                if ((currentStep != 3) || (Date.now() - stepItem.lastClickTime > stepItem.cooldownPeriod)) {
//                                    stepSelected(index)
//                                    stepItem.lastClickTime = Date.now()
//                                }
//                            }
//                            cursorShape: Qt.PointingHandCursor
//                        }
//                    }
//
//                    Text {
//                        text: steps[index]
//                        font.pixelSize: 12 * scaleFactor
//                    }
//
////                    Column {
////                        spacing: 4 * scaleFactor
////                        Text {
////                            text: steps[index]
////                            font.pixelSize: 12 * scaleFactor
////                        }
////
////                        Rectangle {
////                            width: 14 * scaleFactor
////                            height: 14 * scaleFactor
////                            radius: 2 * scaleFactor
////                            color: "#4CAF50"
////                            visible: slicedog_api.stepsConfirmedFlags[index]
//////                            visible: index < currentStep
////                            anchors.horizontalCenter: parent.horizontalCenter
////
////                            Image {
////                                anchors.centerIn: parent
////                                source: "../resources/icons/CheckWhite.svg"
////                                width: 10 * scaleFactor
////                                height: 10 * scaleFactor
////                                mipmap: true
////                            }
////                        }
////                    }
//                }

                Component.onCompleted: {
                    if (index === 0) step1Dot = ring;
                    if (index === 1) step2Dot = ring;
                    if (index === 2) step3Dot = ring;
                    if (index === 3) step4Dot = ring;
//                    if (index === 0) step1Dot = dot;
//                    if (index === 1) step2Dot = dot;
//                    if (index === 2) step3Dot = dot;
//                    if (index === 3) step4Dot = dot;
                    if (step1Dot && step4Dot) updateConnectorLine();
                }
            }
        }

        RowLayout {
            Item {
                Layout.preferredWidth: 24 * scaleFactor
                Layout.preferredHeight: 24 * scaleFactor
                Layout.alignment: Qt.AlignTop

                Image {
                    id: infoIconStrategy
                    anchors.centerIn: parent
                    source: "../resources/icons/Information_not_interactive.svg"
                    width: 24 * scaleFactor
                    height: 24 * scaleFactor
                    fillMode: Image.PreserveAspectFit
                    mipmap: true
                }
            }

            TransientInfoLabel {
                defaultText: "Optimization is running"
                sourceValue: slicedog_api.lastFeedback === "" ? defaultText : slicedog_api.lastFeedback
                autoHide: false
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
//            updateProgressLine()
        }
    }

    Connections {
        target: stepBar
        function onWidthChanged() {
            updateConnectorLine()
//            updateProgressLine()
            resizeUpdateTimer.restart()
        }
        function onHeightChanged() {
            updateConnectorLine()
//            updateProgressLine()
            resizeUpdateTimer.restart()
        }
        function onCurrentStepChanged() {
            updateConnectorLine()
            resizeUpdateTimer.restart()
        }
    }

    Component.onCompleted: {
        updateConnectorLine()
    }
}
