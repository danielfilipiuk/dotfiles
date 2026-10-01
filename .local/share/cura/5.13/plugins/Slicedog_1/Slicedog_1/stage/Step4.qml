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
        "registeredInfo": {
            messageText: "<b>You're almost there!</b><br>Your account has been created.<br>Please click the <b>Log In<b> button in the top-right corner to start using Slicedog.",
            button1Text: "OK",
            button1Color: "#FC4F38",
        }
    })

    Rectangle {
        id: panelDimmer
        anchors.fill: step4Root
        color: "#80000000"
        visible: confirmCancelPopup.visible | confirmUseCurrentResultPopup.visible | genericPopup.visible
        z: 999
        radius: 6 * scaleFactor
    }

    ColumnLayout {
        id: step4Root
        anchors.fill: parent

        spacing: 8
        Layout.fillWidth: true
        Layout.fillHeight: true

        Text {
            text: "Optimization Status"
            wrapMode: Text.WordWrap
            font.pixelSize: 14 * scaleFactor
            color: "#333"
        }

        StepBarVertical {
            id: stepBar
            currentStep: slicedog_api.lastFeedbackStatusIndex
            scaleFactor: panelContainer.scaleFactor
            Layout.alignment: Qt.AlignLeft
            Layout.fillHeight: true
            Layout.preferredHeight: 240 * scaleFactor
            Layout.fillWidth: true
        }

        Rectangle {
            color: "transparent"
            Layout.fillWidth: true
            Layout.preferredHeight: 0.5
            Layout.fillHeight: true
        }

        RowLayout {
            id: actionsRow
            spacing: 8 * scaleFactor
            Layout.leftMargin: 8 * scaleFactor
            Layout.rightMargin: 8 * scaleFactor
            Layout.fillWidth: true

            Rectangle {
                color: "transparent"
                Layout.fillWidth: true
                Layout.preferredHeight: 36 * scaleFactor
                Layout.preferredWidth: 0.5
                visible: !useCurrentResultBtn.visible
            }

            Button {
                Layout.preferredHeight: 36 * scaleFactor
                Layout.preferredWidth: 1
                Layout.fillWidth: true
                visible: stepBar.currentStep > 0
                background: Rectangle {
                    color: "#FC4F38"
                    radius: 6 * scaleFactor

                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                    }
                }

                contentItem: Text {
                    text: "Cancel"
                    color: "white"
                    font.pixelSize: 13 * scaleFactor
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    anchors.fill: parent
                }

                onClicked: confirmCancelPopup.open()
            }

            Rectangle {
                color: "transparent"
                Layout.fillWidth: true
                Layout.preferredHeight: 36 * scaleFactor
                Layout.preferredWidth: 0.5
                visible: !useCurrentResultBtn.visible
            }

            Button {
                id: useCurrentResultBtn
                Layout.preferredHeight: 36 * scaleFactor
                Layout.preferredWidth: 1
                Layout.fillWidth: true
                visible: stepBar.currentStep === 3
                background: Rectangle {
                    color: "#FC8938"
                    radius: 6 * scaleFactor

                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                    }
                }

                contentItem: Text {
                    text: "Use current result"
                    color: "white"
                    font.pixelSize: 13 * scaleFactor
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    anchors.fill: parent
                }

                onClicked: confirmUseCurrentResultPopup.open()
            }
        }

        Rectangle {
            color: "transparent"
            Layout.fillWidth: true
            Layout.preferredHeight: 0.5
            Layout.fillHeight: true
        }

//        LoginPopup {
//            id: loginPopup
//            popupParent: step4Root
//        }
//
//        UnhandledPopup {
//            id: unhandledPopup
//            popupParent: step4Root
//        }

        ModalPopup {
            id: confirmUseCurrentResultPopup
            popupParent: step4Root
            messageText: "Apply the current result to Cura now, or strengthen it first (5 more optimization rounds) without increasing material?"
            button1Text: "Finish and apply now"
            button1Color: "#FC8938"
            button1Action: function() {
                slicedog_api.cancelOptimization("RETURN_LAST_RESULT")
            }
            button2Text: "Strengthen, then apply"
            button2Color: "#FC8938"
            button2Action: function() {
                slicedog_api.cancelOptimization("OPTIMIZE_LAST_RESULT")
            }
        }

        ModalPopup {
            id: confirmCancelPopup
            popupParent: step4Root
            showWarningIcon: true
            titleText: "Do you wish to cancel?"
            messageText: "Cancelling current operation will lose all progress"
            button1Text: "Yes, Cancel"
            button1Color: "#FC4F38"
            button1Action: function() {
                slicedog_api.cancelOptimization("KILL")
            }
            button2Text: "No"
            button2Color: "#FC8938"
        }

        ModalPopup {
            id: genericPopup
            popupParent: step4Root
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

//        StepNotDefinedPopup {
//            id: stepNotDefinedPopup
//            popupParent: step4Root
//        }
//
//        ServerNotReachablePopup {
//            id: serverNotReachablePopup
//            popupParent: step4Root
//        }
//
//        UserNotRegisteredPopup {
//            id: userNotRegisteredPopup
//            popupParent: step4Root
//        }
//
//        Connections {
//            target: slicedog_api
//            function onPopupRequested(which) {
//                switch (which) {
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