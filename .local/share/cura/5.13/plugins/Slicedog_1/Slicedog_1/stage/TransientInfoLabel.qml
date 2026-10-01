import QtQuick
import QtQuick.Layouts

Item {
    id: root

    property real wrapWidth: -1
    property real scaleFactor: 1.0

    property string sourceValue: ""
    property string defaultText: "TODO"
    property int duration: 6000
    property bool autoHide: true

    property alias font: label.font
    property color color: "#333"

    property string displayText: ""

    Layout.fillWidth: true
    height: label.implicitHeight

//    width: label.width
//    height: label.height

    Timer {
        id: hideTimer
        interval: root.duration
        repeat: false
        onTriggered: {
            if (root.autoHide) {
                root.displayText = ""
            }
        }
    }

    onSourceValueChanged: {
        hideTimer.stop()
        displayText = sourceValue
        if (sourceValue !== "" && autoHide) {
            hideTimer.start()
        }
    }

    Text {
        id: label
        text: displayText === "" ? root.defaultText : displayText
        color: root.color
        wrapMode: Text.WordWrap
        width: wrapWidth > 0 ? wrapWidth : root.width
        font.pixelSize: 13 * scaleFactor
    }
}
