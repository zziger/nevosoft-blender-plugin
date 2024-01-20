import bpy

from .BaseSettingsPanel import BaseSettingsPanel

class AnimationSettingsPanel(bpy.types.Panel, BaseSettingsPanel):
    bl_idname = 'FILE_PT_nevosoft_animation_settings'
    bl_order = 1
    bl_label = "Animation settings"

    @classmethod
    def match_operator(cls, operator):
        return operator.bl_idname == "NEVOSOFT_OT_import_animation" or operator.bl_idname == "NEVOSOFT_OT_export_animation"
    
    def draw_settings(self, context, layout, operator):
        layout.prop(operator, 'bone_rotations')

        col = layout.column()
        split = col.split()
        sub = split.column()
        row = sub.row()
        row.label(text="Axis")

        subrow = row.row(align=True)
        subrow.prop(operator, 'location_x', text="X", toggle=True)
        subrow.prop(operator, 'location_y', text="Y", toggle=True)
        subrow.prop(operator, 'location_z', text="Z", toggle=True)
