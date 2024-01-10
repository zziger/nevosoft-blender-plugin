from pathlib import Path
import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile


class ImportAnimationOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper):
    bl_idname = "nevosoft.import_animation"
    bl_label = "Nevosoft Animation (.anm)"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.anm',
        options={'HIDDEN'}
    )

    def execute(self, context):
        try:
            anm = AnmFile.read(self.filepath)
            anm.create(bpy.context.active_object)
            self.message("Animation imported successfully")
        except Exception as e:
            self.error(str(e))
            traceback.print_exception(e)
        return {'FINISHED'}

    @staticmethod
    def load():
        bpy.utils.register_class(ImportAnimationOperator)
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ImportAnimationOperator)
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


def menu_func_import(self, context):
    self.layout.operator(ImportAnimationOperator.bl_idname, text=ImportAnimationOperator.bl_label, icon="ANIM")
