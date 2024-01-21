import bpy

class BoneProperties(bpy.types.PropertyGroup):
    data_ver: bpy.props.IntProperty(name="Data version", default=1, options={'HIDDEN'})
    tag: bpy.props.IntProperty(name="Bone ID", default=-1, min=-1, options={'HIDDEN'})

    def update():
        pass

def register():
    bpy.types.EditBone.nevosoft = bpy.types.Bone.nevosoft = bpy.props.PointerProperty(name="Nevosoft Bone properties", type=BoneProperties, options={'HIDDEN'})