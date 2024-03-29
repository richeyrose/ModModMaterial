from typing import List
import warnings
import bpy
from bpy.app.handlers import persistent
from bpy.props import PointerProperty, EnumProperty, BoolProperty
from bpy.app.translations import pgettext_iface as iface_
from bpy.types import (
    Panel,
    PropertyGroup,
    Node)
from .lib.utils import get_prefs
import warnings


class NODE_EXPOSE_Enum_Helpers:
    def get_mat_frame_enums(self, context):
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

        enum_items = self.create_frame_enums(nodes, enum_items)
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
                if n.type == 'FRAME' and n.ne_node_props.expose_frame],
                key=lambda n: n.label)
        except KeyError:
            return enum_items

        if not frames:
            enum = ('DUMMY', 'None', "")
            enum_items.append(enum)
            return enum_items

        for frame in frames:
            label = get_node_label(frame)

            enum = (frame.name, label, "")
            enum_items.append(enum)

        return enum_items

    def get_geom_frame_enums(self, context):
        """Return enum list of active geometry frame nodes that have expose_frame property set to True.

        Args:
            context (bpy.types.Context): blender context

        Returns:
            list(enum_items): enum items.
        """
        enum_items = []
        if context is None:
            return enum_items
        try:
            scene_props = context.scene.ne_scene_props
            obj = context.object
            mod = obj.modifiers[scene_props.geom_node_mod]
            nodes = mod.node_group.nodes
            return self.create_frame_enums(nodes, enum_items)
        except KeyError:
            return enum_items

    def get_texture_frame_enums(self, context):
        """Return enum list of active texture frame nodes that have expose_frame property set to True.

        Args:
            context (bpy.types.Context): blender context

        Returns:
            list(enum_items): enum items.
        """
        enum_items = []
        if context is None:
            return enum_items
        try:
            scene_props = context.scene.ne_scene_props
            texture = bpy.data.textures[scene_props.active_texture]
            nodes = texture.node_tree.nodes
            return self.create_frame_enums(nodes, enum_items)
        except (KeyError, AttributeError):
            enum = ('%DUMMY', 'None', '')
            enum_items.append(enum)
            return enum_items

    def get_comp_frame_enums(self, context):
        """Return enum list of active compositor frame nodes that have expose_frame property set to True.

        Args:
            context (bpy.types.Context): blender context

        Returns:
            list(enum_items): enum items.
        """
        enum_items = []
        if context is None:
            return enum_items

        nodes = context.scene.node_tree.nodes
        enum_items = self.create_frame_enums(nodes, enum_items)
        return enum_items


class MatPanel:
    """Contains methods specific to exposing material nodes."""
    @classmethod
    def mat_has_exposed_nodes(cls, context):
        """Check if material has exposed frames.

        Args:
            context (bpy.types.Context): context

        Returns:
            bool: True is material contains exposed frames.
        """
        try:
            for node in context.object.active_material.node_tree.nodes:
                if node.type == 'FRAME' and node.ne_node_props.expose_frame:
                    return True
            return False
        except AttributeError:
            return False

    def draw_material_panel(self, context):
        scene = context.scene
        scene_props = scene.ne_scene_props
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


class NODE_EXPOSE_PT_Material_3D_N_Panel(Panel, MatPanel):
    bl_idname = 'NODE_EXPOSE_PT_Material_3D_N_Panel'
    bl_label = 'Material Nodes'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Node Expose'

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        if prefs.expose_mat_nodes_in_3d_n_panel:
            return cls.mat_has_exposed_nodes(context)
        return False

    def draw(self, context):
        """Draw panel in 3D view

        Args:
            context (bpy.types.Context): Blender context
        """
        self.draw_material_panel(context)


class NODE_EXPOSE_PT_Material_Node_N_Panel(Panel, MatPanel):
    bl_idname = 'NODE_EXPOSE_PT_Material_Node_N_Panel'
    bl_label = 'Material Nodes'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Node Expose'

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        if prefs.expose_mat_nodes_in_node_n_panel:
            return cls.mat_has_exposed_nodes(context)
        return False

    def draw(self, context):
        """Draw panel in node editor

        Args:
            context (bpy.types.Context): Blender context
        """
        self.draw_material_panel(context)


class NODE_EXPOSE_PT_Material_options(Panel, MatPanel):
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
        if prefs.expose_mat_nodes_in_mat_props:
            return cls.mat_has_exposed_nodes(context)
        return False

    def draw(self, context):
        """Draw panel in material properties

        Args:
            context (bpy.types.Context): Blender context
        """
        self.draw_material_panel(context)


class GeomNodes:
    """Contains methods specific to exposing geometry nodes."""
    @classmethod
    def node_mod_has_exposed_nodes(cls, context):
        try:
            mods = context.object.modifiers
            for mod in mods:
                if mod.type == 'NODES':
                    for node in mod.node_group.nodes:
                        if node.type == 'FRAME' and node.ne_node_props.expose_frame:
                            return True
            return False
        except AttributeError:
            return False

    def draw_geom_nodes_panel(self, context):
        scene = context.scene
        scene_props = scene.ne_scene_props
        layout = self.layout

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


class NODE_EXPOSE_PT_Geometry_Nodes_N_Panel(Panel, GeomNodes):
    bl_idname = 'NODE_EXPOSE_PT_Geometry_Nodes_N_Panel'
    bl_label = 'Geometry Nodes'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Node Expose'

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        if prefs.expose_geom_nodes_in_node_n_panel:
            return cls.node_mod_has_exposed_nodes(context)
        return False

    def draw(self, context):
        self.draw_geom_nodes_panel(context)


class NODE_EXPOSE_PT_Geometry_View_3D_N_Panel(Panel, GeomNodes):
    bl_idname = 'NODE_EXPOSE_PT_Geometry_View_3D_N_Panel'
    bl_label = 'Geometry Nodes'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Node Expose'

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        if prefs.expose_geom_nodes_in_3d_n_panel:
            return cls.node_mod_has_exposed_nodes(context)
        return False

    def draw(self, context):
        layout = self.layout
        layout.label(text="Node Modifier")
        layout.prop(context.scene.ne_scene_props, 'geom_node_mod', text='')
        self.draw_geom_nodes_panel(context)


class CompositorNodes(NODE_EXPOSE_Enum_Helpers):
    @classmethod
    def comp_has_exposed_nodes(cls, context):
        try:
            for node in context.scene.node_tree.nodes:
                if node.type == 'FRAME' and node.ne_node_props.expose_frame:
                    return True
            return False
        except AttributeError:
            return False

    def draw_comp_nodes_panel(self, context):
        scene = context.scene
        scene_props = scene.ne_scene_props
        layout = self.layout

        if scene_props.comp_top_level_frame:
            layout.label(text="Top Level Frame")
            layout.prop(scene_props, 'comp_top_level_frame', text='')
            layout.separator()
            top_level_frame = scene_props.comp_top_level_frame

            comp_nodes = scene.node_tree.nodes
            try:
                display_frame(self, context, comp_nodes,
                              comp_nodes[top_level_frame], top_level_frame)
            except KeyError:
                pass


class NODE_EXPOSE_PT_Compositor_View_3D_N_Panel(Panel, CompositorNodes):
    bl_idname = 'NODE_EXPOSE_PT_Compositor_View_3D_N_Panel'
    bl_label = 'Compositor Nodes'
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'
    bl_category = 'Node Expose'

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        if prefs.expose_comp_nodes_in_3d_n_panel:
            return cls.comp_has_exposed_nodes(context)
        return False

    def draw(self, context):
        self.draw_comp_nodes_panel(context)


class NODE_EXPOSE_PT_Compositor_Nodes_N_Panel(Panel, CompositorNodes):
    bl_idname = 'NODE_EXPOSE_PT_Compositor_Nodes_N_Panel'
    bl_label = 'Compositor Nodes'
    bl_region_type = 'UI'
    bl_space_type = 'NODE_EDITOR'
    bl_category = 'Node Expose'

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        if prefs.expose_comp_nodes_in_node_n_panel:
            return cls.comp_has_exposed_nodes(context)
        return False

    def draw(self, context):
        self.draw_comp_nodes_panel(context)


class TextureNodes:
    @classmethod
    def texture_has_exposed_nodes(cls, context):
        try:
            textures = bpy.data.textures
            for texture in textures:
                for node in texture.node_tree.nodes:
                    if node.type == 'FRAME' and node.ne_node_props.expose_frame:
                        return True
            return False
        except AttributeError:
            return False

    def draw_texture_nodes_panel(self, context):
        scene = context.scene
        scene_props = scene.ne_scene_props
        layout = self.layout

        layout.label(text="Texture")
        layout.prop(scene_props, 'active_texture', text='')

        if scene_props.active_texture and scene_props.texture_top_level_frame:
            layout.label(text="Top Level Frame")
            layout.prop(scene_props, 'texture_top_level_frame', text='')
            layout.separator()

            top_level_frame = scene_props.texture_top_level_frame
            try:
                nodes = bpy.data.textures[scene_props.active_texture].node_tree.nodes

                display_frame(self, context, nodes,
                              nodes[top_level_frame], top_level_frame)
            except (KeyError, AttributeError):
                pass


class NODE_EXPOSE_PT_Texture_Nodes_N_Panel(Panel, TextureNodes):
    bl_idname = 'NODE_EXPOSE_PT_Texture_Nodes_N_Panel'
    bl_label = 'Texture Nodes'
    bl_region_type = 'UI'
    bl_space_type = 'NODE_EDITOR'
    bl_category = 'Node Expose'

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        if prefs.expose_texture_nodes_in_node_n_panel:
            return cls.texture_has_exposed_nodes(context)
        return False

    def draw(self, context):
        self.draw_texture_nodes_panel(context)


class NODE_EXPOSE_PT_Texture_View_3D_N_Panel(Panel, TextureNodes):
    bl_idname = 'NODE_EXPOSE_PT_Texture_View_3D_N_Panel'
    bl_label = 'Texture Nodes'
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'
    bl_category = 'Node Expose'

    @classmethod
    def poll(cls, context):
        prefs = get_prefs()
        if prefs.expose_texture_nodes_in_node_n_panel:
            return cls.texture_has_exposed_nodes(context)
        return False

    def draw(self, context):
        self.draw_texture_nodes_panel(context)


def display_frame(self, context, nodes, frame, top_level_frame=None) -> None:
    """Recursively display all nodes within a frame, including nodes contained in sub frames.

    Args:
        context (bpy.types.Context): blender context
        nodes (list[Node]): nodes to search within
        frame (bpy.types.NodeFrame): parent node frame.
        top_level_frame(bpy.types.NodeFrame): grandparent frame to stop at
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

    subpanel_status = frame.ne_node_props.subpanel_status

    if children:
        children = [n for n in children if n.type != 'FRAME']
        display_framed_nodes(self, context, children, top_level_frame)

    # handles nested frames
    for f in frames:
        if [n for n in nodes if n.parent == f]:
            subpanel_status = f.ne_node_props.subpanel_status
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
    if num_ancestors(node, top_level_frame):
        inset = " " * num_ancestors(node)
        row.label(text=inset)
    row.prop(node.ne_node_props, 'subpanel_status', icon=icon,
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


def num_ancestors(node, top_level_frame=None, ancestors=0):
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


def split_col(node, top_level_frame):
    """Calculate how many times to split a panel column based on number of ancestors for drawing drop down.

    Args:
        node (bpy.types.Node): node
        top_level_frame (_type_): grandparent frame

    Returns:
        int: num times to split column
    """
    if num_ancestors(node, top_level_frame) == 0:
        return 1
    else:
        return num_ancestors(node, top_level_frame)


def display_node(self, context, node_label, node, top_level_frame=None) -> None:
    """Display node properties in panel.

    Args:
        context (bpy.types.Context): context
        node_label (str): node_label
        node (bpy.types.Node): Node to display.
    """
    if node.type in ('REROUTE', 'FRAME'):
        return
    if node.ne_node_props.exclude_node:
        return

    layout = self.layout

    if node.type == 'VALUE':
        row = layout.row()
        ancestors = num_ancestors(node, top_level_frame)

        if ancestors >= 1:
            row = row.split(factor=0.1 * split_col(node, top_level_frame))
            inset = " " * ancestors
            row.label(text=inset)
        row.prop(node.outputs['Value'], 'default_value', text=node_label)
    else:
        subpanel_status = node.ne_node_props.subpanel_status
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
                row = layout.row()
                row.label(text="Inputs:")

                for socket in value_inputs:
                    row = layout.row()
                    socket.draw(
                        context,
                        row,
                        node,
                        iface_(socket.label if socket.label else socket.name,
                               socket.bl_rna.translation_context),
                    )


class NODE_EXPOSE_PT_Node_Options(Panel):
    bl_idname = 'NODE_EXPOSE_PT_Node_Options'
    bl_label = 'Node options'
    bl_category = 'Node'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'Expose Nodes'

    @classmethod
    def poll(cls, context):
        return context.active_node is not None

    def draw(self, context):
        layout = self.layout
        node = context.active_node
        if node.type == 'FRAME':
            layout.prop(node.ne_node_props, 'expose_frame')

        if node.type != 'FRAME':
            layout.prop(node.ne_node_props, 'exclude_node')


class NODE_EXPOSE_Node_Props(PropertyGroup, NODE_EXPOSE_Enum_Helpers):
    """Node Expose Node Properties.

    Args:
        PropertyGroup (bpy.types.PropertyGroup): PropertyGroup
    """

    def update_frame_enums(self, context):
        tree_type = type(self.id_data)
        if tree_type == bpy.types.CompositorNodeTree:
            comp_enums = self.get_comp_frame_enums(context)
            if comp_enums:
                context.scene.ne_scene_props.comp_top_level_frame = comp_enums[0][0]
        elif tree_type == bpy.types.ShaderNodeTree:
            mat_enums = self.get_mat_frame_enums(context)
            if mat_enums:
                context.scene.ne_scene_props.mat_top_level_frame = mat_enums[0][0]
        elif tree_type == bpy.types.GeometryNodeTree:
            geom_enums = self.get_geom_frame_enums(context)
            if geom_enums:
                context.scene.ne_scene_props.geom_top_level_frame = geom_enums[0][0]
        elif tree_type == bpy.types.TextureNodeTree:
            texture_enums = self.get_texture_frame_enums(context)
            if texture_enums:
                context.scene.ne_scene_props.texture_top_level_frame = texture_enums[0][0]

    exclude_node: BoolProperty(
        name="Exclude Node",
        description="Don't show this node in UI.",
        default=False)

    subpanel_status: BoolProperty(
        name="Show Subpanel",
        default=True)

    expose_frame: BoolProperty(
        name="Expose Frame",
        description="Expose frame and nodes?",
        default=False,
        update=update_frame_enums)


class NODE_EXPOSE_Scene_Props(PropertyGroup, NODE_EXPOSE_Enum_Helpers):
    """Node Expose Scene Properties.

    Args:
        PropertyGroup (bpy.types.PropertyGroup): PropertyGroup
    """

    def create_mat_frame_enums(self, context):
        return self.get_mat_frame_enums(context)

    def create_geom_frame_enums(self, context):
        return self.get_geom_frame_enums(context)

    def create_comp_frame_enums(self, context):
        return self.get_comp_frame_enums(context)

    def create_texture_frame_enums(self, context):
        return self.get_texture_frame_enums(context)

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
        for mod in mods:
            nodes = mod.node_group.nodes
            frames = [f for f in nodes if f.type ==
                      'FRAME' and f.ne_node_props.expose_frame]
            if frames:
                enum = (mod.name, mod.name, "")
                enum_items.append(enum)
        if not enum_items:
            enum = ('%DUMMY', "None", "")
            enum_items.append(enum)

        return enum_items

    def create_texture_enums(self, context):
        """Return enum list of textures.

        Args:
            context (bpy.types.Context): context

        Returns:
            list(enum_items): enum items
        """
        enum_items = []
        if context is None:
            return enum_items

        textures = bpy.data.textures

        for texture in textures:
            if hasattr(texture.node_tree, 'nodes'):
                enum = (texture.name, texture.name, "")
                enum_items.append(enum)
        if not enum_items:
            enum = ('%DUMMY', "None", "")
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

    comp_top_level_frame: EnumProperty(
        name="Frame",
        items=create_comp_frame_enums,
        description="Any nodes or frames within this frame will be exposed for editing."
    )

    texture_top_level_frame: EnumProperty(
        name="Frame",
        items=create_texture_frame_enums,
        description="Any nodes or frames within this frame will be exposed for editing."
    )

    geom_node_mod: EnumProperty(
        name="Modifier",
        items=create_geom_node_mod_enums,
        description="Geometry node modifier to expose."
    )

    active_texture: EnumProperty(
        name="Texture",
        items=create_texture_enums,
        description="Textures"
    )


@persistent
def update_enums(dummy):
    """If necessary resets enums on depsgraph update.

    Args:
        dummy (any): dummy variable
    """
    context = bpy.context
    scene = context.scene
    scene_props = scene.ne_scene_props
    try:
        comp_nodes = context.scene.node_tree.nodes

        comp_frames = sorted([
            n for n in comp_nodes
            if n.type == 'FRAME' and n.ne_node_props.expose_frame],
            key=lambda n: n.label)

        if comp_frames:
            comp_tlf = scene_props.comp_top_level_frame
            if comp_tlf not in [f.name for f in comp_frames]:
                context.scene.ne_scene_props.comp_top_level_frame = comp_frames[0].name
    except (AttributeError, KeyError):
        pass
    try:
        mat_nodes = context.object.active_material.node_tree.nodes
        mat_frames = sorted([
            n for n in mat_nodes
            if n.type == 'FRAME' and n.ne_node_props.expose_frame],
            key=lambda n: n.label)

        if mat_frames:
            mat_tlf = scene_props.mat_top_level_frame
            if mat_tlf not in [f.name for f in mat_frames]:
                context.scene.ne_scene_props.mat_top_level_frame = mat_frames[0].name
    except(AttributeError, KeyError):
        pass
    try:
        obj = context.object
        mods = sorted([m.name for m in obj.modifiers if m.type ==
                       'NODES'], key=lambda m: m.name)

        for mod in mods:
            frames = [f for f in mod.node_group.nodes if f.type == 'FRAME']
            if not frames:
                mods.remove(mod)
        if mods:
            geom_node_mod = scene_props.geom_node_mod
            if geom_node_mod not in mods:
                context.scene.ne_scene_props.geom_node_mod = mods[0].name
    except(AttributeError, KeyError):
        pass
    try:
        geom_nodes = context.object.modifiers[scene_props.geom_node_mod].node_group.nodes
        geom_frames = sorted([
            n for n in geom_nodes
            if n.type == 'FRAME' and n.ne_node_props.expose_frame],
            key=lambda n: n.label)

        if geom_frames:
            geom_tlf = scene_props.geom_top_level_frame
            if geom_tlf not in [f.name for f in geom_frames]:
                context.scene.ne_scene_props.geom_top_level_frame = geom_frames[0].name
    except(AttributeError, KeyError):
        pass
    try:
        texture_nodes = bpy.data.textures[scene_props.active_texture].node_tree.nodes
        texture_frames = sorted([
            n for n in texture_nodes
            if n.type == 'FRAME' and n.ne_node_props.expose_frame],
            key=lambda n: n.label)

        if texture_frames:
            texture_tlf = scene_props.texture_top_level_frame
            if texture_tlf not in [f.name for f in texture_frames]:
                context.scene.ne_scene_props.texture_top_level_frame = texture_frames[0].name
    except (AttributeError, KeyError):
        pass


bpy.app.handlers.depsgraph_update_pre.append(update_enums)


def register():
    bpy.types.Scene.ne_scene_props = PointerProperty(
        type=NODE_EXPOSE_Scene_Props)
    bpy.types.Node.ne_node_props = PointerProperty(
        type=NODE_EXPOSE_Node_Props)


def unregister():
    del bpy.types.Node.ne_node_props
    del bpy.types.Scene.ne_scene_props
