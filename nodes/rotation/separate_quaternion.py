import bpy
from ... base_types.node import AnimationNode

class SeparateQuaternionNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeparateQuaternionNode"
    bl_label = "Separate Quaternion"

    def create(self):
        self.inputs.new("an_QuaternionSocket", "Quaternion", "quaternion")
        self.outputs.new("an_FloatSocket", "W", "w")
        self.outputs.new("an_FloatSocket", "X", "x")
        self.outputs.new("an_FloatSocket", "Y", "y")
        self.outputs.new("an_FloatSocket", "Z", "z")
        
    def getExecutionCode(self):
        return "w, x, y, z = quaternion"

    def getUsedModules(self):
        return ["mathutils"]
