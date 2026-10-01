import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import UM as UM
import Cura as Cura

Item {
    id: panelContainer
    anchors.fill: parent
    property real scaleFactor: 1.0

    property var popupConfigs: ({
        "unhandled": {
            messageText: "Unknown or unhandled error occurred. Please try again and contact support.",
            button1Text: "OK",
            button1Color: "#FC4F38",
        },
        "stepNotDefined": {
            messageText: "Step definition not finished",
            button1Text: "OK",
            button1Color: "#FC4F38",
        },
        "serverNotReachable": {
            messageText: "Error while trying to access Slicedog server. Please try again later",
            button1Text: "OK",
            button1Color: "#FC4F38",
        },
        "userNotRegistered": {
            messageText: "User not registered, please register first",
            button1Text: "OK",
            button1Color: "#FC4F38",
        },
        "userAlreadyRegistered": {
            messageText: "User already registered",
            button1Text: "OK",
            button1Color: "#FC4F38",
        },
        "login": {
            messageText: "You are not logged in - please log in to continue",
            button1Text: "OK",
            button1Color: "#FC4F38",
        },
        "unknownErrorWhileRegistering": {
            messageText: "Something went wrong during registration. Please contact support",
            button1Text: "OK",
            button1Color: "#FC4F38",
        },
        "noConnection": {
            messageText: "Most likely the server is not running or you are not connected to the internet",
            button1Text: "OK",
            button1Color: "#FC4F38",
        },
        "trialFormUrl": {
            messageText: 'If URL is missing, check <a href="https://slicedog.com/help/common-issues/">Common Issues</a>',
            button1Text: "OK",
            button1Color: "#FC4F38",
        },
        "adminApprovalMissing": {
            messageText: 'Looks like you are not approved to use this function, check <a href="https://slicedog.com/help/common-issues/">Common Issues</a>',
            button1Text: "OK",
            button1Color: "#FC4F38",
        },

        "updateExtruderSettings": {
            messageText: "Looks like some print settings of an active extruder aren't Slicedog ready. No worries - just click on Update button and I'll change them for you and continue",
            button1Text: "Update",
            button1Color: "#FC8938",
            button1Action: function() {
                slicedog_api.updateExtruderSettings()
                slicedog_api.optimizeStl()
            },
            button2Text: "Cancel",
            button2Color: "#FC4F38",
        },
        "executionTimeLimitExceeded": {
            messageText: 'Uh-oh, I ran out of execution time. Check <a href="https://slicedog.com/help/common-issues/">Common Issues</a> to see how to fix it',
            button1Text: "OK",
            button1Color: "#FC4F38",
        },
        "registeredInfo": {
            messageText: "<b>You're almost there!</b><br>Your account has been created.<br>Please click the <b>Log In<b> button in the top-right corner to start using Slicedog.",
            button1Text: "OK",
            button1Color: "#FC4F38",
        }
    })

    Rectangle {
        id: panelDimmer
        anchors.fill: step3Root
        color: "#80000000"
        visible: genericPopup.visible
        z: 999
        radius: 6 * scaleFactor
    }

    ColumnLayout {
        id: step3Root
        anchors.fill: parent

        property real scaleFactor: panelContainer.scaleFactor
        readonly property string material: "Material"
        readonly property string strength: "Strength"
        readonly property string time: "Time"
        property bool autoLowerSafetySelected: true

        spacing: 8 * scaleFactor
        Layout.fillWidth: true
        Layout.fillHeight: true

        function getSafetyFactorText(value) {
            if (slicedog_api.optimizationStrategy === "Strength") {
                value = value * 1.5
            }
            return value.toFixed(1)
        }

        Text {
            text: "Set Optimization Goal"
            wrapMode: Text.WordWrap
            font.pixelSize: 14 * scaleFactor
            color: "#333"
        }

        Rectangle {
            color: "#F9F9F9"
            radius: 6 * scaleFactor
            border.color: "#CCC"
            Layout.fillWidth: true
            Layout.preferredHeight: 10
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16 * scaleFactor
                anchors.leftMargin: 32 * scaleFactor
                spacing: 16 * scaleFactor

                ColumnLayout {
                    spacing: 12 * scaleFactor

                    RowLayout {
                        Layout.leftMargin: - 16 * scaleFactor
                        id: infoRow

                        Item {
                            Layout.preferredWidth: 24 * scaleFactor
                            Layout.preferredHeight: 24 * scaleFactor
                            Layout.alignment: Qt.AlignTop

                            Image {
                                anchors.centerIn: parent
                                source: "../resources/icons/Information_not_interactive.svg"
                                width: 24 * scaleFactor
                                height: 24 * scaleFactor
                                fillMode: Image.PreserveAspectFit
                                mipmap: true
                            }
                        }

                        TransientInfoLabel {
                            scaleFactor: step3Root.scaleFactor
                            sourceValue: slicedog_api.lastFeedback
                            defaultText: "What do you want me to optimize for?"
                            Layout.fillWidth: true
                            wrapWidth: infoRow.width - (24 * scaleFactor) - infoRow.spacing
                        }
                    }

//                    RowLayout {
//                        Text {
//                            text: "What do you want me to fetch?"
//                            font.pixelSize: 13 * scaleFactor
//                            color: "#333"
//                        }
//
//                        Item {
//                            Layout.preferredWidth: 24 * scaleFactor
//                            Layout.preferredHeight: 24 * scaleFactor
//                            Layout.alignment: Qt.AlignTop
//
//                            Image {
//                                id: infoIconStrategy
//                                anchors.centerIn: parent
//                                source: "../resources/icons/Information.svg"
//                                width: 30 * scaleFactor
//                                height: 30 * scaleFactor
//                                fillMode: Image.PreserveAspectFit
//                                mipmap: true
//                            }
//
//                            MouseArea {
//                                anchors.fill: parent
//                                onClicked: {
//                                    if (infoPopupStrategy.visible) {
//                                        infoPopupStrategy.close()
//                                    } else {
//                                        infoPopupStrategy.x = infoIconStrategy.width
//                                        infoPopupStrategy.y = 0
//                                        infoPopupStrategy.open()
//                                    }
//                                }
//                                cursorShape: Qt.PointingHandCursor
//                            }
//
//                            Popup {
//                                id: infoPopupStrategy
//                                modal: false
//                                focus: false
//                                width: 500 * scaleFactor
//                                closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
//
//                                background: Rectangle {
//                                    color: "white"
//                                    border.color: "#ccc"
//                                    radius: 6 * scaleFactor
//                                }
//
//                                contentItem: Text {
//                                    wrapMode: Text.WordWrap
//                                    textFormat: Text.RichText
//                                    font.pixelSize: 13 * scaleFactor
//                                    color: "#000"
//                                    padding: 8 * scaleFactor
//                                    text: `
//                                        Choose what Slicedog should focus on during optimization. Each option balances material savings with your chosen goal:<br><br>
//                                        • <b>Material Optimization</b> – Saves as much material as possible while keeping the part strong where it matters.<br><br>
//                                        • <b>Strength Optimization</b> – Reinforces the part, ideal when you need extra safety or durability.<br><br>
//                                        • <b>Time Optimization</b> – Reduces print time as much as possible while keeping the part strong.
//                                    `
//                                }
//                            }
//                        }
//                    }

                    Repeater {
                        model: ["Material", "Strength", "Time"]

                        delegate: Item {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 20 * scaleFactor

                            Row {
                                spacing: 8 * scaleFactor
                                anchors.verticalCenter: parent.verticalCenter
                                anchors.left: parent.left
                                anchors.leftMargin: 4 * scaleFactor

                                Rectangle {
                                    width: 16 * scaleFactor
                                    height: 16 * scaleFactor
                                    radius: 8 * scaleFactor
                                    border.color: "#000"
                                    border.width: 1
                                    color: slicedog_api.optimizationStrategy === modelData ? "#FC8938" : "transparent"

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: slicedog_api.optimizationStrategy = modelData
                                    }
                                }

                                Text {
                                    text: modelData
                                    font.pixelSize: 13 * scaleFactor
                                    color: "#333"
                                    anchors.verticalCenter: parent.verticalCenter
                                }
                            }
                        }

                    }
                }

                ColumnLayout {
                    spacing: 12 * scaleFactor

                    RowLayout {
                        Text {
                            text: "Safety Factor"
                            font.pixelSize: 13 * scaleFactor
                            color: "#333"
                        }

                        Item {
                            Layout.preferredWidth: 24 * scaleFactor
                            Layout.preferredHeight: 24 * scaleFactor
                            Layout.alignment: Qt.AlignTop

                            Image {
                                id: infoIconSafety
                                anchors.centerIn: parent
                                source: "../resources/icons/Information.svg"
                                width: 30 * scaleFactor
                                height: 30 * scaleFactor
                                fillMode: Image.PreserveAspectFit
                                mipmap: true
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    if (infoPopupSafety.visible) {
                                        infoPopupSafety.close()
                                    } else {
                                        infoPopupSafety.x = infoIconSafety.width
                                        infoPopupSafety.y = 0
                                        infoPopupSafety.open()
                                    }
                                }
                                cursorShape: Qt.PointingHandCursor
                            }

                            Popup {
                                id: infoPopupSafety
                                width: 500 * scaleFactor
                                modal: false
                                focus: false
                                closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent

                                background: Rectangle {
                                    color: "white"
                                    border.color: "#ccc"
                                    radius: 6 * scaleFactor
                                }

                                contentItem: Text {
                                    wrapMode: Text.WordWrap
                                    textFormat: Text.RichText
                                    font.pixelSize: 13 * scaleFactor
                                    color: "#000"
                                    padding: 8 * scaleFactor
                                    text: `
                                        This is your safety margin. The higher it is, the more confident you can be that
                                        the part won’t break — even if the force is stronger than expected, or if there are
                                        imperfections from 3D printing or material quality. It’s your buffer against
                                        surprises. However, the higher the safety factor, the less material is saved.
                                    `
                                }
                            }
                        }
                    }
                }

                ColumnLayout {
                    Layout.preferredHeight: 50 * scaleFactor
                    spacing: 6 * scaleFactor
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter

                    property alias value: slider.value

                    Item {
                        Layout.preferredHeight: 16 * scaleFactor

                        Text {
                            id: currentSafetyRatioText
                            text: step3Root.getSafetyFactorText(slicedog_api.optimizationSafetyRatio)
                            x: slider.leftPadding - Math.round(width / 2)
                            font.pixelSize: 13 * scaleFactor
                        }
                    }

                    Slider {
                        id: slider
                        from: 1
                        to: 4
                        stepSize: 0.01
                        value: slicedog_api.optimizationSafetyRatio
                        Layout.preferredWidth: 240 * scaleFactor
                        Layout.preferredHeight: 36 * scaleFactor

                        onValueChanged: {
                            slicedog_api.optimizationSafetyRatio = slider.value
                        }

                        background: Rectangle {
                            radius: 2 * scaleFactor
                            height: 4 * scaleFactor
                            anchors.verticalCenter: parent.verticalCenter
                            width: parent.width
                            color: "#eee"

                            Rectangle {
                                width: slider.visualPosition * parent.width
                                height: parent.height
                                color: "#FC8938"
                                radius: 2 * scaleFactor
                            }

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                acceptedButtons: Qt.NoButton
                            }
                        }

                        handle: Rectangle {
                            width: 16 * scaleFactor
                            height: 16 * scaleFactor
                            radius: 8 * scaleFactor
                            color: "white"
                            border.color: "#555"
                            border.width: 1
                            anchors.verticalCenter: parent.verticalCenter
                            x: slider.leftPadding + slider.visualPosition * slider.availableWidth - width / 2

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                acceptedButtons: Qt.NoButton
                            }
                        }
                    }
                }

                RowLayout {

                    Text {
                        text: "Auto-lower Safety Factor"
                        font.pixelSize: 13 * scaleFactor
                        color: "#333"
                    }

                    Item {
                        Layout.preferredWidth: 24 * scaleFactor
                        Layout.preferredHeight: 24 * scaleFactor
                        Layout.alignment: Qt.AlignTop

                        Image {
                            id: infoIconAutoLower
                            anchors.centerIn: parent
                            source: "../resources/icons/Information.svg"
                            width: 30 * scaleFactor
                            height: 30 * scaleFactor
                            fillMode: Image.PreserveAspectFit
                            mipmap: true
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (infoPopupAutoLower.visible) {
                                    infoPopupAutoLower.close()
                                } else {
                                    infoPopupAutoLower.x = infoIconAutoLower.width
                                    infoPopupAutoLower.y = 0
                                    infoPopupAutoLower.open()
                                }
                            }
                            cursorShape: Qt.PointingHandCursor
                        }

                        Popup {
                            id: infoPopupAutoLower
                            width: 500 * scaleFactor
                            modal: false
                            focus: false
                            closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent

                            background: Rectangle {
                                color: "white"
                                border.color: "#ccc"
                                radius: 6 * scaleFactor
                            }

                            contentItem: Text {
                                wrapMode: Text.WordWrap
                                textFormat: Text.RichText
                                font.pixelSize: 13 * scaleFactor
                                color: "#000"
                                padding: 8 * scaleFactor
                                text: `
                                    In some situations, the original safety factor is too high and can’t be applied to
                                    the part. If this happens, enabling auto-lowering lets the optimization continue by
                                    automatically reducing the safety factor as needed.
                                `
                            }
                        }
                    }

                    Rectangle {
                        Layout.preferredWidth: 30 * scaleFactor
                        Layout.preferredHeight: 24 * scaleFactor
                        color: "transparent"
                    }

                    Switch {
                        id: autoLowerSwitch
                        checked: slicedog_api.optimizationAutoLowerSafetyRatio
                        implicitWidth: 50 * scaleFactor
                        implicitHeight: 26 * scaleFactor

                        indicator: Rectangle {
                            id: track
                            width: 50 * scaleFactor
                            height: 26 * scaleFactor
                            radius: height / 2
                            color: autoLowerSwitch.checked ? "#FC8938" : "#ccc"
                            border.color: "#444"
                            border.width: 1

                            Rectangle {
                                id: thumb
                                width: 22 * scaleFactor
                                height: 22 * scaleFactor
                                radius: height / 2
                                y: 2 * scaleFactor
                                x: autoLowerSwitch.checked ? (track.width - width - y) : y
                                color: "white"
                                border.color: "#333"
                                border.width: 1
                                Behavior on x {
                                    NumberAnimation { duration: 150; easing.type: Easing.InOutQuad }
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                acceptedButtons: Qt.NoButton
                            }
                        }

                        onCheckedChanged: {
                            slicedog_api.optimizationAutoLowerSafetyRatio = checked
                        }
                    }
                }
            }
        }

        Rectangle {
            color: "transparent"
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            Layout.fillHeight: true
        }

        Button {
            Layout.alignment: Qt.AlignHCenter
            leftPadding: 24 * scaleFactor
            rightPadding: 24 * scaleFactor
            background: Rectangle {
                color: "#FC8938"
                radius: 6

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                }
            }

            contentItem: Text {
                text: "Confirm All Steps and Start Optimization"
                color: "white"
                font.pixelSize: 13 * scaleFactor
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                anchors.fill: parent
            }

            font.pixelSize: 13 * scaleFactor
            Layout.preferredHeight: 36 * scaleFactor

            onClicked: {
                if (slicedog_api.confirmCurrentStep()) {
                    slicedog_api.optimizeStl()
    //                slicedog_api.currentStep = 3 // set by optimizeStl
                }
            }
        }

        Text {
            text: "Tip: To go back to a previous step, just click on it in the top bar"
            font.pixelSize: 13 * scaleFactor
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
        }

        Rectangle {
            color: "transparent"
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            Layout.fillHeight: true
        }

//        ModalPopup {
//            id: updateExtruderSettingsPopup
//            objectName: "updateExtruderSettings"
//            parent: step3Root
//            messageText: "Looks like some print settings of an active extruder aren't Slicedog ready. No worries - just click on Update button and I'll change them for you and continue"
//            button1Text: "Update"
//            button1Color: "#FC8938"
//            button1Action: function() {
//                slicedog_api.updateExtruderSettings()
//                slicedog_api.optimizeStl()
//            }
//            button2Text: "Cancel"
//            button2Color: "#FC4F38"
//        }

        ModalPopup {
            id: genericPopup
            popupParent: step3Root
        }

        Connections {
            target: slicedog_api
            function onPopupRequested(jsonString) {
                const payload = JSON.parse(jsonString)
                const which = payload.type
                const custom = payload.message

                if (popupConfigs[which]) {
                    const cfg = popupConfigs[which]
                    if (cfg.titleText) genericPopup.titleText = cfg.titleText
                    if (cfg.messageText) genericPopup.messageText = custom || cfg.messageText
                    if (cfg.button1Text) genericPopup.button1Text = cfg.button1Text
                    if (cfg.button1Action) genericPopup.button1Action = cfg.button1Action
                    if (cfg.button1Color) genericPopup.button1Color = cfg.button1Color
                    if (cfg.button2Text) genericPopup.button2Text = cfg.button2Text
                    if (cfg.button2Action) genericPopup.button2Action = cfg.button2Action
                    if (cfg.button2Color) genericPopup.button2Color = cfg.button2Color
                    if (cfg.showWarningIcon) genericPopup.showWarningIcon = cfg.showWarningIcon
                    genericPopup.open()
                } else {
                    console.warn("Unknown popup requested: ", which)
                }
            }
        }

//        LoginPopup {
//            id: loginPopup
//            popupParent: step3Root
//        }
//
//        UnhandledPopup {
//            id: unhandledPopup
//            popupParent: step3Root
//        }
//
//        StepNotDefinedPopup {
//            id: stepNotDefinedPopup
//            popupParent: step3Root
//        }
//
//        ServerNotReachablePopup {
//            id: serverNotReachablePopup
//            popupParent: step3Root
//        }
//
//        UserNotRegisteredPopup {
//            id: userNotRegisteredPopup
//            popupParent: step3Root
//        }
//
//        Connections {
//            target: slicedog_api
//            function onPopupRequested(which) {
//                switch (which) {
//                    case "login":
//                        loginPopup.open()
//                        break
//                    case "updateExtruderSettings":
//                        updateExtruderSettingsPopup.open()
//                        break
//                    case "unhandled":
//                        unhandledPopup.open()
//                        break
//                    case "stepNotDefined":
//                        stepNotDefinedPopup.open()
//                        break
//                    case "serverNotReachable":
//                        serverNotReachablePopup.open()
//                        break
//                    case "userNotRegistered":
//                        userNotRegisteredPopup.open()
//                        break
//                    default:
//                        console.warn("Unknown popup requested: ", which)
//                        break
//                }
//            }
//        }
    }
}