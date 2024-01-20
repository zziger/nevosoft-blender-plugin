from pathlib import Path
import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.ChrFile import ChrFile
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile
from ..logger import operator_logger


class ImportCharacterOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper):
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

    load_at_0z: bpy.props.BoolProperty(
        name="Load at height 0",
        description="Move character's root bone to height 0",
        default=True,
    )

    def execute(self, context):
        with operator_logger(self):
            try:
                chr = ChrFile.read(self.filepath)
                directory = str(Path(self.filepath).parent)

                if chr.isComplex(directory):
                    bpy.ops.nevosoft.import_simplified_character('INVOKE_DEFAULT', chr_filepath=self.filepath, load_at_0z=self.load_at_0z)
                    return {'FINISHED'}
                
                chr.create(directory, self.load_at_0z)
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)

            return {'FINISHED'}