import bpy

def register():
    bpy.types.EditBone.tag = bpy.props.IntProperty(name="Bone ID", default=-1, min=-1)