import bpy
from ... data_structures import VirtualDoubleList
from ... base_types import AnimationNode, VectorizedSocket

class BevelVertexWeights(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetBevelVertexWeight"
    bl_label = "Set Bevel Vertex Weight"
    errorHandlingType = "EXCEPTION"

    useWeightList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput(VectorizedSocket("Float", "useWeightList",
            ("Weight", "weight"), ("Weights", "weights")))

        self.newOutput("Object", "Object", "object")

    def getExecutionFunctionName(self):
        if self.useWeightList:
            return "execute_WeightList"
        else:
            return "execute_SingleWeight"

    def execute_SingleWeight(self, object, weight):
        if object is None or object.type != "MESH" or object.mode != "OBJECT": return
        if object.data.use_customdata_vertex_bevel is False:
            object.data.use_customdata_vertex_bevel = True

        weights = VirtualDoubleList.create(weight, 0).materialize(len(object.data.vertices))
        object.data.vertices.foreach_set('bevel_weight', weights)
        object.data.update()
        return object

    def execute_WeightList(self, object, weights):
        if object is None or object.type != "MESH" or object.mode != "OBJECT": return
        if object.data.use_customdata_vertex_bevel is False:
            object.data.use_customdata_vertex_bevel = True

        weights = VirtualDoubleList.create(weights, 0).materialize(len(object.data.vertices))
        object.data.vertices.foreach_set('bevel_weight', weights)
        object.data.update()
        return object
