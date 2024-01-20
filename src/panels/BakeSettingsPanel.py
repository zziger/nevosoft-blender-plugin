import bpy

from .BaseSettingsPanel import BaseSettingsPanel

class BakeSettingsPanel(bpy.types.Panel, BaseSettingsPanel):
    bl_idname = 'FILE_PT_nevosoft_bake_settings'
    bl_order = 1
    bl_label = "Material settings"

    @classmethod
    def match_operator(cls, operator):
        return operator.bl_idname == "NEVOSOFT_OT_export_character" or operator.bl_idname == "NEVOSOFT_OT_export_object"
    
    def draw_settings(self, context, layout, operator):
        layout.prop(operator, 'bake_materials')
