import bpy
from bpy.props import *
from ... math import Vector
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import (
    Color,
    FloatList,
    VirtualLongList,
    VirtualColorList,
    VirtualDoubleList,
    VirtualVector3DList,
    VirtualBooleanList,
)

dataTypeItems = [
    ("FLOAT", "Float", "", "NONE", 0),
    ("INT", "Integer", "", "NONE", 1),
    ("FLOAT_VECTOR", "Vector", "", "NONE", 2),
    ("FLOAT_COLOR", "Color", "", "NONE", 3),
    ("BYTE_COLOR", "Byte Color", "", "NONE", 4),
    ("BOOLEAN", "Boolean", "", "NONE", 5),
]
domainItems = [
    ("POINT", "Point", "", "NONE", 0),
    ("EDGE", "Edge", "", "NONE", 1),
    ("CORNER", "Corner", "", "NONE", 2),
    ("POLYGON", "Polygon", "NONE", 3),
]

class SetCustomAttributeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetCustomAttributeNode"
    bl_label = "Set Custom Attribute"
    errorHandlingType = "EXCEPTION"

    dataType: EnumProperty(name = "Data Type", default = "FLOAT",
        items = dataTypeItems, update = AnimationNode.refresh)

    domain: EnumProperty(name = "Domain", default = "POINT",
        items = domainItems, update = AnimationNode.refresh)

    useDataList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("Object", "Object", "object", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Text", "Attribute Name", "attName", value = "AN-Att")
        if self.dataType == "FLOAT":
            self.newInput(VectorizedSocket("Float", "useDataList",
            ("Value", "data"), ("Values", "data")))
        elif self.dataType == "INT":
            self.newInput(VectorizedSocket("Integer", "useDataList",
            ("Value", "data"), ("Values", "data")))
        elif self.dataType == "FLOAT_VECTOR":
            self.newInput(VectorizedSocket("Vector", "useDataList",
            ("Vector", "data"), ("Vectors", "data")))
        elif self.dataType in ["FLOAT_COLOR", "BYTE_COLOR"]:
            self.newInput(VectorizedSocket("Color", "useDataList",
            ("Color", "data"), ("Colors", "data")))
        else:
            self.newInput(VectorizedSocket("Boolean", "useDataList",
            ("Value", "data"), ("Values", "data")))

        self.newOutput("Object", "Object", "object")

    def draw(self, layout):
        layout.prop(self, "dataType", text = "")
        layout.prop(self, "domain", text = "")

    def execute(self, object, attName, data):
        if object is None: return object
        if attName == "": self.raiseErrorMessage("Attribute name can't be empty.")

        attribute = object.data.attributes.get(attName)
        if attribute is None:
            attribute = object.data.attributes.new(attName, self.dataType, self.domain)
        elif attribute.data_type != self.dataType or attribute.domain != self.domain:
            object.data.attributes.remove(attribute)
            attribute = object.data.attributes.new(attName, self.dataType, self.domain)

        if self.domain == "POINT":
            amount = len(object.data.vertices)
        elif self.domain == "EDGE":
            amount = len(object.data.edges)
        elif self.domain == "CORNER":
            amount = len(object.data.loops)
        else:
            amount = len(object.data.polygons)

        if self.dataType == "FLOAT":
            _data = FloatList.fromValues(VirtualDoubleList.create(data, 0).materialize(amount))
        elif self.dataType == "INT":
            _data = VirtualLongList.create(data, 0).materialize(amount)
        elif self.dataType == "FLOAT_VECTOR":
            _data = VirtualVector3DList.create(data, Vector((0, 0, 0))).materialize(amount)
        elif self.dataType in ["FLOAT_COLOR", "BYTE_COLOR"]:
            _data = VirtualColorList.create(data, Color((0, 0, 0, 0))).materialize(amount)
        else:
            _data = VirtualBooleanList.create(data, False).materialize(amount)

        if self.dataType in ["FLOAT", "INT", "BOOLEAN"]:
            attribute.data.foreach_set("value", _data.asMemoryView())
        elif self.dataType == "FLOAT_VECTOR":
            attribute.data.foreach_set("vector", _data.asMemoryView())
        else:
            attribute.data.foreach_set("color", _data.asMemoryView())

        attribute.data.update()
        return object
