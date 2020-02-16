import bpy
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class SetEdgeCreaseNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetEdgeCreaseNode"
    bl_label = "Set Edge Crease"
    errorHandlingType = "EXCEPTION"

    useFloatList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Float", "useFloatList",
            ("Crease", "crease"), ("Creases", "creases")))
        self.newOutput("Object", "Object", "object")

    def execute(self, object, creases):
        if object is None: return None

        if object.type != "MESH":
            self.raiseErrorMessage("Object is not a mesh object.")

        if object.mode != "OBJECT":
            self.raiseErrorMessage("Object is not in object mode.")

        creases = VirtualDoubleList.create(creases, 0).materialize(len(object.data.edges))
        object.data.edges.foreach_set('crease', creases)
        object.data.update()
        return object
