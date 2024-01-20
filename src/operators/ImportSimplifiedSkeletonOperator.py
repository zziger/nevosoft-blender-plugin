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


class ImportSimplifiedSkeletonOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper, ImportSkeletonSettings):
    """Simplify and import Nevosoft Skeleton file into current scene.
Simplification process requires a valid animation file to be selected"""

    bl_idname = "nevosoft.import_simplified_skeleton"
    bl_label = "Simplify Skeleton"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.skl',
        options={'HIDDEN'}
    )

    apply_anim: bpy.props.BoolProperty(
        name="Apply animation",
        description="Apply selected animation after import",
        default=True
    )

    skl_filepath: bpy.props.StringProperty(default="")
    confirmed: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if not self.confirmed:
            return context.window_manager.invoke_props_dialog(self, width=600)
        else:
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    def draw(self, context):
        if not self.confirmed:
            layout = self.layout
            layout.label(text="Selected model is too complex.")
            layout.label(text="To simplify the model, please select a valid animation.")
            layout.label(text="Proceed?")
        else:
            layout = self.layout
        
            layout.use_property_split = True
            layout.use_property_decorate = False
            operator = context.space_data.active_operator
            layout.prop(operator, 'apply_anim')

    def execute(self, context):
        if not self.confirmed:
            bpy.ops.nevosoft.import_simplified_skeleton('INVOKE_DEFAULT', confirmed=True, skl_filepath=self.skl_filepath, load_at_0z=self.load_at_0z)
            return {'FINISHED'}
        
        with operator_logger(self):
            try:
                anm = AnmFile.read(self.filepath)
                skl = SklFile.read(self.skl_filepath)
                skl.simplify(anm)
                obj = skl.create(Path(self.skl_filepath).stem, None, self)
                if self.apply_anim:
                    anm.create(obj.parent)
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)
            return {'FINISHED'}
