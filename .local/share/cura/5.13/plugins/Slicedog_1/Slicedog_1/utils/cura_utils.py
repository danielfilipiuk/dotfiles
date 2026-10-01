from UM.Application import Application
from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

def getPrintableNodes():
    scene = Application.getInstance().getController().getScene()
    root = scene.getRoot()

    printable_nodes = []

    for node in DepthFirstIterator(root):
        isSliceable = node.callDecoration("isSliceable")
        isPrinting = not node.callDecoration("isNonPrintingMesh")
        isInfillMesh = node.callDecoration("isInfillMesh")
        isSupport = False

        stack = node.callDecoration("getStack")

        if stack:
            isSupport = stack.getProperty("support_mesh", "value")

        if isSliceable and (isPrinting or isInfillMesh) and not isSupport:
            printable_nodes.append(node)

    return printable_nodes