import bpy
from ... data_structures import DoubleList
from ... base_types import AnimationNode, ListTypeSelectorSocket, VectorizedSocket

class midiTrackEvaluateNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiTrackEvaluateNode"
    bl_label = "MIDI Track Evaluate"
    bl_width_default = 180

    useNoteNumberList: VectorizedSocket.newProperty()

    def create(self):
        self.newInput("midiTrack", "Track", "track")
        self.newInput("Integer", "Channel", "channel")
        self.newInput(VectorizedSocket("Integer", "useNoteNumberList",
            ("noteNumber", "noteNumber"), ("numbers", "numbers")))
        self.newInput("Float", "Time", "time")
        self.newInput("Float", "Attack Time", "attackTime")
        self.newInput("Interpolation", "Attack Interpolation", "attackInterpolation")
        self.newInput("Float", "Release Time", "releaseTime")
        self.newInput("Interpolation", "Release Interpolation", "releaseInterpolation")
        self.newOutput(VectorizedSocket("Float", "useNoteNumberList",
            ("notePlayed", "note played"), ("notesplayed", "notes played")))

    def execute(self, track, channel, noteNumber, time, attackTime, attackInterpolation,
        releaseTime, releaseInterpolation):
        if track is None:
            if self.useNoteNumberList:
                return DoubleList.fromValues([0.0])
            else:
                return 0.0
        else:
            return track.evaluate(channel, self.useNoteNumberList, noteNumber, time, attackTime,
                attackInterpolation, releaseTime, releaseInterpolation)
