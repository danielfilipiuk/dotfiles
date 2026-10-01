import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import UM as UM

Popup {
    id: root
    objectName: root.objectName
    modal: true
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    anchors.centerIn: parent
    width: Math.min(380 * scaleFactor, parent.width * 0.9)

    property string titleText: ""
    property string messageText: ""
    property string button1Text: ""
    property var button1Action: function() {}
    property string button1Color: "#FC4F38"
    property string button2Text: ""
    property var button2Action: function() {}
    property string button2Color: "#FC8938"
    property bool showWarningIcon: false

    property alias popupParent: root.parent

    background: Rectangle {
        id: closeButton
        radius: 8 * scaleFactor
        color: "white"
        border.color: "#DDD"

        Button {
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.margins: 6 * scaleFactor
            background: Rectangle {
                color: "transparent"
                radius: 4 * scaleFactor
            }
            contentItem: Text {
                text: "✕"
                font.pixelSize: 16 * scaleFactor
                color: "#666"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: root.close()
            }
        }
    }

    contentItem: Item {
        width: root.availableWidth
        implicitHeight: columnContent.height + columnContent.anchors.topMargin

        Column {
            id: columnContent
            spacing: 10 * scaleFactor
            width: parent.width
            anchors {
                top: parent.top
                topMargin: 36 * scaleFactor
                left: parent.left
                right: parent.right
            }
//            width: root.availableWidth
//            anchors.margins: 10 * scaleFactor
//            anchors.topMargin: 30 * scaleFactor

            Text {
                text: root.titleText
                visible: root.titleText !== ""
                font.bold: true
                font.pixelSize: 14 * scaleFactor
                color: "#222"
                wrapMode: Text.WordWrap
                width: parent.width
            }

            RowLayout {
                spacing: 8 * scaleFactor
                width: parent.width

                Image {
                    visible: root.showWarningIcon
                    id: warningIcon
                    source: UM.Theme.getIcon("Warning")
                    Layout.preferredWidth: 30 * scaleFactor
                    Layout.preferredHeight: 30 * scaleFactor
                    Layout.alignment: Qt.AlignVCenter
                    fillMode: Image.PreserveAspectFit
                    mipmap: true
                }

                Text {
                    text: root.messageText
                    Layout.fillWidth: true
                    font.pixelSize: 13 * scaleFactor
                    color: "#333"
                    wrapMode: Text.WordWrap
                    textFormat: Text.RichText
                    onLinkActivated: (url) => Qt.openUrlExternally(url)

                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        acceptedButtons: Qt.NoButton
                        cursorShape: parent.hoveredLink !== "" ? Qt.PointingHandCursor : Qt.ArrowCursor
                    }
                }
            }

            RowLayout {
                spacing: 8 * scaleFactor
                width: parent.width

                Button {
                    visible: root.button1Text !== ""
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    implicitHeight: Math.max(36 * scaleFactor, contentItem.implicitHeight + topPadding + bottomPadding)

                    topPadding: 8 * scaleFactor
                    bottomPadding: 8 * scaleFactor
                    leftPadding: 14 * scaleFactor
                    rightPadding: 14 * scaleFactor

                    background: Rectangle {
                        color: root.button1Color
                        radius: 6 * scaleFactor

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                        }
                    }

                    contentItem: Label {
                        text: root.button1Text
                        color: "white"
                        font.pixelSize: 13 * scaleFactor
                        wrapMode: Text.WordWrap
                        maximumLineCount: 2
                        elide: Text.ElideRight
                        horizontalAlignment: Qt.AlignHCenter
                        verticalAlignment: Qt.AlignVCenter
                        anchors.fill: parent
                    }

                    onClicked: {
                        root.button1Action()
                        root.close()
                    }
                }

                Button {
                    visible: root.button2Text !== ""
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    implicitHeight: Math.max(36 * scaleFactor, contentItem.implicitHeight + topPadding + bottomPadding)

                    topPadding: 8 * scaleFactor
                    bottomPadding: 8 * scaleFactor
                    leftPadding: 14 * scaleFactor
                    rightPadding: 14 * scaleFactor

                    background: Rectangle {
                        color: root.button2Color
                        radius: 6 * scaleFactor

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                        }
                    }

                    contentItem: Label {
                        text: root.button2Text
                        color: "white"
                        font.pixelSize: 13 * scaleFactor
                        wrapMode: Text.WordWrap
                        maximumLineCount: 2
                        elide: Text.ElideRight
                        horizontalAlignment: Qt.AlignHCenter
                        verticalAlignment: Qt.AlignVCenter
                        anchors.fill: parent
                    }

                    onClicked: {
                        root.button2Action()
                        root.close()
                    }
                }
            }
        }
    }
}