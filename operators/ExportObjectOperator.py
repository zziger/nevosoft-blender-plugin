import traceback

import bpy
import bpy_extras
from bpy.props import BoolProperty
from bpy.types import Panel

from ..helpers import OperatorBase
from ..structures.CgoFile import CgoFile


class ExportObjectOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ExportHelper):
    bl_idname = "nevosoft.export_object"
    bl_label = "Nevosoft object (.cgo)"
    bl_action = "export"
    bl_showtime = True
    bl_update_view = True
    check_extension = True
    filename_ext = ".cgo"

    def execute(self, context):
        try:
            if bpy.context.scene is None:
                raise Exception("No scene found")

            CgoFile.write(self.filepath, bpy.context.scene, self.bake_materials)
            self.message(f"Object exported successfully")
        except Exception as e:
            self.error(str(e))
            traceback.print_exception(e)
        return {'FINISHED'}

    bake_materials: BoolProperty(
        name="Bake materials",
        description="Bake materials instead of searching for texture",
        default=False,
    )

    def draw(self, context):
        pass

    @staticmethod
    def load():
        bpy.utils.register_class(ExportObjectOperator)
        bpy.utils.register_class(CUSTOM_PT_object_export_settings)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ExportObjectOperator)
        bpy.utils.unregister_class(CUSTOM_PT_object_export_settings)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


def menu_func_export(self, context):
    self.layout.operator(ExportObjectOperator.bl_idname, text=ExportObjectOperator.bl_label)


class CUSTOM_PT_object_export_settings(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Export settings"

    @classmethod
    def poll(cls, context):
        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return False

        operator = context.space_data.active_operator
        return operator.bl_idname == "NEVOSOFT_OT_export_object"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return

        operator = context.space_data.active_operator
        layout.prop(operator, 'bake_materials')
