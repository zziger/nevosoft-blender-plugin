import bpy
from ..preferences import get_preferences
from ..helpers import get_bone_properties

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

        properties = get_bone_properties(bone)
        # row = layout.row()
        layout.prop(properties, "tag")
        layout.operator('nevosoft.assign_bone_id', text="Assign new ID")

        if get_preferences().debug:
            layout.label(text="Data block version: " + str(properties.data_ver))
