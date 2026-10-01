import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import UM as UM
import Cura as Cura

Item {
    id: slicedogMain
    anchors.fill: parent

    property real scaleFactor: Math.min(parent.width / 1200, parent.height / 900)

    property int panelWidth: 360 * scaleFactor
    property int panelHeight: 680 * scaleFactor

    property int currentStep: slicedog_api.currentStep
    property list<Component> stepComponents: [
        step1Component,
        step2Component,
        step3Component,
        step4Component
    ]

    Rectangle {
        id: root
        width: panelWidth
        height: panelHeight
        x: 24 * scaleFactor
        color: "white"
        radius: 8 * scaleFactor
        border.color: "#C0C1C2"
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16 * scaleFactor
            spacing: 12 * scaleFactor

            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: 35 * scaleFactor

                RowLayout {
                    anchors.fill: parent
                    spacing: 8 * scaleFactor

                    Item { Layout.fillWidth: true }

                    Image {
                        source: "../resources/icons/logo-black.svg"
                        Layout.preferredHeight: 35 * scaleFactor
                        Layout.preferredWidth: 182 * scaleFactor
                        fillMode: Image.PreserveAspectFit
                        mipmap: true
                    }

                    Item { Layout.fillWidth: true }
                }

                RowLayout {
                    anchors.fill: parent
                    spacing: 0

                    Item { Layout.fillWidth: true }

                    Item {
                        Layout.preferredWidth: 32 * scaleFactor
                        Layout.preferredHeight: 32 * scaleFactor
                        Layout.alignment: Qt.AlignTop

//                        Rectangle {
//                            anchors.fill: parent
//                            color: "#FC8938"
//                            radius: 16 * scaleFactor
//                        }

                        Image {
                            anchors.centerIn: parent
                            source: "../resources/icons/Question2.svg"
                            width: 40 * scaleFactor
                            height: 40 * scaleFactor
                            fillMode: Image.PreserveAspectFit
                            mipmap: true
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: Qt.openUrlExternally("https://slicedog.com/help")
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                }
            }

            StepBar {
                id: stepBar
                currentStep: slicedog_api.currentStep
                scaleFactor: slicedogMain.scaleFactor
                onStepSelected: (index) => {
                    slicedog_api.currentStep = index
                }
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
            }

            Loader {
                id: stepLoader
                Layout.fillWidth: true
                Layout.fillHeight: true
                sourceComponent: stepComponents[slicedog_api.currentStep]
            }

            Component {
                id: step1Component
                Step1 {
                    scaleFactor: slicedogMain.scaleFactor
                }
            }
            Component {
                id: step2Component
                Step2 {
                    scaleFactor: slicedogMain.scaleFactor
                }
            }
            Component {
                id: step3Component
                Step3 {
                    scaleFactor: slicedogMain.scaleFactor
                }
            }
            Component {
                id: step4Component
                Step4 {
                    scaleFactor: slicedogMain.scaleFactor
                }
            }
        }
    }

    Rectangle {
        id: lastResultButton
        width: 120 * scaleFactor
        height: 40 * scaleFactor
        radius: 6
        color: "#FC8938"
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.rightMargin: lastResultButton.height / 2
        anchors.topMargin: lastResultButton.height / 2

        // Mouse area for interaction
        MouseArea {
            anchors.fill: parent
            onClicked: slicedog_api.importLastResult()
            cursorShape: Qt.PointingHandCursor
        }

        // Centered text
        Text {
            text: catalog.i18nc("@button", "Last Result")
            font.pixelSize: 14 * scaleFactor  // Dynamically adjust font size
            anchors.centerIn: parent
            color: "white"  // Set the text color to white
        }
    }

    Rectangle {
        id: loginButton
        width: 120 * scaleFactor
        height: 40 * scaleFactor
        radius: 6
        color: "#FC8938"
        anchors.top: lastResultButton.bottom
        anchors.right: parent.right
        anchors.rightMargin: loginButton.height / 2
        anchors.topMargin: loginButton.height / 2

        // Mouse area for interaction
        MouseArea {
            anchors.fill: parent
            onClicked: {
                if (slicedog_api.isLoggedIn) {
                    slicedog_api.logOut()
                } else {
                    slicedog_api.logInWithGoogle()
                }
            }
            cursorShape: Qt.PointingHandCursor
        }

        // Centered text
        Text {
            text: slicedog_api.isLoggedIn ? catalog.i18nc("@button", "Log out") : catalog.i18nc("@button", "Log In")
            font.pixelSize: 14 * scaleFactor  // Dynamically adjust font size
            anchors.centerIn: parent
            color: "white"  // Set the text color to white
        }
    }

    Rectangle {
        id: registerButton
        width: 120 * scaleFactor
        height: 40 * scaleFactor
        radius: 6
        color: "#FC8938"
        anchors.top: loginButton.bottom
        anchors.right: parent.right
        anchors.rightMargin: registerButton.height / 2
        anchors.topMargin: registerButton.height / 2
        visible: !slicedog_api.isLoggedIn

        // Mouse area for interaction
        MouseArea {
            anchors.fill: parent
            onClicked: slicedog_api.registerWithGoogle()
            cursorShape: Qt.PointingHandCursor
        }

        // Centered text
        Text {
            text: catalog.i18nc("@button", "Register")
            font.pixelSize: 14 * scaleFactor  // Dynamically adjust font size
            anchors.centerIn: parent
            color: "white"  // Set the text color to white
        }
    }
}
