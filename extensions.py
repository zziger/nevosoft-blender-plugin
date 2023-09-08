import bpy

class BoneProperties(bpy.types.Panel):
    bl_label = "Nevosoft"
    bl_idname = "BONE_PT_nevosoft"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "bone"

    @staticmethod
    def load():
        bpy.types.EditBone.tag = bpy.props.IntProperty(name="Bone tag", description="amogus sus", default=-1, min=0)
        bpy.utils.register_class(BoneProperties)

    @classmethod
    def poll(cls, context):
        return context.active_bone is not None

    def draw(self, context: bpy.types.Context):
        bone = context.active_bone
        layout = self.layout

        row = layout.row()
        row.prop(bone, "tag")
