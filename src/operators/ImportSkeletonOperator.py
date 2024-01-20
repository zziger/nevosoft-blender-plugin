from pathlib import Path
import traceback

import bpy
import bpy_extras

from ..settings.ImportSkeletonSettings import ImportSkeletonSettings
from ..helpers import OperatorBase
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile
from ..logger import operator_logger


class ImportSkeletonOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper, ImportSkeletonSettings):
    """Import Nevosoft Skeleton file into current scene"""

    bl_idname = "nevosoft.import_skeleton"
    bl_label = "Nevosoft Skeleton (.skl)"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.skl',
        options={'HIDDEN'}
    )

    def draw(self, context):
        pass

    def execute(self, context):
        with operator_logger(self):
            try:
                skl = SklFile.read(self.filepath)

                if skl.isComplex():
                    bpy.ops.nevosoft.import_simplified_skeleton('INVOKE_DEFAULT', skl_filepath=self.filepath, load_at_0z=self.load_at_0z)
                    return {'FINISHED'}
                    
                skl.create(Path(self.filepath).stem, None, self)
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)
            return {'FINISHED'}
