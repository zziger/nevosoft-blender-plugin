import bpy

class BakeSettings:
    bake_materials: bpy.props.BoolProperty(
        name="Bake materials",
        description="Bake materials instead of searching for texture",
        default=False,
    ) = False