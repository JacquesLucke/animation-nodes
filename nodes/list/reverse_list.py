import bpy
from bpy.props import *
from ... tree_info import keepNodeLinks
from ... sockets.info import toIdName, isList, isLimitedList, toGeneralListIdName, toDataType
from ... base_types.node import AnimationNode

class ReverseListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ReverseListNode"
    bl_label = "Reverse List"

    def assignedTypeChanged(self, context):
        self.listIdName = toIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    listIdName = StringProperty()

    def create(self):
        self.assignedType = "Object List"

    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")

    def getExecutionCode(self):
        return "reversedList = list(reversed(inList))"

    def edit(self):
        listDataType = self.getWantedDataType()
        self.assignType(listDataType)

    def getWantedDataType(self):
        listInput = self.inputs[0].dataOrigin
        listOutputs = self.outputs[0].dataTargets

        if listInput is not None: 
            idName = listInput.bl_idname
            if isLimitedList(idName): idName = toGeneralListIdName(idName)
            return toDataType(idName)
        if len(listOutputs) == 1: return listOutputs[0].dataType
        return self.inputs[0].dataType

    def assignType(self, listDataType):
        if not isList(listDataType): return
        if listDataType == self.assignedType: return
        self.assignedType = listDataType

    @keepNodeLinks
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(self.listIdName, "List", "inList").dataIsModified = True
        self.outputs.new(self.listIdName, "Reversed List", "reversedList")
