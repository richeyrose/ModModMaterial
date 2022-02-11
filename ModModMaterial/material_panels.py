from bpy.types import Panel


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


def create_nodes_panel(self, nodes, parent):
    """Display all nodes within a frame, including nodes contained in sub frames.

    Args:
        nodes (bpy_prop_collection): nodes to search within
        parent (bpy.types.NodeFrame): parent node frame.
    """
    children = [n for n in nodes if n.parent ==
                parent and n.type != 'FRAME']

    frames = sorted([n for n in nodes if n.parent ==
                    parent and n.type == 'FRAME'],
                    key=lambda x: x.label)

    if not frames:
        display_framed_nodes(self, parent, children)
        return

    # handles nested frames
    for frame in frames:
        create_nodes_panel(self, nodes, frame)

    if children:
        children = [n for n in children if n.type != 'FRAME']
        display_framed_nodes(self, parent, children)
    return


def display_framed_nodes(self, frame, children):
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

        if child.type == 'VALUE':
            layout.prop(child.outputs['Value'],
                        'default_value', text=child_label)
        elif child.type == 'GROUP':
            display_group_inputs(self, child, child_label)

        # Curves
        elif child.type == 'CURVE_VEC':
            layout.label(text=child_label)
            layout.template_curve_mapping(
                child, 'mapping')
        elif child.type == 'CURVE_FLOAT':
            layout.label(text=child_label)
            layout.template_curve_mapping(
                child, 'mapping')
        elif child.type == 'CURVE_RGB':
            layout.label(text=child_label)
            layout.template_curve_mapping(
                child, 'mapping')

        # Color
        elif child.type == 'VALTORGB':  # Color ramp
            layout.label(text=child_label)
            layout.template_color_ramp(child, 'color_ramp', expand=True)
        elif child.type == 'RGB':
            layout.label(text=child_label)
            layout.template_color_picker(child, 'color', value_slider=True)

        # texture
        elif child.type == 'TEX_IMAGE':
            display_img_tex_node(self, child, child_label)


def display_img_tex_node(self, node, node_label):
    layout = self.layout
    layout.label(text=node_label)
    layout.template_ID(node, "image", new="image.new", open="image.open")
    layout.prop(node, "interpolation", text="")
    layout.prop(node, "projection", text="")
    if node.projection == 'BOX':
        layout.prop(node, "projection_blend", text="")
    layout.prop(node, "extension", text="")


def display_group_inputs(self, node, node_label):
    """Display all empty inputs in a group.

    Args:
        node (bpy.types.ShaderNodeGroup): Group Node
    """
    inputs = [i for i in node.inputs if not i.links]

    if inputs:
        layout = self.layout
        layout.label(text=node_label)

        for i in inputs:
            if i.label:
                input_label = i.label
            else:
                input_label = i.name
            layout.prop(i, 'default_value', text=input_label)
