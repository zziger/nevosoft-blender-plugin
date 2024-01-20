import traceback

import bpy
import bpy_extras
from bpy.props import BoolProperty, StringProperty
from bpy.types import Panel

from ..settings.BakeSettings import BakeSettings
from .ExportSkeletonOperator import ExportSkeletonOperator
from ..logger import operator_logger
from ..helpers import OperatorBase
from ..structures.ChrFile import ChrFile


class ExportCharacterOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ExportHelper, BakeSettings):
    """Export Nevosoft Character and Skeleton file from selected armature.
Armature must have one mesh child. Output character includes model, armature and texture data"""

    bl_idname = "nevosoft.export_character"
    bl_label = "Nevosoft Character (.chr)"
    bl_action = "export"
    bl_showtime = True
    bl_update_view = True
    check_extension = True
    filename_ext = ".chr"

    filter_glob: bpy.props.StringProperty(
        default='*.chr',
        options={'HIDDEN'}
    )

    texture_name: StringProperty(
        name="Texture name",
        description="Name for texture file",
        default=""
    )
    
    @classmethod
    def poll(cls, context):
        return ExportSkeletonOperator.find_armature() is not None

    def execute(self, context):
        with operator_logger(self):
            try:
                obj = ExportSkeletonOperator.find_armature()
                if obj is None:
                    raise Exception("Failed to find an armature to export. Select armature in your 3D viewport and make sure it has a mesh child")
                
                ChrFile.write(self.filepath, obj, self.texture_name, self)
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)

            return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        operator = context.space_data.active_operator
        layout.prop(operator, 'texture_name')
