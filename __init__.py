from .operators.ExportCharacterOperator import ExportCharacterOperator
from .operators.ExportSkeletonOperator import ExportSkeletonOperator
from .operators.ImportCharacterOperator import ImportCharacterOperator
from .operators.ImportSimplifiedCharacterOperator import ImportSimplifiedCharacterOperator
from .operators.ImportAnimationOperator import ImportAnimationOperator
from .operators.ExportAnimationOperator import ExportAnimationOperator
from .operators.ExportMeshOperator import ExportMeshOperator
from .operators.ExportObjectOperator import ExportObjectOperator
from .operators.ImportMeshOperator import ImportMeshOperator
from .operators.ImportObjectOperator import ImportObjectOperator
from .operators.ImportSkeletonOperator import ImportSkeletonOperator
from .operators.ImportSimplifiedSkeletonOperator import ImportSimplifiedSkeletonOperator
# from .operators.DebugOperator import DebugOperator

from .extensions import BoneProperties

bl_info = {
    "name": "Nevosoft",
    "author": "Creepobot, zziger",
    "version": (0, 1),
    "blender": (3, 0, 1),
    "description": "",
    "warning": "",
    "location": "",
    "doc_url": "",
    "category": "Import-Export",
}


def register():
    BoneProperties.load()
    # DebugOperator.load()
    ImportMeshOperator.load()
    ImportObjectOperator.load()
    ImportSkeletonOperator.load()
    ImportSimplifiedSkeletonOperator.load()
    ImportAnimationOperator.load()
    ExportAnimationOperator.load()
    ImportCharacterOperator.load()
    ImportSimplifiedCharacterOperator.load()
    ExportMeshOperator.load()
    ExportObjectOperator.load()
    ExportSkeletonOperator.load()
    ExportCharacterOperator.load()