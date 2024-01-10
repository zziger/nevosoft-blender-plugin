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
from .settings import PluginPreferences
from .logger import logger

from .extensions import BoneProperties

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

def unregister():
    pass