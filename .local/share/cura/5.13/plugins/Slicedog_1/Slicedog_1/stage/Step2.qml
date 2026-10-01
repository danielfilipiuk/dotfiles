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
        anchors.fill: step2Root
        color: "#80000000"
        visible: genericPopup.visible
        z: 999
        radius: 6 * scaleFactor
    }

    ColumnLayout {
        id: step2Root
        anchors.fill: parent

        spacing: 8 * scaleFactor

        Layout.fillWidth: true
        Layout.fillHeight: true

        Text {
            text: "Define All Fixed Points of the Part"
            wrapMode: Text.WordWrap
            font.pixelSize: 14 * scaleFactor
            color: "#333"
        }

        Rectangle {
            color: "#F9F9F9"
            radius: 6 * scaleFactor
            border.color: "#CCC"
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            Layout.fillHeight: true

            Item {
                anchors.fill: parent
                anchors.margins: 6 * scaleFactor
                anchors.rightMargin: 0

                Flickable {
                    id: chipFlickable
                    anchors.fill: parent
                    clip: true
                    interactive: false
                    flickableDirection: Flickable.VerticalFlick
                    contentWidth: fixedPointsFlow.width
                    contentHeight: fixedPointsFlow.height
                    boundsBehavior: Flickable.StopAtBounds

                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AlwaysOn
                    }

                    Flow {
                        id: fixedPointsFlow
                        width: chipFlickable.width - 6 * scaleFactor
                        spacing: 8 * scaleFactor

                        Repeater {
                            model: slicedog_api.anchorsAsList

                            delegate: Column {
                                spacing: 2 * scaleFactor

                                Rectangle {
                                    id: chip
                                    height: 18 * scaleFactor
                                    radius: 6 * scaleFactor
                                    color: "#eeeeee"
                                    border.color: "transparent"
    //                                border.color: slicedog_api.currentForceId === modelData.id ? "#f87c1b" : "transparent"
                                    border.width: 1
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    width: fixedPointsText.implicitWidth + 30 * scaleFactor

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 6 * scaleFactor
                                        anchors.rightMargin: 6 * scaleFactor

                                        Text {
                                            id: fixedPointsText
                                            text: modelData.id
                                            font.pixelSize: 13 * scaleFactor
                                            font.bold: true
                                        }

                                        Rectangle {
                                            id: checkIcon
                                            Layout.preferredWidth: 14 * scaleFactor
                                            Layout.preferredHeight: 14 * scaleFactor
                                            radius: 2 * scaleFactor
                                            color: "#4CAF50"
                                            opacity: modelData.confirmed ? 1 : 0

                                            Image {
                                                anchors.centerIn: parent
                                                source: "../resources/icons/CheckWhite.svg"
                                                width: 10 * scaleFactor
                                                height: 10 * scaleFactor
                                                mipmap: true
                                            }
                                        }
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: slicedog_api.selectAnchor(modelData.id)
                                    }
                                }

                                Rectangle {
                                    width: chip.width
                                    height: 2 * scaleFactor
                                    color: slicedog_api.currentForceId === modelData.id ? "#FC8938" : "transparent"
                                }
                            }
                        }

                        Column {
                            spacing: 2 * scaleFactor
                            visible: slicedog_api.allAnchorsConfirmed

                            Rectangle {
                                id: addFixedPointButton
                                height: 18 * scaleFactor
                                radius: 6 * scaleFactor
                                color: "#FC8938"
                                border.color: "transparent"
                                border.width: 1

                                width: addfixedPointsText.implicitWidth + 12 * scaleFactor

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 6 * scaleFactor
                                    anchors.rightMargin: 6 * scaleFactor

                                    Text {
                                        id: addfixedPointsText
                                        text: "+ Add New Fixed Point"
                                        font.pixelSize: 13 * scaleFactor
                                        color: "white"
                                        font.bold: true
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: {
                                        slicedog_api.resetCurrentForce()
                                        slicedog_api.updateAnchorsWithCurrent()
    //                                    slicedog_api.updateAnchors(slicedog_api.currentForceAsDict)
                                    }
                                }
                            }

                            Rectangle {
                                width: addFixedPointButton.width
                                height: 2 * scaleFactor
                                color: "transparent"
                            }
                        }
                    }
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

//                MouseArea {
//                    anchors.fill: parent
//                    onClicked: {
//                        if (infoPopupStrategy.visible) {
//                            infoPopupStrategy.close()
//                        } else {
//                            infoPopupStrategy.x = infoIconStrategy.width
//                            infoPopupStrategy.y = 0
//                            infoPopupStrategy.open()
//                        }
//                    }
//                    cursorShape: Qt.PointingHandCursor
//                }
//
//                Popup {
//                    id: infoPopupStrategy
//                    modal: false
//                    focus: false
//                    width: 500 * scaleFactor
//                    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
//
//                    background: Rectangle {
//                        color: "white"
//                        border.color: "#ccc"
//                        radius: 6 * scaleFactor
//                    }
//
//                    contentItem: Text {
//                        wrapMode: Text.WordWrap
//                        textFormat: Text.RichText
//                        font.pixelSize: 13 * scaleFactor
//                        color: "#000"
//                        padding: 8 * scaleFactor
//                        text: "TODO"
//                    }
//                }
            }

            TransientInfoLabel {
                sourceValue: slicedog_api.lastFeedback
                defaultText: "Click on “Add New Fixed Point” to start"
            }

//            Text {
//                text: "Click on “Add New Fixed Point” to start"
//                font.pixelSize: 13 * scaleFactor
//                color: "#333"
//            }
        }

//        Text {
//            text: "Click on “Add New Fixed Point” to start"
//            font.pixelSize: 14 * scaleFactor
//            color: "#888"
//        }

        Rectangle {
            color: "#F9F9F9"
            radius: 6 * scaleFactor
            border.color: "#CCC"
            Layout.fillWidth: true
            Layout.preferredHeight: 5
            Layout.fillHeight: true

            Loader {
                id: fixedPointDetailLoader
                anchors.fill: parent
                opacity: slicedog_api.currentForceId === '' ? 0 : 1
                sourceComponent: createFixedPointComponent
            }
        }

        Button {
            id: confirmAllFixedPointsButton
            Layout.alignment: Qt.AlignHCenter
            leftPadding: 24 * scaleFactor
            rightPadding: 24 * scaleFactor
            opacity: slicedog_api.anchorsAsList.length > 0 ? 1 : 0
            background: Rectangle {
                color: slicedog_api.allAnchorsConfirmed ? "#FC8938" : "#C0C1C2"
                radius: 6

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: confirmAllFixedPointsButton.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                }
            }

            contentItem: Text {
                text: "Confirm All Fixed Points to Move to Step 3"
                color: "white"
                font.pixelSize: 13 * scaleFactor
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                anchors.fill: parent
            }

            font.pixelSize: 12 * scaleFactor
            Layout.preferredHeight: 36 * scaleFactor

            onClicked: {
                if (slicedog_api.confirmCurrentStep()) {
                    slicedog_api.resetCurrentForce()
                    slicedog_api.currentStep = 2
                }
            }
        }

        Component {
            id: createFixedPointComponent

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                readonly property string flatSurface: "flat_surface"
                readonly property string convexSurface: "convex_surface"
                readonly property string concaveSurface: "concave_surface"
                property bool forceDefined: slicedog_api.currentForceFacesFlat.length > 0

                function setSurfaceSelection(type) {
                    flatSurfaceButton.checked = type === flatSurface
                    convexSurfaceButton.checked = type === convexSurface
                    concaveSurfaceButton.checked = type === concaveSurface
                    slicedog_api.surfaceSelection = type
                }

                Button {
                    id: selectAreaButton
                    Layout.alignment: Qt.AlignHCenter
                    font.pixelSize: 13 * scaleFactor
                    leftPadding: 50 * scaleFactor
                    rightPadding: 50 * scaleFactor
                    topPadding: 8 * scaleFactor
                    bottomPadding: 8 * scaleFactor
                    checked: slicedog_api.selectMultipleAreas

                    background: Rectangle {
                        color: selectAreaButton.checked ? "#018DD7" : "#CCC"
                        radius: 6 * scaleFactor

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: fixedPointDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                        }
                    }

                    contentItem: Row {
                        spacing: 6 * scaleFactor
                        anchors.centerIn: parent

                        Image {
                            source: "../resources/icons/Cursor.svg"
                            width: 24 * scaleFactor
                            height: 24 * scaleFactor
                            mipmap: true
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            id: selectAreaText
                            text: slicedog_api.currentForceFaces.length > 0 && slicedog_api.currentForceFacesFlat.length > 0
                                ? slicedog_api.currentForceFaces.length + " area selected"
                                : "Select Area on Model"
                            color: "white"
                            font.bold: true
                            font.pixelSize: 13 * scaleFactor
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    onClicked: {
                        slicedog_api.selectMultipleAreas = !slicedog_api.selectMultipleAreas
                    }
                }

                Text {
                    text: "Need a paw? Change an area type to help me sniff it out!"
                    wrapMode: Text.WordWrap
                    font.pixelSize: 13 * scaleFactor
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                    Layout.leftMargin: 6 * scaleFactor
                    Layout.rightMargin: 6 * scaleFactor
                }

                RowLayout {
                    spacing: 25 * scaleFactor
                    Layout.alignment: Qt.AlignHCenter

                    // Flat Surface Button
                    Item {
                        Layout.preferredHeight: UM.Theme.getSize("button").width * scaleFactor
                        Layout.preferredWidth: UM.Theme.getSize("button").width * scaleFactor

                        UM.ToolbarButton {
                            id: flatSurfaceButton
                            anchors.centerIn: parent
                            text: catalog.i18nc("@label", "FlatSurface")
                            toolItem: Image {
                                source: "../resources/icons/Plane.svg"
                                mipmap: true
                            }
                            buttonSize: UM.Theme.getSize("button").width * scaleFactor
                            iconScale: 0.5 * scaleFactor
                            property bool needBorder: true
                            checkable: true
                            checked: slicedog_api.surfaceSelection === flatSurface
                            onClicked: setSurfaceSelection(flatSurface)

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                acceptedButtons: Qt.NoButton
                            }
                        }
                    }

                    // Convex Surface Button
                    Item {
                        Layout.preferredHeight: UM.Theme.getSize("button").width * scaleFactor
                        Layout.preferredWidth: UM.Theme.getSize("button").width * scaleFactor

                        UM.ToolbarButton {
                            id: convexSurfaceButton
                            anchors.centerIn: parent
                            text: catalog.i18nc("@label", "ConvexSurface")
                            toolItem: Image {
                                source: "../resources/icons/Hole.svg"
                                mipmap: true
                            }
                            buttonSize: UM.Theme.getSize("button").width * scaleFactor
                            iconScale: 0.5 * scaleFactor
                            property bool needBorder: true
                            checkable: true
                            checked: slicedog_api.surfaceSelection === convexSurface
                            onClicked: setSurfaceSelection(convexSurface)

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                acceptedButtons: Qt.NoButton
                            }
                        }
                    }

                    // Concave Surface Button
                    Item {
                        Layout.preferredHeight: UM.Theme.getSize("button").width * scaleFactor
                        Layout.preferredWidth: UM.Theme.getSize("button").width * scaleFactor

                        UM.ToolbarButton {
                            id: concaveSurfaceButton
                            anchors.centerIn: parent
                            text: catalog.i18nc("@label", "ConcaveSurface")
                            toolItem: Image {
                                source: "../resources/icons/Cylinder.svg"
                                mipmap: true
                            }
                            buttonSize: UM.Theme.getSize("button").width * scaleFactor
                            iconScale: 0.5 * scaleFactor
                            property bool needBorder: true
                            checkable: true
                            checked: slicedog_api.surfaceSelection === concaveSurface
                            onClicked: setSurfaceSelection(concaveSurface)

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                acceptedButtons: Qt.NoButton
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 26 * scaleFactor
                    color: "transparent"
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 50 * scaleFactor
                    color: "transparent"
                }

                RowLayout {
                    spacing: 8 * scaleFactor
                    Layout.leftMargin: 8 * scaleFactor
                    Layout.rightMargin: 8 * scaleFactor
                    Button {
                        Layout.fillWidth: true
                        background: Rectangle {
                            color: forceDefined ? "#FC8938" : "#C0C1C2"
                            radius: 6 * scaleFactor

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: fixedPointDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                            }
                        }

                        contentItem: Text {
                            text: slicedog_api.currentForceConfirmed ? "Update the Fixed Point" : "Create the Fixed Point"
                            color: "white"
                            font.pixelSize: 13 * scaleFactor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            anchors.fill: parent
                        }

                        onClicked: {
                            slicedog_api.confirmCurrentAnchor()
                        }
                    }

                    Button {
                        Layout.fillWidth: true
                        background: Rectangle {
                            color: "#FC4F38"
                            radius: 6 * scaleFactor

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: fixedPointDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                            }
                        }

                        contentItem: Text {
                            text: "Delete the Fixed Point"
                            color: "white"
                            font.pixelSize: 13 * scaleFactor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            anchors.fill: parent
                        }

                        onClicked: {
                            console.log("Delete the Fixed Point clicked")
                            slicedog_api.removeCurrentAnchor()
                        }
                    }
                }
            }
        }

        ModalPopup {
            id: genericPopup
            popupParent: step2Root
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

//        UnhandledPopup {
//            id: unhandledPopup
//            popupParent: step2Root
//        }
//
//        StepNotDefinedPopup {
//            id: stepNotDefinedPopup
//            popupParent: step2Root
//        }
//
//        ServerNotReachablePopup {
//            id: serverNotReachablePopup
//            popupParent: step2Root
//        }
//
//        UserNotRegisteredPopup {
//            id: userNotRegisteredPopup
//            popupParent: step2Root
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