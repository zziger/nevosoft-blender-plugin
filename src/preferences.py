import bpy
from bpy.types import Operator, AddonPreferences
from .constants import PACKAGE_NAME
from . import logger

def on_debug_update(self, context):
    logger.set_debug(self.debug)

class PluginPreferences(AddonPreferences):
    ignore_autoload = True
    bl_idname = PACKAGE_NAME
    update_handlers = list()

    debug: bpy.props.BoolProperty(
                name="Debug mode",
                description="Enable additional debug messages and features. May be useful to diagnose some issues",
                default=False,
                update=on_debug_update
            )


    def draw(self, context):
        layout = self.layout
        # layout.label(text="This is a preferences view for our addon")
        layout.prop(self, "debug")

def get_preferences(context = bpy.context) -> PluginPreferences:
    return context.preferences.addons[PACKAGE_NAME].preferences