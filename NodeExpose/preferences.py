from bpy.types import AddonPreferences
from bpy.props import BoolProperty


class ModModMaterialPreferences(AddonPreferences):
    bl_idname = __package__

    expose_mat_nodes_in_3d_n_panel: BoolProperty(
        name="Expose material nodes in 3D view N panel",
        default=True
    )

    expose_mat_nodes_in_mat_props: BoolProperty(
        name="Expose material nodes in material properties panel",
        default=True
    )

    expose_mat_nodes_in_node_n_panel: BoolProperty(
        name="Expose material nodes in node editor N panel",
        default=True
    )

    expose_geom_nodes_in_3d_n_panel: BoolProperty(
        name="Expose geometry nodes in 3D view N panel",
        default=True
    )

    expose_geom_nodes_in_node_n_panel: BoolProperty(
        name="Expose geometry nodes in node editor N panel",
        default=True
    )

    expose_comp_nodes_in_node_n_panel: BoolProperty(
        name="Expose compositor nodes in node editor N panel",
        default=True
    )

    expose_comp_nodes_in_3d_n_panel: BoolProperty(
        name="Expose compositor nodes in 3D view N panel",
        default=True
    )

    expose_texture_nodes_in_node_n_panel: BoolProperty(
        name="Expose texture nodes in node editor N panel",
        default=True
    )

    expose_texture_nodes_in_3d_n_panel: BoolProperty(
        name="Expose texture nodes in 3D view N panel",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'expose_mat_nodes_in_3d_n_panel')
        layout.prop(self, 'expose_mat_nodes_in_node_n_panel')
        layout.prop(self, 'expose_mat_nodes_in_mat_props')
        layout.prop(self, 'expose_geom_nodes_in_3d_n_panel')
        layout.prop(self, 'expose_geom_nodes_in_node_n_panel')
        layout.prop(self, 'expose_comp_nodes_in_node_n_panel')
        layout.prop(self, 'expose_comp_nodes_in_3d_n_panel')
        layout.prop(self, 'expose_texture_nodes_in_node_n_panel')
        layout.prop(self, 'expose_texture_nodes_in_3d_n_panel')
