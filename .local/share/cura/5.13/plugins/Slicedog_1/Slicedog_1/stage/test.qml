import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import UM as UM
import Cura as Cura

Item {
    id: slicedogMain

    Rectangle {
        id: root
        width: 360
        height: 580
        color: "white"
        radius: 8
        border.color: "#CCCCCC"
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            // Header with logo and help icon
            RowLayout {
                width: parent.width
                spacing: 8
                Image {
                    source: "../resources/icons/logo-black.svg"
                    height: 32
                    anchors.fill: parent
                    fillMode: Image.PreserveAspectFit
                }
                Item { Layout.fillWidth: true }
                ToolButton {
                    icon.source: "qrc:/icons/help.svg"
                }
            }

            // Steps indicator
            RowLayout {
                spacing: 10
                Repeater {
                    model: 4
                    delegate: ColumnLayout {
                        spacing: 2
                        Rectangle {
                            width: 12
                            height: 12
                            radius: 6
                            color: index === 0 ? "#000" : "#CCC"
                        }
                        Text {
                            text: "Step " + (index + 1)
                            font.pixelSize: 10
                            color: "#666"
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                }
            }

            // Title
            Text {
                text: "Define All Forces that affect the Part"
                wrapMode: Text.WordWrap
                font.pixelSize: 14
                font.bold: true
                color: "#333"
            }

            // Add New Force button
            Button {
                text: "+ Add New Force"
                background: Rectangle {
                    color: "#FFA500"
                    radius: 6
                }
                font.pixelSize: 12
                height: 36
            }

            // Info text
            Text {
                text: "Click on “Add New Force” to start"
                font.pixelSize: 12
                color: "#888"
            }

            // Placeholder list box
            Rectangle {
                color: "#F9F9F9"
                radius: 6
                border.color: "#CCC"
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }
    }
}