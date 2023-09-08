from pathlib import Path
import traceback

import bpy
import bpy_extras


from ..helpers import OperatorBase
from ..structures.ChrFile import ChrFile
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile


class ImportSimplifiedCharacterOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper):
    bl_idname = "nevosoft.import_simplified_character"
    bl_label = "Simplify character"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.anm',
        options={'HIDDEN'}
    )

    chr_filepath: bpy.props.StringProperty(default="")
    confirmed: bpy.props.BoolProperty(default=False)
    apply_anim: bpy.props.BoolProperty(name="Apply animation", description="Apply selected animation after import", default=False)

    def invoke(self, context, event):
        if not self.confirmed:
            return context.window_manager.invoke_props_dialog(self)
        else:
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    def draw(self, context):
        if not self.confirmed:
            layout = self.layout
            layout.label(text="Selected model is too complex.")
            layout.label(text="To simplify the model, please select a valid animation.")
            layout.label(text="Continue?")
        else:
            layout = self.layout
        
            layout.use_property_split = True
            layout.use_property_decorate = False
            operator = context.space_data.active_operator
            layout.prop(operator, 'apply_anim')

    def execute(self, context):
        if not self.confirmed:
            bpy.ops.nevosoft.import_simplified_character('INVOKE_DEFAULT', confirmed=True, chr_filepath=self.chr_filepath)
            return {'FINISHED'}
        
        try:
            chr = ChrFile.read(self.chr_filepath)
            anm = AnmFile.read(self.filepath)
            directory = str(Path(self.chr_filepath).parent)
            obj = chr.createSimplified(anm, directory)
            if self.apply_anim:
                anm.create(obj.parent)
            self.message("Character was simplified and imported successfully")
        except Exception as e:
            self.error(str(e))
            traceback.print_exception(e)
        return {'FINISHED'}

    @staticmethod
    def load():
        bpy.utils.register_class(ImportSimplifiedCharacterOperator)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ImportSimplifiedCharacterOperator)
