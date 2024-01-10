import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.AnmFile import AnmFile


class ExportAnimationOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ExportHelper):
    bl_idname = "nevosoft.export_animation"
    bl_label = "Nevosoft Animation (.anm)"
    bl_action = "export"
    bl_showtime = True
    bl_update_view = True
    check_extension = True
    filename_ext = ".anm"

    def execute(self, context):
        try:
            if bpy.context.active_object is None:
                raise Exception("No active object found")

            anm = AnmFile.fromObject(bpy.context.active_object)
            anm.write(self.filepath)
            self.message(f"Animation was exported successfully")
        except Exception as e:
            self.error(str(e))
            traceback.print_exception(e)
        return {'FINISHED'}

    @staticmethod
    def load():
        bpy.utils.register_class(ExportAnimationOperator)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ExportAnimationOperator)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


def menu_func_export(self, context):
    self.layout.operator(ExportAnimationOperator.bl_idname, text=ExportAnimationOperator.bl_label, icon="ANIM")
