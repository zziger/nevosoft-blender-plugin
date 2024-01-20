import bpy

class ImportSkeletonSettings:
    load_at_0z: bpy.props.BoolProperty(
        name="Load at height 0",
        description="Move skeleton's root bone to height 0",
        default=True,
    ) = True