from pathlib import Path
import traceback

import bpy
import bpy_extras
from mathutils import Vector
from .ExportSkeletonOperator import ExportSkeletonOperator
from ..utils import find_last

from ..helpers import OperatorBase, select, set_active
from ..structures.MshFile import MshFile
from ..structures.SklFile import SklFile
from ..structures.AnmFile import AnmFile
from ..logger import operator_logger


class ImportAnimationBatchOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ImportHelper):
    """Imports multiple animations at once and stores information for their export"""

    bl_idname = "nevosoft.import_animation_batch"
    bl_label = "Import animation batch"
    bl_action = "import"
    bl_showtime = True
    bl_update_view = True

    filter_glob: bpy.props.StringProperty(
        default='*.anm',
        options={'HIDDEN'}
    )

    files: bpy.props.CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype='DIR_PATH')

    @classmethod
    def poll(cls, context):
        return ExportSkeletonOperator.find_armature() is not None
    
    def execute(self, context):
        with operator_logger(self):
            obj = ExportSkeletonOperator.find_armature()

            if obj is None:
                raise Exception("Failed to find an armature to import animations. Select armature in your 3D viewport and make sure it has a mesh child")

            animations = []

            for filepath in self.files:
                try:
                    filepath = self.directory + filepath.name
                    anm = AnmFile.read(filepath)
                    animations.append(anm)
                except Exception as e:
                    self.error(str(e))
                    traceback.print_exception(e)

            AnmFile.createBatch(animations, obj)
                    
            return {'FINISHED'}
