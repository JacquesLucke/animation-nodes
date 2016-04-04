import bpy
from bpy.props import *
from ... tree_info import keepNodeState
from ... events import executionCodeChanged, propertyChanged
from ... sockets.info import toIdName, isList
from ... base_types.node import AnimationNode

repetitionTypeItems = [
    ("LOOP", "Loop", "Repeat", "NONE", 0),
    ("PING_PONG", "Ping Pong", "Repeat and Reverse", "NONE", 1),
    ("SHIFT", "Shift Each", "Shift Step Each Time", "NONE", 2),
    ("SHUFFLE", "Shuffle Each", "Shuffle Each Time", "NONE", 3)]

amountTypeItems = [
    ("AMOUNT", "Amount", "Repeat N Times", "NONE", 0),
    ("LENGTH_FLOOR", "Below Length", "Repeat up to Length, needs fill till length", "NONE", 1),
    ("LENGTH_CEIL", "Over Length", "Repeat over Length, needs slice down to length", "NONE", 2) ]

class RepeatListNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RepeatListNode"
    bl_label = "Repeat  List"

    def assignedTypeChanged(self, context):
        self.listIdName = toIdName(self.assignedType)
        self.generateSockets()

    assignedType = StringProperty(update = assignedTypeChanged)
    listIdName = StringProperty()

    def repetitionTypeChanged(self, context):
        self.generateSockets()
        executionCodeChanged()
        
    def amountTypeChanged(self, context):
        self.generateSockets()
        executionCodeChanged()

    repetitionType = EnumProperty(name = "Repeat Type", default = "LOOP",
        items = repetitionTypeItems, update = repetitionTypeChanged)
    amountType = EnumProperty(name = "Amount Type", default = "AMOUNT",
        items = amountTypeItems, update = amountTypeChanged)

    nodeSeed = IntProperty(update = propertyChanged)
    
    def create(self):
        self.assignedType = "Object List"
        self.generateSockets()

    @keepNodeState
    def generateSockets(self):
        self.inputs.clear()
        self.outputs.clear()

        if self.repetitionType == "SHIFT":
            self.inputs.new("an_IntegerSocket", "Step", "step")
        elif self.repetitionType == "SHUFFLE":
            self.inputs.new("an_IntegerSocket", "Seed", "seed")

        self.inputs.new(self.listIdName, "List", "inList").dataIsModified = True

        if self.amountType == "AMOUNT": 
            self.inputs.new("an_IntegerSocket", "Amount", "amount").value = 5
        elif "LENGTH" in self.amountType:
            self.inputs.new("an_IntegerSocket", "Length", "length").value = 23

        self.outputs.new(self.listIdName, "List", "outList")

    def draw(self, layout):
        layout.prop(self, "repetitionType", text = "")
        layout.prop(self, "amountType", text = "")

        if self.repetitionType == "SHUFFLE":
            layout.prop(self, "nodeSeed", text = "Node Seed")

    def drawAdvanced(self, layout):
        self.invokeSocketTypeChooser(layout, "assignListDataType",
            socketGroup = "LIST", text = "Change Type", icon = "TRIA_RIGHT")


    def getExecutionCode(self):

        yield "outList = []"
        yield "lenList = len(inList)"
        yield "if lenList:"
        
        if self.amountType == "LENGTH_FLOOR":
            yield "    amount = math.floor(abs(length) / lenList)"
        if self.amountType == "LENGTH_CEIL":
            yield "    amount = math.ceil(abs(length) / lenList)"

        if self.repetitionType == "PING_PONG":
            yield "    reList = reversed(inList)"
            
        yield "    for i in range(amount):"
        if self.repetitionType == "LOOP":
            yield "        outList += inList"
        
        elif self.repetitionType == "PING_PONG":
            yield "        if (i % 2) == 0: outList += inList"
            yield "        else: outList += reList"
        
        elif self.repetitionType == "SHIFT":
            yield "        shift = (amount + i) % lenList"
            yield "        inList = inList[-shift:] + inList[:-shift]"
            yield "        outList += inList"
        
        elif self.repetitionType == "SHUFFLE":
            yield "        random.seed(i + self.nodeSeed * 1245 + seed)"
            yield "        random.shuffle(inList)"
            yield "        outList += inList"

    def getUsedModules(self):
        return ["random", "math"]
    

    def edit(self):
        listDataType = self.getWantedDataType()
        self.assignType(listDataType)

    def assignListDataType(self, listDataType):
        self.assignedType = listDataType

    def getWantedDataType(self):
        listInput = self.inputs["List"].dataOrigin
        listOutputs = self.outputs["List"].dataTargets

        if listInput is not None: return listInput.dataType
        if len(listOutputs) == 1: return listOutputs["List"].dataType
        return self.inputs["List"].dataType

    def assignType(self, listDataType):
        if not isList(listDataType): return
        if listDataType == self.assignedType: return
        self.assignedType = listDataType


    def duplicate(self, sourceNode):
        self.randomizeNodeSeed()

    def randomizeNodeSeed(self):
        self.nodeSeed = int(random.random() * 100)
