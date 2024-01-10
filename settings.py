import bpy
from bpy.types import Operator, AddonPreferences
from . import logger

def on_debug_update(self, context):
    logger.set_debug(self.debug)

class PluginPreferences(AddonPreferences):
    bl_idname = __package__
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

    def load():
        bpy.utils.register_class(PluginPreferences)
        logger.set_debug(get_preferences().debug)

    def unload():
        bpy.utils.unregister_class(PluginPreferences)


def get_preferences(context = bpy.context) -> PluginPreferences:
    return context.preferences.addons[__package__].preferences