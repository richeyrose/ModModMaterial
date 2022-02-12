from ctypes import Union
from typing import List
from .lib.multimethod import multimethod
from bpy.types import (
    Panel,
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


class MODMODMAT_PT_Material_options(Panel):
    bl_idname = 'MODMODMAT_PT_Material_Options'
    bl_label = 'Material Options'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'
    bl_order = 1

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
                create_nodes_panel(self, nodes, parent_frame)
            except KeyError:
                pass


def create_nodes_panel(self, nodes: list[Node], frame: NodeFrame) -> None:
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
        display_framed_nodes(self, frame, children)
        return

    # handles nested frames
    for frame in frames:
        create_nodes_panel(self, nodes, frame)

    if children:
        children = [n for n in children if n.type != 'FRAME']
        display_framed_nodes(self, frame, children)
    return


def display_framed_nodes(self, frame: NodeFrame, children: List[Node]) -> None:
    """Display all nodes in a frame.

    Args:
        frame (bpy.types.NodeFrame): Frame
        children (list): List of child nodes
    """
    if frame.label:
        frame_label = frame.label
    else:
        frame_label = frame.name

    layout = self.layout
    layout.label(text=frame_label)
    for child in children:
        if child.label:
            child_label = child.label
        else:
            child_label = child.name
        try:
            display_node(layout, child, child_label)
        # catch unsupported node types
        except TypeError:
            layout.label(text=child_label)
            layout.label(text="Node type not supported.")


@multimethod(UILayout, ShaderNodeValue, str)
def display_node(layout, node: ShaderNodeValue, node_label: str) -> None:
    layout.prop(node.outputs['Value'],
                'default_value', text=node_label)


@multimethod(UILayout, ShaderNodeRGB, str)
def display_node(layout, node: ShaderNodeRGB, node_label: str) -> None:
    layout.label(text=node_label)
    layout.template_color_picker(node, 'color', value_slider=True)


@multimethod(UILayout, ShaderNodeValToRGB, str)
def display_node(layout, node: ShaderNodeValToRGB, node_label: str) -> None:
    layout.label(text=node_label)
    layout.template_color_ramp(node, 'color_ramp', expand=True)


@multimethod(UILayout, ShaderNodeFloatCurve, str)
def display_node(layout, node: list, node_label: str) -> None:
    layout.label(text=node_label)
    layout.template_curve_mapping(
        node, 'mapping')


@multimethod(UILayout, ShaderNodeTexImage, str)
def display_node(layout, node: ShaderNodeTexImage, node_label: str) -> None:
    """Display inputs for image texture node.

    Args:
        node (bpy.types.ShaderNodeTexImage): node
        node_label (str): node_label
    """
    layout.label(text=node_label)
    layout.template_ID(node, "image", new="image.new", open="image.open")
    layout.prop(node, "interpolation", text="")
    layout.prop(node, "projection", text="")
    if node.projection == 'BOX':
        layout.prop(node, "projection_blend", text="")
    layout.prop(node, "extension", text="")


@multimethod(UILayout, ShaderNodeGroup, str)
def display_node(layout, node: ShaderNodeGroup, node_label: str) -> None:
    """Display all empty inputs in a group.

    Args:
        node (bpy.types.ShaderNodeGroup): Group Node
        node_label (str): Node label
    """
    inputs = [i for i in node.inputs if not i.links]

    if inputs:
        layout.label(text=node_label)

        for i in inputs:
            if i.label:
                input_label = i.label
            else:
                input_label = i.name
            layout.prop(i, 'default_value', text=input_label)
