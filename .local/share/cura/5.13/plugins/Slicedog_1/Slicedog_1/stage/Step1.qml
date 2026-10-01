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
            messageText: "<b>You're almost there!</b><br>Your account has been created.<br>Please click the <b>Log In</b> button in the top-right corner to start using Slicedog.",
            button1Text: "OK",
            button1Color: "#FC4F38",
        }
    })

    Rectangle {
        id: panelDimmer
        anchors.fill: step1Root
        color: "#80000000"
        visible: genericPopup.visible
        z: 999
        radius: 6 * scaleFactor
    }

    ColumnLayout {
        id: step1Root
        anchors.fill: parent

        spacing: 8 * scaleFactor

        Layout.fillWidth: true
        Layout.fillHeight: true

        Text {
            text: "Define All Forces that affect the Part"
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
                    contentWidth: forceFlow.width
                    contentHeight: forceFlow.height
                    boundsBehavior: Flickable.StopAtBounds

                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AlwaysOn
                    }

                    Flow {
                        id: forceFlow
                        width: chipFlickable.width - 6 * scaleFactor
                        spacing: 8 * scaleFactor

                        Repeater {
                            model: slicedog_api.forcesAsList

                            delegate: Column {
                                spacing: 2 * scaleFactor

                                Rectangle {
                                    id: chip
                                    height: 18 * scaleFactor
                                    radius: 4 * scaleFactor
                                    color: "#eeeeee"
                                    border.color: "transparent"
    //                                border.color: slicedog_api.currentForceId === modelData.id ? "#FDDCC3" : "transparent"
                                    border.width: 1
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    width: forceText.implicitWidth + 30 * scaleFactor

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 6 * scaleFactor
                                        anchors.rightMargin: 6 * scaleFactor

                                        Text {
                                            id: forceText
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
                                        onClicked: slicedog_api.selectForce(modelData.id)
                                    }
                                }

                                Rectangle {
                                    width: chip.width
                                    height: 2 * scaleFactor
                                    color: slicedog_api.currentForceId === modelData.id ? "#FDDCC3" : "transparent"
                                }
                            }
                        }

                        Column {
                            spacing: 2 * scaleFactor
                            visible: slicedog_api.allForcesConfirmed

                            Rectangle {
                                id: addForceButton
                                height: 18 * scaleFactor
                                radius: 6 * scaleFactor
                                color: "#FC8938"
                                border.color: "transparent"
                                border.width: 1
                                width: addForceText.implicitWidth + 12 * scaleFactor

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 6 * scaleFactor
                                    anchors.rightMargin: 6 * scaleFactor

                                    Text {
                                        id: addForceText
                                        text: "+ Add New Force"
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
                                        slicedog_api.updateForcesWithCurrent()
    //                                    slicedog_api.updateForces(slicedog_api.currentForceAsDict)
                                    }
                                }
                            }

                            Rectangle {
                                width: addForceButton.width
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
                defaultText: "Click on “Add New Force” to start"
            }

//            Text {
//                text: "Click on “Add New Force” to start"
//                font.pixelSize: 13 * scaleFactor
//                color: "#333"
//            }
        }

//        Text {
//            text: "Click on “Add New Force” to start"
//            font.pixelSize: 14 * scaleFactor
//            color: "#333"
//        }

        Rectangle {
            color: "#F9F9F9"
            radius: 6 * scaleFactor
            border.color: "#CCC"
            Layout.fillWidth: true
            Layout.preferredHeight: 5
            Layout.fillHeight: true

            Loader {
                id: forceDetailLoader
                anchors.fill: parent
                opacity: slicedog_api.currentForceId === '' ? 0 : 1
                sourceComponent: createForceComponent
            }
        }

        Button {
            id: confirmAllForcesButton
            Layout.alignment: Qt.AlignHCenter
            leftPadding: 24 * scaleFactor
            rightPadding: 24 * scaleFactor
            opacity: slicedog_api.forcesAsList.length > 0 ? 1 : 0
            background: Rectangle {
                color: slicedog_api.allForcesConfirmed ? "#FC8938" : "#C0C1C2"
                radius: 6

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: confirmAllForcesButton.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                }
            }

            contentItem: Text {
                text: "Confirm All Forces to Move to Step 2"
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
                    slicedog_api.currentStep = 1
                }
            }
        }

        Component {
            id: createForceComponent

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                readonly property string flatSurface: "flat_surface"
                readonly property string convexSurface: "convex_surface"
                readonly property string concaveSurface: "concave_surface"
                property bool forceDefined: slicedog_api.currentForceFacesFlat.length > 0 && slicedog_api.currentForceMagnitude >= 0

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
                            cursorShape: forceDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
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
                            text: catalog.i18nc("@label", "Flat")
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
                            text: catalog.i18nc("@label", "Hole")
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
                            text: catalog.i18nc("@label", "Cylinder")
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

                RowLayout {
                    Layout.leftMargin: 48 * scaleFactor
                    spacing: 48 * scaleFactor

                    Text {
                        text: "Rotate Force Direction    "
                        wrapMode: Text.WordWrap
                        font.pixelSize: 12 * scaleFactor
                    }

                    Switch {
                        id: rotateSwitch
                        checked: slicedog_api.rotationActive
                        implicitWidth: 50 * scaleFactor
                        implicitHeight: 26 * scaleFactor

                        indicator: Rectangle {
                            id: rotateTrack
                            width: 50 * scaleFactor
                            height: 26 * scaleFactor
                            radius: height / 2
                            color: rotateSwitch.checked ? "#FC8938" : "#ccc"
                            border.color: "#444"
                            border.width: 1

                            Rectangle {
                                width: 22 * scaleFactor
                                height: 22 * scaleFactor
                                radius: height / 2
                                y: 2 * scaleFactor
                                x: rotateSwitch.checked ? (rotateTrack.width - width - y) : y
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
                                cursorShape: forceDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                                acceptedButtons: Qt.LeftButton

                                onClicked: {
                                    slicedog_api.rotationActive = !slicedog_api.rotationActive
                                }
                            }
                        }
                    }
                }

                Item {
                    Layout.leftMargin: 12 * scaleFactor
                    Layout.bottomMargin: 12 * scaleFactor
                    Text {
                        text: "Force Intensity"
                        wrapMode: Text.WordWrap
                        font.pixelSize: 13 * scaleFactor
                        font.bold: true
                    }
                }

                RowLayout {
                    Layout.leftMargin: 48 * scaleFactor
                    spacing: 48 * scaleFactor

                    Text {
                        text: "Precise Force in Newtons"
                        wrapMode: Text.WordWrap
                        font.pixelSize: 12 * scaleFactor
                    }

                    Switch {
                        id: forceSwitch

                        property bool internalChecked: false

                        Component.onCompleted: {
                            forceSwitch.internalChecked = slicedog_api.isCurrentForcePrecise
                        }

                        Connections {
                            target: slicedog_api
                            function onCurrentForceChanged() {
                                forceSwitch.internalChecked = slicedog_api.isCurrentForcePrecise
                            }
                        }

                        checked: forceSwitch.internalChecked
                        implicitWidth: 50 * scaleFactor
                        implicitHeight: 26 * scaleFactor

                        indicator: Rectangle {
                            id: track
                            width: 50 * scaleFactor
                            height: 26 * scaleFactor
                            radius: height / 2
                            color: forceSwitch.checked ? "#FC8938" : "#ccc"
                            border.color: "#444"
                            border.width: 1

                            Rectangle {
                                width: 22 * scaleFactor
                                height: 22 * scaleFactor
                                radius: height / 2
                                y: 2 * scaleFactor
                                x: forceSwitch.checked ? (track.width - width - y) : y
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
                                cursorShape: forceDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                                acceptedButtons: Qt.NoButton
                            }
                        }

                        onCheckedChanged: {
    //                        forceSwitch.internalChecked = checked

                            if (checked) {
                                defineForceLoader.currentOption = defineForceLoader.preciseOption
                                defineForceLoader.nextOption = defineForceLoader.defaultOption
                                defineForceLoader.sourceComponent = preciseForceComponent
                            } else {
                                defineForceLoader.currentOption = defineForceLoader.defaultOption
                                defineForceLoader.nextOption = defineForceLoader.preciseOption
                                defineForceLoader.sourceComponent = defaultForceComponent
                            }
                        }
                    }

                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 50 * scaleFactor
                    color: "transparent"

                    Loader {
                        id: defineForceLoader
                        sourceComponent: defaultForceComponent
                        anchors.horizontalCenter: parent.horizontalCenter

                        readonly property string defaultOption: "Default"
                        readonly property string preciseOption: "Precise Force"
                        property string currentOption: defaultOption
                        property string nextOption: preciseOption
                    }
                }

                Component {
                    id: defaultForceComponent

                    ColumnLayout {
                        height: 50 * scaleFactor
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 6 * scaleFactor

                        property alias value: slider.value

                        Item {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 16 * scaleFactor

                            Text {
                                text: "Very Low"
                                x: slider.leftPadding - Math.round(width / 2)
                                font.pixelSize: 12 * scaleFactor
                            }

                            Text {
                                text: "Very High"
                                x: slider.leftPadding + slider.availableWidth - Math.round(width / 2)
                                font.pixelSize: 12 * scaleFactor
                            }
                        }

                        Slider {
                            id: slider
                            Layout.preferredWidth: 240 * scaleFactor
                            from: 0
                            to: 100
                            value: 50
    //                        value: slicedog_api.currentForceMagnitude >= 0 ? slicedog_api.currentForceMagnitude : 50
                            Layout.preferredHeight: 36 * scaleFactor

                            // TODO this does not update value if new force is selected
                            Component.onCompleted: {
                                if (slicedog_api.currentForceMagnitude >= 0 && slicedog_api.currentForceUnit === "%") {
                                    slider.value = slicedog_api.currentForceMagnitude
                                } else {
                                    slicedog_api.currentForceMagnitude = slider.value
                                    slicedog_api.currentForceUnit = '%'
                                }
                            }

                            onValueChanged: {
                                slicedog_api.currentForceMagnitude = value
                                slicedog_api.currentForceUnit = '%'
                            }

                            Connections {
                                target: slicedog_api
                                function onCurrentForceChanged() {
                                    if (!slider.pressed && slicedog_api.currentForceMagnitude >= 0) {
                                        slider.value = slicedog_api.currentForceMagnitude
                                    } else if (slicedog_api.currentForceMagnitude < 0) {
                                        slider.value = 50
                                        slicedog_api.currentForceMagnitude = slider.value
                                        slicedog_api.currentForceUnit = '%'
                                    }
                                }
                            }

                            background: Rectangle {
                                height: 4 * scaleFactor
                                radius: 2 * scaleFactor
                                anchors.verticalCenter: parent.verticalCenter
                                width: parent.width
                                color: "#eee"

                                Rectangle {
                                    width: slider.visualPosition * parent.width
                                    height: parent.height
                                    color: "#FC8938"
                                    radius: 2 * scaleFactor
                                }

                                Repeater {
                                    id: tickRepeater
                                    model: 5
                                    Rectangle {
                                        width: 1
                                        height: 28 * scaleFactor
                                        radius: 1
                                        color: "#aaa"
                                        anchors.verticalCenter: parent.verticalCenter
                                        x: (parent.width - width) * (index / Math.max(tickRepeater.model - 1))
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: forceDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                                    acceptedButtons: Qt.NoButton
                                }
                            }

                            handle: Rectangle {
                                id: sliderHandle
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
                                    cursorShape: forceDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                                    acceptedButtons: Qt.NoButton
                                }
                            }
                        }
                    }
                }

                Component {
                    id: preciseForceComponent

                    ColumnLayout {
                        Layout.preferredHeight: 50 * scaleFactor
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 6 * scaleFactor
                        property real value: -1

                        RowLayout {
                            spacing: 8 * scaleFactor
                            Layout.alignment: Qt.AlignHCenter

                            Rectangle {
                                Layout.preferredWidth: 200 * scaleFactor
                                Layout.preferredHeight: 36 * scaleFactor
                                radius: 6 * scaleFactor
                                color: "white"
                                border.color: "#ccc"
                                border.width: 1

                                TextField {
                                    id: numberField
                                    anchors.fill: parent
                                    anchors.margins: 4 * scaleFactor
                                    font.pixelSize: 12 * scaleFactor
                                    text: ""
                                    placeholderText: "Force"
                                    color: "black"
                                    placeholderTextColor: "#888"
                                    background: null
                                    validator: RegularExpressionValidator {
                                        regularExpression: /^[0-9./]+$/
                                    }

                                    onTextChanged: {
                                        value = parseFloat(text)
                                        slicedog_api.currentForceMagnitude = value
                                        slicedog_api.currentForceUnit = 'N'
                                    }

                                    Component.onCompleted: {
                                        if (slicedog_api.currentForceMagnitude >= 0 && slicedog_api.currentForceUnit === "N") {
                                            text = slicedog_api.currentForceMagnitude
                                        } else {
                                            slicedog_api.currentForceMagnitude = -1
                                            slicedog_api.currentForceUnit = 'N'
                                        }
                                    }
                                }
                            }


                            Text {
                                text: "[N]"
                                font.pixelSize: 12 * scaleFactor
                                verticalAlignment: Text.AlignVCenter
                            }
                        }

                        Text {
                            text: "1 kg is approximately equal to 10 N"
                            font.pixelSize: 11 * scaleFactor
                            color: "#666"
                            Layout.alignment: Qt.AlignHCenter
                        }
                    }
                }

                // TODO: this adds the force, but the logic is different than before, so it needs to be updated
                RowLayout {
                    spacing: 8 * scaleFactor
                    Layout.leftMargin: 8 * scaleFactor
                    Layout.rightMargin: 8 * scaleFactor
                    Button {
                        property real forceValue: -1
                        property string forceUnit: ''

                        Layout.fillWidth: true
                        background: Rectangle {
                            color: forceDefined ? "#FC8938" : "#C0C1C2"
                            radius: 6 * scaleFactor

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: forceDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                            }
                        }

                        contentItem: Text {
                            text: slicedog_api.currentForceConfirmed ? "Update the Force" : "Create the Force"
                            color: "white"
                            font.pixelSize: 13 * scaleFactor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            anchors.fill: parent
                        }

    //                    onClicked: {
    //                        slicedog_api.confirmCurrentForce()
    //                    }

                        onClicked: {
                            if (defineForceLoader.currentOption === defineForceLoader.defaultOption) {
                                forceValue = defineForceLoader.item.value
                                forceUnit = '%'
                            } else {
                                forceValue = defineForceLoader.item.value
                                forceUnit = 'N'
                            }

                            slicedog_api.confirmCurrentForce(forceValue, forceUnit)
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
                                cursorShape: forceDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                            }
                        }

                        contentItem: Text {
                            text: "Delete the Force"
                            color: "white"
                            font.pixelSize: 13 * scaleFactor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            anchors.fill: parent
                        }

                        onClicked: {
                            slicedog_api.removeCurrentForce()
                        }
                    }
                }
            }
        }

        ModalPopup {
            id: genericPopup
            popupParent: step1Root
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
    }
}