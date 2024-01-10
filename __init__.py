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
from .operators.RetargetAnimationsOperator import RetargetAnimationsOperator
from .operators.RetargetModelOperator import RetargetModelOperator
from .settings import PluginPreferences
from .logger import logger

from .extensions import BoneProperties, ModelTools

bl_info = {
    "name": "Nevosoft",
    "author": "zziger, Creepobot",
    "version": (0, 1),
    "blender": (3, 6, 2),
    "description": "",
    "warning": "",
    "location": "File -> Import/Export -> Nevosoft ...",
    "doc_url": "",
    "category": "Import-Export",
}


def register():
    logger.info("Loading Nevosoft blender plugin v%s", '.'.join(map(str, bl_info["version"])))

    PluginPreferences.load()
    BoneProperties.load()
    ModelTools.load()

    # Import
    ImportObjectOperator.load()
    ImportMeshOperator.load()
    ImportCharacterOperator.load()
    ImportSkeletonOperator.load()
    ImportAnimationOperator.load()
    ImportSimplifiedCharacterOperator.load()
    ImportSimplifiedSkeletonOperator.load()

    # Export
    ExportObjectOperator.load()
    ExportMeshOperator.load()
    ExportCharacterOperator.load()
    ExportSkeletonOperator.load()
    ExportAnimationOperator.load()

    # Tools
    RetargetAnimationsOperator.load()
    RetargetModelOperator.load()

def unregister():
    pass