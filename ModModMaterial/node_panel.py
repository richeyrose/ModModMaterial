import bpy
from bpy.types import Panel, PropertyGroup, NodeFrame
from bpy.props import PointerProperty, BoolProperty


class MODMODMAT_PT_Node_Options(Panel):
    bl_idname = 'MODMODMATE_PT_Node_Options'
    bl_label = 'Node options'
    bl_category = 'Node'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'Expose Nodes'

    @classmethod
    def poll(cls, context):
        return context.active_node is not None and context.active_node.type == 'FRAME'

    def draw(self, context):
        layout = self.layout
        node = context.active_node

        layout.prop(node.mmm_frame_props, 'expose_frame')


class MMM_Frame_Props(PropertyGroup):
    expose_frame: BoolProperty(
        name="Expose Frame",
        description="Expose frame and nodes in material panel?",
        default=False)


def register():
    bpy.types.NodeFrame.mmm_frame_props = PointerProperty(
        type=MMM_Frame_Props
    )


def unregister():
    del bpy.types.NodeFrame.mmm_frame_props
