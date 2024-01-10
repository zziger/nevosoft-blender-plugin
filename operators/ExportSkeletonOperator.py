import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.SklFile import SklFile


class ExportSkeletonOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ExportHelper):
    bl_idname = "nevosoft.export_skeleton"
    bl_label = "Nevosoft Skeleton (.skl)"
    bl_action = "export"
    bl_showtime = True
    bl_update_view = True
    check_extension = True
    filename_ext = ".skl"

    def execute(self, context):
        try:
            if bpy.context.active_object is None:
                raise Exception("No active object found")

            SklFile.write(bpy.context.active_object, self.filepath)
            self.message(f"Skeleton exported successfully")
        except Exception as e:
            self.error(str(e))
            traceback.print_exception(e)
        return {'FINISHED'}

    @staticmethod
    def load():
        bpy.utils.register_class(ExportSkeletonOperator)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ExportSkeletonOperator)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


def menu_func_export(self, context):
    self.layout.operator(ExportSkeletonOperator.bl_idname, text=ExportSkeletonOperator.bl_label, icon="ARMATURE_DATA")
