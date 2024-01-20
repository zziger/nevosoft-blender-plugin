import bpy

from .src.preferences import get_preferences, PluginPreferences
from .src.logger import logger, set_debug
from .src.lang.ru import ru_lang
from . import autoload

bl_info = {
    "name": "Nevosoft Model Formats (.cgo, .msh, .skl, .chr, .anm)",
    "description": "Import/export model and animation formats used in Nevosoft games",
    "author": "zziger, Creepobot",
    "blender": (3, 6, 2),
    "warning": "This is a development plugin version",
    "location": "File > Import/Export > Nevosoft ...",
    "doc_url": "https://github.com/zziger/nevosoft-blender-plugin",
    "tracker_url": "https://github.com/zziger/nevosoft-blender-plugin/issues/new",
    "category": "Import-Export",
}

autoload.init()

def register():
    version = "verison" in bl_info and bl_info["version"] or (0, 0, 0)
    logger.info("Loading Nevosoft blender plugin v%s", '.'.join(map(str, version)))

    bpy.utils.register_class(PluginPreferences)
    set_debug(get_preferences().debug)

    bpy.app.translations.register(__name__, {
        'ru': ru_lang
    })

    autoload.register()

def unregister():
    logger.info("Unloading Nevosoft blender plugin")
    
    autoload.unregister()

    bpy.app.translations.unregister(__name__)
    bpy.utils.unregister_class(PluginPreferences)