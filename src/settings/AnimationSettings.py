import bpy

class AnimationSettings:
    bone_rotations: bpy.props.BoolProperty(
        name="Bone rotations",
        description="Export/import bone rotations",
        default=True,
    ) = True

    location_x: bpy.props.BoolProperty(
        name="Location X",
        description="Export/import model transform on X axis",
        default=True,
        options={'HIDDEN'}
    ) = True

    location_y: bpy.props.BoolProperty(
        name="Location Y",
        description="Export/import model transform on Y axis",
        default=True,
        options={'HIDDEN'}
    ) = True

    location_z: bpy.props.BoolProperty(
        name="Location Z",
        description="Export/import model transform on Z axis",
        default=True,
        options={'HIDDEN'}
    ) = True
