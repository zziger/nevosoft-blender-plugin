import os
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


class ImportAnimationBatchOperator(bpy.types.Operator, OperatorBase, bpy_extras.io_utils.ExportHelper):
    """Exports previously imported animation batch"""

    bl_idname = "nevosoft.export_animation_batch"
    bl_label = "Export animation batch"
    bl_action = "export"
    bl_showtime = True
    bl_update_view = True
    use_filter_folder = True
    filename_ext = "."

    filter_glob: bpy.props.StringProperty(
        default='*.anm',
        options={'HIDDEN'}
    )

    files: bpy.props.CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype='DIR_PATH')

    @classmethod
    def poll(cls, context):
        return ExportSkeletonOperator.find_armature() is not None and AnmFile.hasBatch()
    
    def execute(self, context):
        with operator_logger(self):
            obj = ExportSkeletonOperator.find_armature()

            if obj is None:
                raise Exception("Failed to find an armature to export animations. Select armature in your 3D viewport and make sure it has a mesh child")
            
            path = self.properties.filepath
            if not os.path.isdir(path):
                raise Exception("Select directory as an output")

            if not AnmFile.hasBatch():
                raise Exception("Batch animation data is missing. Import animation batch first")
            
            AnmFile.saveBatch(obj, path)
            
                    
            return {'FINISHED'}
