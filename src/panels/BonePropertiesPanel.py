import bpy

class BoneProperties(bpy.types.Panel):
    bl_label = "Nevosoft"
    bl_idname = "BONE_PT_nevosoft"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "bone"

    @classmethod
    def poll(cls, context):
        return context.active_bone is not None

    def draw(self, context: bpy.types.Context):
        bone = context.active_bone
        layout = self.layout

        row = layout.row()
        row.prop(bone, "tag")
