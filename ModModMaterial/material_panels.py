from typing import List
from .lib.multimethod import multimethod
import bpy
from bpy.props import PointerProperty, EnumProperty, BoolProperty
from bpy.app.translations import pgettext_iface as iface_
from bpy.types import (
    Scene,
    Context,
    Panel,
    PropertyGroup,
    UILayout,
    ShaderNodeTexImage,
    ShaderNodeGroup,
    ShaderNodeValue,
    ShaderNodeRGB,
    ShaderNodeValToRGB,
    ShaderNodeVectorCurve,
    ShaderNodeRGBCurve,
    ShaderNodeFloatCurve,
    Node,
    NodeFrame)
from bpy_extras.node_utils import find_node_input


class MODMODMAT_PT_Material_options(Panel):
    bl_idname = 'MODMODMAT_PT_Material_Options'
    bl_label = 'Material Options'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'
    bl_order = 0

    @classmethod
    def poll(cls, context):
        try:
            for node in context.object.active_material.node_tree.nodes:
                return node.type == 'FRAME'
            return False
        except AttributeError:
            return False

    def draw(self, context):
        scene = context.scene
        scene_props = scene.mmm_scene_props
        layout = self.layout

        if scene_props.top_level_frame:
            layout.prop(scene_props, 'top_level_frame')
            top_level_frame = scene_props.top_level_frame

            obj = context.object
            mat = obj.active_material
            tree = mat.node_tree
            nodes = tree.nodes
            try:
                parent_frame = nodes[top_level_frame]
                create_nodes_panel(self, context, nodes, parent_frame)
            except KeyError:
                pass

    def show_socket_input(self, socket):
        return hasattr(socket, 'draw') and socket.enabled and not socket.is_linked


def create_nodes_panel(self, context, nodes: list[Node], frame: NodeFrame) -> None:
    """Recursively display all nodes within a frame, including nodes contained in sub frames.

    Args:
        nodes (list[Node]): nodes to search within
        frame (bpy.types.NodeFrame): parent node frame.
    """
    children = [n for n in nodes if n.parent ==
                frame and n.type != 'FRAME']

    frames = sorted([n for n in nodes if n.parent ==
                    frame and n.type == 'FRAME'],
                    key=lambda x: x.label)

    if not frames:
        display_framed_nodes(self, context, children)
        return

    # handles nested frames
    layout = self.layout
    for f in frames:
        if f.label:
            frame_label = f.label
        else:
            frame_label = f.name
        layout.label(text=frame_label)
        create_nodes_panel(self, context,  nodes, f)

    if children:
        if frame.label:
            frame_label = frame.label
        else:
            frame_label = frame.name
        layout.label(text=frame_label)
        children = [n for n in children if n.type != 'FRAME']
        display_framed_nodes(self, context, children)
    return


def display_framed_nodes(self, context, children: List[Node]) -> None:
    """Display all nodes in a frame.

    Args:
        frame (bpy.types.NodeFrame): Frame
        children (list): List of child nodes
    """

    layout = self.layout

    for child in children:
        if child.label:
            child_label = child.label
        else:
            child_label = child.name
        try:
            display_node(self, context, child_label, child)
        # catch unsupported node types
        except TypeError:
            layout.label(text=child_label)
            layout.label(text="Node type not supported.")


def display_node(self, context, node_label, node) -> None:
    if node.type in ('REROUTE', 'FRAME'):
        return
    if node.mmm_node_props.exclude_node:
        return

    layout = self.layout
    if node.type != 'VALUE':
        row = layout.row()
        icon = 'DOWNARROW_HLT' if node.subpanel_status else 'RIGHTARROW'
        row.prop(node, 'subpanel_status', icon=icon,
                 icon_only=True, emboss=False)
        row.label(text=node_label)

    if node.subpanel_status or node.type == 'VALUE':
        layout.context_pointer_set("node", node)
        if hasattr(node, "draw_buttons_ext"):
            node.draw_buttons_ext(context, layout)
        elif hasattr(node, "draw_buttons"):
            node.draw_buttons(context, layout)

        # XXX this could be filtered further to exclude socket types
        # which don't have meaningful input values (e.g. cycles shader)
        value_inputs = [
            socket for socket in node.inputs if self.show_socket_input(socket)]
        if value_inputs:
            layout.separator()
            layout.label(text="Inputs:")
            for socket in value_inputs:
                row = layout.row()
                socket.draw(
                    context,
                    row,
                    node,
                    iface_(socket.label if socket.label else socket.name,
                           socket.bl_rna.translation_context),
                )


class MMM_Scene_Props(PropertyGroup):
    def create_frame_enums(self, context):
        enum_items = []
        if context is None:
            return enum_items

        obj = context.object
        mat = obj.active_material
        tree = mat.node_tree
        nodes = tree.nodes
        try:
            frames = sorted([
                n for n in nodes
                if n.type == 'FRAME' and n.mmm_frame_props.expose_frame],
                key=lambda n: n.label)
        except KeyError:
            return enum_items

        if not frames:
            return enum_items

        for frame in frames:
            if frame.label:
                label = frame.label
            else:
                label = frame.name

            enum = (frame.name, label, "")
            enum_items.append(enum)

        return enum_items

    top_level_frame: EnumProperty(
        name="Frame",
        items=create_frame_enums,
        description="Any nodes or frames within this frame will be exposed for editing.")


def register():
    bpy.types.Scene.mmm_scene_props = PointerProperty(
        type=MMM_Scene_Props)
    Node.subpanel_status = BoolProperty(
        default=False
    )


def unregister():
    del Node.subpanel_status
    del bpy.types.Scene.mmm_scene_props
