from bpy.types import AddonPreferences
from bpy.props import BoolProperty


class ModModMaterialPreferences(AddonPreferences):
    bl_idname = __package__

    show_mat_options_in_n_menu: BoolProperty(
        name="Show material options in N menu",
        default=True
    )

    show_mat_options_in_mat_props: BoolProperty(
        name="Show material options in material properties panel",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'show_mat_options_in_n_menu')
        layout.prop(self, 'show_mat_options_in_mat_props')
