import bpy
from .. problems import canExecute
from .. utils.layout import writeText
from .. utils.blender_ui import isViewportRendering

class AutoExecutionPanel(bpy.types.Panel):
    bl_idname = "an_auto_execution_panel"
    bl_label = "Auto Execution"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Animation Nodes"

    @classmethod
    def poll(cls, context):
        tree = cls.getTree()
        if tree is None: return False
        return tree.bl_idname == "an_AnimationNodeTree"

    def draw_header(self, context):
        tree = self.getTree()
        self.layout.prop(tree.autoExecution, "enabled", text = "")

    def draw(self, context):
        layout = self.layout

        if not canExecute():
            layout.label("Look in the 'Problems' panel", icon = "INFO")

        tree = context.space_data.edit_tree
        autoExecution = tree.autoExecution
        isRendering = isViewportRendering()
        layout.active = autoExecution.enabled

        col = layout.column()
        col.active = not isRendering
        text = "Always" if not isRendering else "Always (deactivated)"
        col.prop(autoExecution, "sceneUpdate", text = text)

        col = layout.column()
        col.active = not autoExecution.sceneUpdate or isRendering
        col.prop(autoExecution, "treeChanged", text = "Tree Changed")
        col.prop(autoExecution, "frameChanged", text = "Frame Changed")
        col.prop(autoExecution, "propertyChanged", text = "Property Changed")

        layout.prop(autoExecution, "minTimeDifference", slider = True)

    @classmethod
    def getTree(cls):
        return bpy.context.space_data.edit_tree
