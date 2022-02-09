import bpy
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, PointerProperty


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
                if n.type == 'FRAME'],
                key=lambda n: n.label)
        except KeyError:
            return enum_items

        if not frames:
            return enum_items

        for frame in frames:
            # Only display frames which contain editable nodes
            children = sorted([n for n in nodes if n.parent ==
                               frame and n.type in ['VALUE', 'FRAME']], key=lambda x: x.label)

            if children:
                if frame.label:
                    label = frame.label
                else:
                    label = frame.name
                enum = (frame.name, label, "")
                enum_items.append(enum)

            for i, enum in enumerate(enum_items):
                if enum[0] == 'editable_inputs':
                    enum_items.insert(0, enum_items.pop(i))

        return enum_items

    top_level_frame: EnumProperty(
        name="Frame",
        items=create_frame_enums,
        description="Any nodes or frames within this frame will be exposed for editing.")


def register():
    bpy.types.Scene.mmm_scene_props = PointerProperty(
        type=MMM_Scene_Props)


def unregister():
    del bpy.types.Scene.mmm_scene_props
