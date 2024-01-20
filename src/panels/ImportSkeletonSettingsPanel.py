import bpy

from .BaseSettingsPanel import BaseSettingsPanel

class ImportSkeletonSettingsPannel(bpy.types.Panel, BaseSettingsPanel):
    bl_idname = 'FILE_PT_nevosoft_import_skeleton_settings'
    bl_order = 1
    bl_label = "Skeleton settings"

    @classmethod
    def match_operator(cls, operator):
        return \
            operator.bl_idname == "NEVOSOFT_OT_import_character" or \
            operator.bl_idname == "NEVOSOFT_OT_import_skeleton" or \
            operator.bl_idname == "NEVOSOFT_OT_import_simplified_character" or \
            operator.bl_idname == "NEVOSOFT_OT_import_simplified_skeleton"
    
    def draw_settings(self, context, layout, operator):
        layout.prop(operator, 'load_at_0z')
