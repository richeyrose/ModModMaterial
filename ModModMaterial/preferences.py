from bpy.types import AddonPreferences
from bpy.props import BoolProperty


class ModModMaterialPreferences(AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'collapsed')
