from pathlib import Path
import traceback

import bpy
import bpy_extras

from ..helpers import OperatorBase
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile
from .ExportSkeletonOperator import ExportSkeletonOperator
from ..logger import operator_logger

class ImportAnimationOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper):
    """Import Nevosoft Animation file onto selected armature.
Armature must have one mesh child"""

    bl_idname = "nevosoft.import_animation"
    bl_label = "Nevosoft Animation (.anm)"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.anm',
        options={'HIDDEN'}
    )
    
    use_quaternions: bpy.props.BoolProperty(
        default=False,
        name="Use Quaternions",
        description="Use Quaternions (WXYZ) for rotations instead of Eulers (XYZ)"
    )
    
    @classmethod
    def poll(cls, context):
        return ExportSkeletonOperator.find_armature() is not None

    def draw(self, context):
        layout = self.layout
    
        layout.use_property_split = True
        layout.use_property_decorate = False
        operator = context.space_data.active_operator
        layout.prop(operator, 'use_quaternions')
            
    def execute(self, context):
        with operator_logger(self):
            try:
                obj = ExportSkeletonOperator.find_armature()
                if obj is None:
                    raise Exception("Failed to find an armature to import animation to. Select armature in your 3D viewport and make sure it has a mesh child")
                
                anm = AnmFile.read(self.filepath)
                anm.create(obj, self.use_quaternions)
            except Exception as e:
                self.error(str(e))
                traceback.print_exception(e)

            return {'FINISHED'}

    @staticmethod
    def load():
        bpy.utils.register_class(ImportAnimationOperator)

    @staticmethod
    def unload():
        bpy.utils.unregister_class(ImportAnimationOperator)
