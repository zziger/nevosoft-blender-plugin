from pathlib import Path
import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.ChrFile import ChrFile
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile


class ImportCharacterOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper):
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
        default=False,
    )

    def execute(self, context):
        try:
            chr = ChrFile.read(self.filepath)
            directory = str(Path(self.filepath).parent)

            if chr.isComplex(directory):
                bpy.ops.nevosoft.import_simplified_character('INVOKE_DEFAULT', chr_filepath=self.filepath, load_at_0z=self.load_at_0z)
                return {'FINISHED'}
            
            chr.create(directory, self.load_at_0z)
            self.message("Character was imported successfully")
        except Exception as e:
            self.error(str(e))
            traceback.print_exception(e)
        return {'FINISHED'}

    @staticmethod
    def load():
        bpy.utils.register_class(ImportCharacterOperator)
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ImportCharacterOperator)
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


def menu_func_import(self, context):
    self.layout.operator(ImportCharacterOperator.bl_idname, text=ImportCharacterOperator.bl_label, icon="OUTLINER_OB_ARMATURE")
