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
    bl_label = 'Material Nodes'
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


class NODE_EXPOSE_PT_Material_options(Panel):
    bl_idname = 'NODE_EXPOSE_PT_Material_Options'
    bl_label = 'Material Nodes'
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
    bl_label = 'Geometry Nodes'
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

        layout.label(text="Node Modifier")
        layout.prop(scene_props, 'geom_node_mod', text='')

        if scene_props.geom_top_level_frame:
            layout.label(text="Top Level Frame")
            layout.prop(scene_props, 'geom_top_level_frame', text='')
            layout.separator()
            top_level_frame = scene_props.geom_top_level_frame

            obj = context.object
            mod = obj.modifiers[scene_props.geom_node_mod]
            nodes = mod.node_group.nodes
            try:
                display_frame(self, context, nodes,
                              nodes[top_level_frame], top_level_frame)
            except KeyError:
                pass


def mat_has_exposed_nodes(context):
    """Check if material has exposed frames.

    Args:
        context (bpy.types.Context): context

    Returns:
        bool: True is material contains exposed frames.
    """
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
            display_frame(self, context, nodes,
                          nodes[top_level_frame], top_level_frame)
        except KeyError:
            pass


def display_frame(self, context, nodes: list[Node], frame: NodeFrame, top_level_frame=None) -> None:
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
        display_framed_nodes(self, context, children, top_level_frame)
        return

    subpanel_status = frame.mmm_node_props.subpanel_status

    if children:
        children = [n for n in children if n.type != 'FRAME']
        display_framed_nodes(self, context, children, top_level_frame)

        # handles nested frames
        for f in frames:
            if [n for n in nodes if n.parent == f]:
                subpanel_status = f.mmm_node_props.subpanel_status
                display_subpanel_label(
                    self, subpanel_status,  f, top_level_frame)
                if subpanel_status:
                    display_frame(self, context,  nodes,
                                  f, top_level_frame)

    return


def display_subpanel_label(self, subpanel_status: bool, node: Node, top_level_frame=None) -> None:
    """Display a label with a dropdown control for showing and hiding a subpanel.

    Args:
        subpanel_status (Bool): Controls arrow state
        f (bpy.types.Node): Node
    """
    layout = self.layout
    icon = 'DOWNARROW_HLT' if subpanel_status else 'RIGHTARROW'
    node_label = get_node_label(node)
    row = layout.row()
    row.alignment = 'LEFT'
    ancestors = num_ancestors(node, top_level_frame)
    if node.parent:
        i = 0
        while i < ancestors:
            row.label(text=' ')
            i += 1
    row.prop(node.mmm_node_props, 'subpanel_status', icon=icon,
             icon_only=True, emboss=False)
    row.label(text=node_label)


def get_node_label(node):
    """Return node label if there is one, else return node name.

    Args:
        node (bpy.types.Node): Node

    Returns:
        str: Node label
    """
    if node.label and not node.label.isspace():
        return node.label
    else:
        return node.name


def num_ancestors(node, top_level_frame, ancestors=0):
    """Return number of ancestor of a node.

    Args:
        node (bpy.types.Node): node
        ancestors (int, optional): Num ancestors. Defaults to 0.

    Returns:
        int: num ancestors
    """
    if not node.parent:
        return ancestors
    elif node.parent.name == top_level_frame:
        return 0
    if node.parent:
        ancestors = num_ancestors(node.parent, top_level_frame, ancestors) + 1
    return ancestors


def display_framed_nodes(self, context, children: List[Node], top_level_frame=None) -> None:
    """Display all nodes in a frame.

    Args:
        context (bpy.types.Context): context
        children (list): List of child nodes
    """

    layout = self.layout

    for child in children:
        child_label = get_node_label(child)
        try:
            display_node(self, context, child_label, child, top_level_frame)
        # catch unsupported node types
        except TypeError:
            layout.label(text=child_label)
            layout.label(text="Node type not supported.")


def display_node(self, context, node_label, node, top_level_frame=None) -> None:
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
        subpanel_status = node.mmm_node_props.subpanel_status
        display_subpanel_label(self, subpanel_status, node, top_level_frame)
        if subpanel_status:
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

        scene_props = context.scene.mmm_scene_props
        obj = context.object
        mod = obj.modifiers[scene_props.geom_node_mod]
        nodes = mod.node_group.nodes
        return self.create_frame_enums(nodes, enum_items)

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

        return self.create_frame_enums(nodes, enum_items)

    def create_geom_node_mod_enums(self, context):
        """Return enum list of geometry node modifiers of active object
        that contain a frame with expose_frame property set to true.

        Args:
            context (bpy.types.Context): Blender Context

        Returns:
            list(enum_items): enum items
        """
        enum_items = []
        if context is None:
            return enum_items

        obj = context.object
        mods = sorted([m for m in obj.modifiers if m.type ==
                      'NODES'], key=lambda m: m.name)

        mods = set(
            mod
            for mod in obj.modifiers
            if mod.type == 'NODES'
            for node in mod.node_group.nodes
            if node.type == 'FRAME' and node.mmm_node_props.expose_frame)

        for mod in mods:
            enum = (mod.name, mod.name, "")
            enum_items.append(enum)
        return enum_items

    def create_frame_enums(self, nodes, enum_items):
        """Return enum list of frame nodes where expose_frame property is set to true.

        Args:
            nodes (list(bpy.types.Node)): list of nodes
            enum_items (list(enum_items)): list of enum items

        Returns:
            list(enum_items): emu items
        """
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
            label = get_node_label(frame)

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

    geom_node_mod: EnumProperty(
        name="Modifier",
        items=create_geom_node_mod_enums,
        description="Geometry node modifier to expose."
    )


def register():
    bpy.types.Scene.mmm_scene_props = PointerProperty(
        type=MMM_Scene_Props)


def unregister():
    del bpy.types.Scene.mmm_scene_props
