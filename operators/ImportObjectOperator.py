import traceback

import bpy
import bpy_extras
from bpy.props import BoolProperty
from bpy.types import Panel

from ..helpers import OperatorBase
from ..structures.CgoFile import CgoFile
from ..utils import clear_scene
from ..logger import operator_logger


class ImportObjectOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper):
    """Import Nevosoft Object file into current scene"""

    bl_idname = "nevosoft.import_object"
    bl_label = "Nevosoft Object (.cgo)"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.cgo',
        options={'HIDDEN'}
    )

    clear_scene: BoolProperty(
        name="Clear scene",
        description="Clear whole scene before importing",
        default=True,
    )

    def execute(self, context):
        with operator_logger(self):
            try:
                if self.clear_scene:
                    clear_scene()
                cgo = CgoFile.read(self.filepath)
                cgo.create()
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)
            return {'FINISHED'}

    def draw(self, context):
        pass

    @staticmethod
    def load():
        bpy.utils.register_class(ImportObjectOperator)
        bpy.utils.register_class(CUSTOM_PT_object_import_settings)
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ImportObjectOperator)
        bpy.utils.unregister_class(CUSTOM_PT_object_import_settings)
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


class CUSTOM_PT_object_import_settings(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Import settings"

    @classmethod
    def poll(cls, context):
        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return False

        operator = context.space_data.active_operator
        return operator.bl_idname == "NEVOSOFT_OT_import_object"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if not isinstance(context.space_data, bpy.types.SpaceFileBrowser):
            return

        operator = context.space_data.active_operator
        layout.prop(operator, 'clear_scene')


def menu_func_import(self, context):
    self.layout.operator(ImportObjectOperator.bl_idname, text=ImportObjectOperator.bl_label, icon="MESH_CUBE")