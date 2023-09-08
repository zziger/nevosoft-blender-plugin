from pathlib import Path
import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile


class ImportSkeletonOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper):
    bl_idname = "nevosoft.import_skeleton"
    bl_label = "Nevosoft skeleton (.skl)"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.skl',
        options={'HIDDEN'}
    )

    def execute(self, context):
        try:
            skl = SklFile.read(self.filepath)

            if skl.isComplex():
                bpy.ops.nevosoft.import_simplified_skeleton('INVOKE_DEFAULT', skl_filepath=self.filepath)
                return {'FINISHED'}
                
            skl.create(Path(self.filepath).stem, (0, 0, 0), None)
            self.message("Skeleton was imported successfully")
        except Exception as e:
            self.error(str(e))
            traceback.print_exception(e)
        return {'FINISHED'}

    @staticmethod
    def load():
        bpy.utils.register_class(ImportSkeletonOperator)
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ImportSkeletonOperator)
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


def menu_func_import(self, context):
    self.layout.operator(ImportSkeletonOperator.bl_idname, text=ImportSkeletonOperator.bl_label)
