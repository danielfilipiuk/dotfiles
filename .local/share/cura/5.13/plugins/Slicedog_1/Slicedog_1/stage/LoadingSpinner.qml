import QtQuick

Item {
    id: spinner
    property color spinnerColor: "black"
    property color backgroundColor: "white"
    property real size: 16
    property real borderWidth: size / 8
    width: size
    height: size
    z: 2

    Canvas {
        id: spinnerCanvas
        anchors.fill: parent
        antialiasing: true
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)

            ctx.beginPath()
            ctx.arc(width/2, height/2, width/2 + borderWidth/2 - 0.5, 0, Math.PI * 2)
            ctx.fillStyle = spinner.backgroundColor
            ctx.fill()
//            if (spinner.borderWidth > 0) {
//                ctx.lineWidth = spinner.borderWidth
//                ctx.strokeStyle = "black"
//                ctx.stroke()
//            }

//            var lw = Math.max(1, Math.round(height / 6))
            ctx.lineWidth = borderWidth
            ctx.strokeStyle = spinner.spinnerColor
            ctx.lineCap = "round"
            ctx.beginPath()
            ctx.arc(width/2, height/2, width/2 - 1, 0, Math.PI * 1.5)
            ctx.stroke()

//            ctx.lineWidth = parent.height / 10
//            ctx.strokeStyle = spinner.spinnerColor
//            ctx.beginPath()
//            ctx.arc(width / 2, height / 2, width / 2 - 4, 0, Math.PI * 1.5)
//            ctx.stroke()
        }
    }

    property real rotation: 0
    transform: Rotation {
        origin.x: width / 2
        origin.y: height / 2
        angle: spinner.rotation
    }

    NumberAnimation on rotation {
        running: true
        loops: Animation.Infinite
        duration: 1000
        from: 0
        to: 360
    }
}
