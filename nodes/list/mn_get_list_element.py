import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... utils.mn_node_utils import *
from ... sockets.mn_socket_info import *
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_GetListElementNode(Node, AnimationNode):
    bl_idname = "mn_GetListElementNode"
    bl_label = "Get Element"
    
    #sometimes we need to limit min to 0, unlike where we have start/end
    #by default False, to not break existing trees
    allowNegativeIndex = BoolProperty(default = False, description = "Allow negative index for reversed selection")
    
    def init(self, context):
        forbidCompiling()
        self.generateSockets()
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"List" : "list",
                "Index" : "index",
                "Fallback" : "fallback"}
    def getOutputSocketNames(self):
        return {"Element" : "element"}
        
    def draw_buttons(self, context, layout): 
        layout.prop(self, "allowNegativeIndex", text = "Negative Index")
        
    def execute(self, list, index, fallback):  
        minIndex = -len(list) if self.allowNegativeIndex else 0
        if minIndex <= index < len(list): 
            return list[index]
        return fallback
        
    def update(self):
        nodeTree = self.id_data
        treeInfo = NodeTreeInfo(nodeTree)
        originSocket = treeInfo.getDataOriginSocket(self.inputs.get("List"))
        targetSockets = treeInfo.getDataTargetSockets(self.outputs.get("Element"))
        
        forbidCompiling()
        if originSocket is not None and len(targetSockets) == 0:
            self.generateSockets(originSocket.bl_idname)
            nodeTree.links.new(self.inputs.get("List"), originSocket)
        if originSocket is None and len(targetSockets) == 1:
            self.generateSockets(getListSocketIdName(targetSockets[0].bl_idname))
            nodeTree.links.new(targetSockets[0], self.outputs.get("Element"))
        allowCompiling()
        
    def generateSockets(self, listIdName = "mn_ObjectListSocket"):
        if listIdName is None: return
        baseIdName = getListBaseSocketIdName(listIdName)
        if baseIdName is None: return
        if listIdName == getattr(self.inputs.get("List"), "bl_idname", None): return
        
        forbidCompiling()
        self.inputs.clear()
        self.outputs.clear()
        self.inputs.new(listIdName, "List")
        self.inputs.new("mn_IntegerSocket", "Index")
        self.inputs.new(baseIdName, "Fallback")
        self.outputs.new(baseIdName, "Element")
        allowCompiling()
