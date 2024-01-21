import bpy

class ModelToolsSkeleton(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_nevosoft_tools_skeleton'
    bl_label = 'Skeleton tools'
    bl_order = 0
    bl_context = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS' if bpy.app.version < (2, 80, 0) else 'UI'
    bl_category = 'Nevosoft'

    def draw(self, context):
        layout = self.layout
        
        layout.operator("nevosoft.fix_bone_ids")
        layout.operator("nevosoft.place_skeleton_on_ground")

class ModelToolsRetarget(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_nevosoft_tools_retarget'
    bl_label = 'Retarget skeleton rest pose'
    bl_order = 1
    bl_context = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS' if bpy.app.version < (2, 80, 0) else 'UI'
    bl_category = 'Nevosoft'

    def draw(self, context):
        layout = self.layout
        
        layout.operator("nevosoft.retarget_animations")
        layout.operator("nevosoft.retarget_model")
        layout.operator("nevosoft.import_animation_batch")
        layout.operator("nevosoft.export_animation_batch")
        layout.operator("nevosoft.reapply_animation_batch_location")
