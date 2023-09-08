import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.MshFile import MshFile


class ExportMeshOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ExportHelper):
    bl_idname = "nevosoft.export_mesh"
    bl_label = "Nevosoft mesh (.msh)"
    bl_action = "export"
    bl_showtime = True
    bl_update_view = True
    check_extension = True
    filename_ext = ".msh"

    def execute(self, context):
        try:
            if bpy.context.active_object is None:
                raise Exception("No active object found")

            MshFile.write(bpy.context.active_object, self.filepath)
            self.message(f"Mesh exported successfully")
        except Exception as e:
            self.error(str(e))
            traceback.print_exception(e)
        return {'FINISHED'}

    @staticmethod
    def load():
        bpy.utils.register_class(ExportMeshOperator)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ExportMeshOperator)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


def menu_func_export(self, context):
    self.layout.operator(ExportMeshOperator.bl_idname, text=ExportMeshOperator.bl_label)
