from pathlib import Path
import traceback

import bpy
import bpy_extras

from ..settings.ImportSkeletonSettings import ImportSkeletonSettings
from ..helpers import OperatorBase
from ..structures.ChrFile import ChrFile
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile
from ..logger import operator_logger


class ImportCharacterOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper, ImportSkeletonSettings):
    """Import Nevosoft Character file into current scene"""

    bl_idname = "nevosoft.import_character"
    bl_label = "Nevosoft Character (.chr)"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.chr',
        options={'HIDDEN'}
    )

    def draw(self, context):
        pass

    def execute(self, context):
        with operator_logger(self):
            try:
                chr = ChrFile.read(self.filepath)
                directory = str(Path(self.filepath).parent)

                if chr.isComplex(directory):
                    bpy.ops.nevosoft.import_simplified_character('INVOKE_DEFAULT', chr_filepath=self.filepath, load_at_0z=self.load_at_0z)
                    return {'FINISHED'}
                
                chr.create(directory, self)
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)

            return {'FINISHED'}
