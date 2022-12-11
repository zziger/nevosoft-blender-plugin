from .operators.ExportMeshOperator import ExportMeshOperator
from .operators.ExportObjectOperator import ExportObjectOperator
from .operators.ImportMeshOperator import ImportMeshOperator
from .operators.ImportObjectOperator import ImportObjectOperator

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
    ImportMeshOperator.load()
    ImportObjectOperator.load()
    ExportMeshOperator.load()
    ExportObjectOperator.load()
