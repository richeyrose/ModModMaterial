from typing import List
import bpy
from bpy.props import PointerProperty, EnumProperty
from bpy.app.translations import pgettext_iface as iface_
from bpy.types import (
    Panel,
    PropertyGroup,
    Node,
    NodeFrame)
from .lib.utils import get_prefs


class NODE_EXPOSE_PT_Material_N_Panel(Panel):
    bl_idname = 'NODE_EXPOSE_PT_Material_N_Panel'
    bl_label = 'Material Options'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Node Expose'

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        if prefs.show_mat_options_in_n_menu:
            return mat_has_exposed_nodes(context)
        return False

    def draw(self, context):
        """Draw panel in material properties

        Args:
            context (bpy.types.Context): Blender context
        """
        draw_material_panel(self, context)


class MODMODMAT_PT_Material_options(Panel):
    bl_idname = 'MODMODMAT_PT_Material_Options'
    bl_label = 'Material Options'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'
    bl_order = 0

    @classmethod
    def poll(cls, context):
        """Check there is a valid frame in node tree.

        Args:
            context (bpy.types.Context): Blender Context

        Returns:
            bool: bool
        """
        prefs = get_prefs()
        if prefs.show_mat_options_in_mat_props:
            return mat_has_exposed_nodes(context)
        return False

    def draw(self, context):
        """Draw panel in material properties

        Args:
            context (bpy.types.Context): Blender context
        """
        draw_material_panel(self, context)


class NODE_EXPOSE_PT_Geometry_N_Panel(Panel):
    bl_idname = 'NODE_EXPOSE_PT_Geometry_N_Panel'
    bl_label = 'Geometry Node Options'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Node Expose'

    @classmethod
    def poll(cls, context):
        try:
            mods = context.object.modifiers
            for mod in mods:
                if mod.type == 'NODES':
                    for node in mod.node_group.nodes:
                        if node.type == 'FRAME' and node.mmm_node_props.expose_frame:
                            return True
            return False
        except AttributeError:
            return False

    def draw(self, context):
        scene = context.scene
        scene_props = scene.mmm_scene_props
        layout = self.layout
        obj = context.object
        mods = [m for m in obj.modifiers if m.type == 'NODES']
        for mod in mods:
            node_group = mod.node_group
            nodes = node_group.nodes
            for node in nodes:
                layout = self.layout
                layout.label(text=node.name)
        # node_groups = [
        #     m.node_group.nodes for m in obj.modifiers if m.type == 'NODES']
        # #nodes = [n.nodes for n in node_groups]
        # for n in node_groups:
        #     layout = self.layout
        #     layout.label(text=n.name)


def mat_has_exposed_nodes(context):
    try:
        for node in context.object.active_material.node_tree.nodes:
            if node.type == 'FRAME' and node.mmm_node_props.expose_frame:
                return True
        return False
    except AttributeError:
        return False


def draw_material_panel(self, context):
    scene = context.scene
    scene_props = scene.mmm_scene_props
    layout = self.layout
    if scene_props.mat_top_level_frame:
        layout.prop(scene_props, 'mat_top_level_frame')
        layout.separator()
        top_level_frame = scene_props.mat_top_level_frame

        obj = context.object
        mat = obj.active_material
        tree = mat.node_tree
        nodes = tree.nodes
        try:
            parent_frame = nodes[top_level_frame]
            display_frame(self, context, nodes, parent_frame)
        except KeyError:
            pass


def display_frame(self, context, nodes: list[Node], frame: NodeFrame) -> None:
    """Recursively display all nodes within a frame, including nodes contained in sub frames.

    Args:
        context (bpy.types.Context): blender context
        nodes (list[Node]): nodes to search within
        frame (bpy.types.NodeFrame): parent node frame.
    """
    children = sorted([n for n in nodes if n.parent ==
                       frame and n.type != 'FRAME'],
                      key=lambda x: x.label)

    frames = sorted([n for n in nodes if n.parent ==
                    frame and n.type == 'FRAME'],
                    key=lambda x: x.label)

    if not frames and children:
        display_framed_nodes(self, context, children)
        return

    subpanel_status = frame.mmm_node_props.subpanel_status

    if children:
        display_subpanel_label(self, subpanel_status, frame)
        if subpanel_status:
            children = [n for n in children if n.type != 'FRAME']
            display_framed_nodes(self, context, children)

        # handles nested frames
        for f in frames:
            if [n for n in nodes if n.parent == f]:
                subpanel_status = f.mmm_node_props.subpanel_status
                display_subpanel_label(self, subpanel_status,  f)
                if subpanel_status:
                    display_frame(self, context,  nodes, f)

    return


def display_subpanel_label(self, subpanel_status: bool, node: Node) -> None:
    """Display a label with a dropdown control for showing and hiding a subpanel.

    Args:
        subpanel_status (Bool): Controls arrow state
        f (bpy.types.Node): Node
    """
    layout = self.layout
    if node.label:
        node_label = node.label
    else:
        node_label = node.name
    row = layout.row()
    icon = 'DOWNARROW_HLT' if subpanel_status else 'RIGHTARROW'
    row.prop(node.mmm_node_props, 'subpanel_status', icon=icon,
             icon_only=True, emboss=False)
    row.label(text=node_label)


def display_framed_nodes(self, context, children: List[Node]) -> None:
    """Display all nodes in a frame.

    Args:
        context (bpy.types.Context): context
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
    """Display node properties in panel.

    Args:
        context (bpy.types.Context): context
        node_label (str): node_label
        node (bpy.types.Node): Node to display.
    """
    if node.type in ('REROUTE', 'FRAME'):
        return
    if node.mmm_node_props.exclude_node:
        return

    layout = self.layout

    if node.type == 'VALUE':
        layout.prop(node.outputs['Value'], 'default_value', text=node_label)
    else:
        layout.label(text=node_label)
        layout.context_pointer_set("node", node)
        if hasattr(node, "draw_buttons_ext"):
            node.draw_buttons_ext(context, layout)
        elif hasattr(node, "draw_buttons"):
            node.draw_buttons(context, layout)

        value_inputs = [
            socket for socket in node.inputs]
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
    """Mod Mod Material Scene Properties.

    Args:
        PropertyGroup (bpy.types.PropertyGroup): PropertyGroup
    """

    def create_geom_frame_enums(self, context):
        enum_items = []
        if context is None:
            return enum_items
        obj = context.object
        mods = context.object.modifiers

        # exposes all nodes in all node modifiers
        node_groups = [
            m.node_group for m in obj.modifiers if m.type == 'NODES']
        nodes = [n for n in node_groups]

    def create_mat_frame_enums(self, context):
        """Return enum list of active material frame nodes that have expose_frame property set to True.

        Args:
            context (bpy.types.Context): blender context

        Returns:
            list(enum_items): enum items.
        """
        enum_items = []
        if context is None:
            return enum_items

        obj = context.object
        mat = obj.active_material
        tree = mat.node_tree
        nodes = tree.nodes

        return self.create_node_enums(nodes, enum_items)

    def create_node_enums(self, nodes, enum_items):
        try:
            frames = sorted([
                n for n in nodes
                if n.type == 'FRAME' and n.mmm_node_props.expose_frame],
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

    mat_top_level_frame: EnumProperty(
        name="Frame",
        items=create_mat_frame_enums,
        description="Any nodes or frames within this frame will be exposed for editing.")

    geom_top_level_frame: EnumProperty(
        name="Frame",
        items=create_geom_frame_enums,
        description="Any nodes or frames within this frame will be exposed for editing."
    )


def register():
    bpy.types.Scene.mmm_scene_props = PointerProperty(
        type=MMM_Scene_Props)


def unregister():
    del bpy.types.Scene.mmm_scene_props
