import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import UM as UM
import Cura as Cura

Item {
    id: base
    width: childrenRect.width
    height: childrenRect.height

    readonly property string flatSurface: "flat_surface"
    readonly property string convexSurface: "convex_surface"
    readonly property string concaveSurface: "concave_surface"

    UM.I18nCatalog {
        id: catalog;
        name: "Slicedog_1"
    }

    function setSurfaceSelection(type) {
        flatSurfaceButton.checked = type === flatSurface
        convexSurfaceButton.checked = type === convexSurface
        concaveSurfaceButton.checked = type === concaveSurface
        slicedog_api.surfaceSelection = type
    }

    Grid {
        id: baseGrid
        visible: true
        anchors.leftMargin: UM.Theme.getSize("default_margin").width
        anchors.top: parent.top
        columns: 1
        flow: Grid.TopToBottom
        spacing: Math.round(UM.Theme.getSize("default_margin").width / 2)

        Repeater {
            model: slicedog_api.objectsAsList
            delegate: Cura.SecondaryButton {
                id: button
                text: catalog.i18nc("@action:button", modelData.id);
                visible: true
                height: UM.Theme.getSize("setting_control").height;

                onClicked: {
                    slicedog_api.currentForceId = modelData.id
                    slicedog_api.currentForceFaces = modelData.faces
                    slicedog_api.currentForceCenter = modelData.center
                    // TODO pass more data?
                }
            }
        }

        UM.Label {
            id: surfaceSelectionLabel
            height: UM.Theme.getSize("setting").height
            text: catalog.i18nc("@label", "Select type of surface")
        }

        UM.Label {
            id: ctrlHintLabel
            height: UM.Theme.getSize("setting").height
            text: catalog.i18nc("@label", "Hold CTRL to select multiple areas at once")
        }

        Row {
            id: surfaceSelection
            spacing: UM.Theme.getSize("default_margin").width

            Item {
                UM.ToolbarButton {
                    id: flatSurfaceButton
                    text: catalog.i18nc("@label", "FlatSurface")
                    toolItem: Image
                    {
                        source: "../resources/icons/Plane.svg"
                    }
                    property bool needBorder: true
                    checkable: true
                    onClicked: setSurfaceSelection(flatSurface)
                    z: 2
                    checked: slicedog_api.surfaceSelection === flatSurface
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.NoButton
                    cursorShape: forceDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                }
            }

            Item {
                UM.ToolbarButton {
                    id: convexSurfaceButton
                    text: catalog.i18nc("@label", "ConvexSurface")
                    toolItem: Image
                    {
                        source: "../resources/icons/Hole.svg"
                    }
                    property bool needBorder: true
                    checkable: true
                    onClicked: setSurfaceSelection(convexSurface)
                    z: 2
                    checked: slicedog_api.surfaceSelection === convexSurface
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.NoButton
                    cursorShape: forceDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                }
            }

            Item {
                UM.ToolbarButton {
                    id: concaveSurfaceButton
                    text: catalog.i18nc("@label", "ConcaveSurface")
                    toolItem: Image
                    {
                        source: "../resources/icons/Cylinder.svg"
                    }
                    property bool needBorder: true
                    checkable: true
                    onClicked: setSurfaceSelection(concaveSurface)
                    z: 1
                    checked: slicedog_api.surfaceSelection === concaveSurface
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.NoButton
                    cursorShape: forceDetailLoader.opacity > 0 ? Qt.PointingHandCursor : Qt.ArrowCursor
                }
            }
        }

        UM.Label {
            height: UM.Theme.getSize("setting_control").height
            width: UM.Theme.getSize("message").width
            visible: slicedog_api.anchorsAsList.length == 0 || slicedog_api.forcesAsList.length == 0
            text: {
                if (slicedog_api.objectsAsList.length == 0) {
                    'Missing Force and Anchor. Click on model to select surface.'
                } else if (slicedog_api.anchorsAsList.length == 0) {
                    'Missing Anchor'
                } else if (slicedog_api.forcesAsList.length == 0) {
                    'Missing Forces'
                } else {
                    'Continue to Optimization'
                }
            }
        }

        Cura.SecondaryButton {
            id: continue_to_optimization_button
            text: catalog.i18nc("@action:button", "Continue to Optimization");
            visible: slicedog_api.anchorsAsList.length != 0 && slicedog_api.forcesAsList.length != 0
            height: UM.Theme.getSize("setting_control").height;
            onClicked: {
                UM.Controller.setActiveTool("Slicedog_1_OptimizationTool")
            }
        }
    }

}
