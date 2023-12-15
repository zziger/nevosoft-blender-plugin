from pathlib import Path
import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile


class ImportSimplifiedSkeletonOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper):
    bl_idname = "nevosoft.import_simplified_skeleton"
    bl_label = "Simplify skeleton"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.anm',
        options={'HIDDEN'}
    )

    load_at_0z: bpy.props.BoolProperty(
        name="Load at height 0",
        description="Move character's root bone to height 0",
        default=False,
    )

    skl_filepath: bpy.props.StringProperty(default="")
    apply_anim: bpy.props.BoolProperty(name="Apply animation", description="Apply selected animation after import", default=False)
    confirmed: bpy.props.BoolProperty(default=False)

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
            bpy.ops.nevosoft.import_simplified_skeleton('INVOKE_DEFAULT', confirmed=True, skl_filepath=self.skl_filepath, load_at_0z=self.load_at_0z)
            return {'FINISHED'}
        
        try:
            anm = AnmFile.read(self.filepath)
            skl = SklFile.read(self.skl_filepath)
            skl.simplify(anm)
            if self.load_at_0z:
                skl.moveTo0z()
            obj = skl.create(Path(self.skl_filepath).stem, (0, 0, 0), None)
            if self.apply_anim:
                anm.create(obj.parent)
            self.message("Skeleton was simplified and imported successfully")
        except Exception as e:
            self.error(str(e))
            traceback.print_exception(e)
        return {'FINISHED'}

    @staticmethod
    def load():
        bpy.utils.register_class(ImportSimplifiedSkeletonOperator)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ImportSimplifiedSkeletonOperator)
