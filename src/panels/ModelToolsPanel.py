import bpy

class ModelTools(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_nevosoft_tools'
    bl_label = 'Tools'
    bl_context = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS' if bpy.app.version < (2, 80, 0) else 'UI'
    bl_category = 'Nevosoft'

    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Replace model rest pose:")
        layout.operator("nevosoft.retarget_animations")
        layout.operator("nevosoft.retarget_model")

        layout.label(text="Bone utils:")
        layout.operator("nevosoft.fix_bone_ids")
        layout.operator("nevosoft.place_skeleton_on_ground")
