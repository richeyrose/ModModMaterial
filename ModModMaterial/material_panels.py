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
                display_framed_nodes(self, nodes, parent_frame)
            except KeyError:
                pass


def get_nodes_of_type(self, nodes, parent, type):
    nodes = [n for n in nodes if n.parent == parent and n.type == type]
    return sorted(nodes, key=lambda n: n.label)


def display_framed_nodes(self, nodes, parent):
    """Display all nodes within a frame, including nodes contained in sub frames.

    Args:
        nodes (bpy_prop_collection): nodes to search within
        parent (bpy.types.NodeFrame): parent node frame.
    """
    children = [n for n in nodes if n.parent ==
                parent and n.type != 'FRAME']
    frames = [n for n in nodes if n.parent == parent and n.type == 'FRAME']
    layout = self.layout
    if not frames:
        layout.label(text=parent.label)
        for child in children:
            layout.prop(child.outputs['Value'],
                        'default_value', text=child.label)
        return

    # handles nested frames
    for frame in frames:
        display_framed_nodes(self, nodes, frame)

    # handles cases where there are both frames and nodes in a frame
    if children:
        layout.label(text=parent.label)
        for child in children:
            if child.type != 'FRAME':
                layout.prop(child.outputs['Value'],
                            'default_value', text=child.label)
    return
