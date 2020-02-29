import bpy
from bpy.props import *
from ... events import executionCodeChanged
from .. falloff.falloffs import offsetFloatList
from .. vector.offset_vector import offsetVector3DList
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures import VirtualVector3DList, VirtualDoubleList

class OffsetGPStrokeNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_OffsetGPStrokeNode"
    bl_label = "Offset GP Stroke"
    errorHandlingType = "EXCEPTION"

    def checkedPropertiesChanged(self, context):
        self.updateSocketVisibility()
        executionCodeChanged()

    useLocation: BoolProperty(update = checkedPropertiesChanged)
    useStrength: BoolProperty(update = checkedPropertiesChanged)
    usePressure: BoolProperty(update = checkedPropertiesChanged)
    useUVRotation: BoolProperty(update = checkedPropertiesChanged)

    useVectorList: VectorizedSocket.newProperty()
    useStrengthList: VectorizedSocket.newProperty()
    usePressureList: VectorizedSocket.newProperty()
    useUVRotationList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("GPStroke", "Stroke", "stroke", dataIsModified = True)
        self.newInput("Falloff", "Falloff", "falloff")
        self.newInput(VectorizedSocket("Vector", "useVectorList",
            ("Location", "offsetLocations", dict(value = (0, 0, 1))),
            ("Locations", "offsetLocations")))
        self.newInput(VectorizedSocket("Float", "useStrengthList",
            ("Strength", "offsetStrength", dict(value = 1)),
            ("Strengths", "offsetStrengths")))
        self.newInput(VectorizedSocket("Float", "usePressureList",
            ("Pressure", "offsetPressure", dict(value = 1)),
            ("Pressures", "offsetPressures")))
        self.newInput(VectorizedSocket("Float", "useUVRotationList",
            ("UV-Rotation", "offsetUVRotation", dict(value = 1)),
            ("UV-Rotations", "offsetUVRotations")))

        self.newOutput("GPStroke", "Stroke", "stroke")

        self.updateSocketVisibility()

    def draw(self, layout):
        col = layout.column(align = True)

        row = col.row(align = True)
        row.prop(self, "useLocation", text = "Location", toggle = True)
        row.prop(self, "useStrength", text = "Strength", toggle = True)

        row = col.row(align = True)
        row.prop(self, "usePressure", text = "Pressure", toggle = True)
        row.prop(self, "useUVRotation", text = "UVRotation", toggle = True)

    def updateSocketVisibility(self):
        self.inputs[2].hide = not self.useLocation
        self.inputs[3].hide = not self.useStrength
        self.inputs[4].hide = not self.usePressure
        self.inputs[5].hide = not self.useUVRotation

    def execute(self, stroke, falloff, offsetLocations, offsetStrengths, offsetPressures, offsetUVRotations):
        if not any((self.useLocation, self.useStrength, self.usePressure, self.useUVRotation)):
            return stroke

        falloffEvaluator = self.getFalloffEvaluator(falloff)

        if self.useStrength:
            _offsetStrengths = VirtualDoubleList.create(offsetStrengths, 0)
            offsetFloatList(stroke.vertices, stroke.strengths, _offsetStrengths, falloffEvaluator)

        if self.usePressure:
            _offsetPressures = VirtualDoubleList.create(offsetPressures, 0)
            offsetFloatList(stroke.vertices, stroke.pressures, _offsetPressures, falloffEvaluator)

        if self.useUVRotation:
            _offsetUVRotations = VirtualDoubleList.create(offsetUVRotations, 0)
            offsetFloatList(stroke.vertices, stroke.uvRotations, _offsetUVRotations, falloffEvaluator)

        if self.useLocation:
            _offsetLocations = VirtualVector3DList.create(offsetLocations, (0, 0, 0))
            offsetVector3DList(stroke.vertices, _offsetLocations, falloffEvaluator)

        return stroke

    def getFalloffEvaluator(self, falloff):
        try: return falloff.getEvaluator("LOCATION")
        except: self.raiseErrorMessage("This falloff cannot be evaluated for vectors")
