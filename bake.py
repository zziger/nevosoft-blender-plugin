import bpy

old_samples = 64
old_file_format = "PNG"
old_view_transform = "Standard"
old_look = "None"
old_gamma = 1
old_exposure = 0
old_colorspace = "Raw"
old_color_depth = "8"
old_color_mode = "RGBA"

BAKE_SAMPLES = 4
IMAGE_FORMAT = "JPEG"
IMAGE_EXT = ".jpg"
BAKE_INDEX = 1001
BUMP_BAKE_MULTIPLIER = 2.0


def prep_bake():
    global old_samples, old_file_format, old_color_depth, old_color_mode
    global old_view_transform, old_look, old_gamma, old_exposure, old_colorspace

    old_samples = bpy.context.scene.cycles.samples
    old_file_format = bpy.context.scene.render.image_settings.file_format
    old_color_depth = bpy.context.scene.render.image_settings.color_depth
    old_color_mode = bpy.context.scene.render.image_settings.color_mode
    old_view_transform = bpy.context.scene.view_settings.view_transform
    old_look = bpy.context.scene.view_settings.look
    old_gamma = bpy.context.scene.view_settings.gamma
    old_exposure = bpy.context.scene.view_settings.exposure
    old_colorspace = bpy.context.scene.sequencer_colorspace_settings.name

    bpy.context.scene.cycles.samples = BAKE_SAMPLES

    bpy.context.scene.cycles.preview_samples = BAKE_SAMPLES
    bpy.context.scene.cycles.use_adaptive_sampling = False
    bpy.context.scene.cycles.use_preview_adaptive_sampling = False
    bpy.context.scene.cycles.use_denoising = False
    bpy.context.scene.cycles.use_preview_denoising = False
    bpy.context.scene.cycles.use_auto_tile = False

    bpy.context.scene.render.use_bake_multires = False
    bpy.context.scene.render.bake.use_selected_to_active = False
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.margin = 16
    bpy.context.scene.render.bake.use_clear = True
    bpy.context.scene.render.image_settings.file_format = IMAGE_FORMAT
    # color management settings affect the baked output so set them to standard/raw defaults:
    bpy.context.scene.view_settings.view_transform = 'Standard'
    bpy.context.scene.view_settings.look = 'None'
    bpy.context.scene.view_settings.gamma = 1
    bpy.context.scene.view_settings.exposure = 0
    bpy.context.scene.sequencer_colorspace_settings.name = 'Raw'


def post_bake():
    global old_samples, old_file_format, old_color_depth, old_color_mode
    global old_view_transform, old_look, old_gamma, old_exposure, old_colorspace

    bpy.context.scene.cycles.samples = old_samples
    bpy.context.scene.cycles.preview_samples = old_samples
    bpy.context.scene.render.image_settings.file_format = old_file_format
    bpy.context.scene.render.image_settings.color_depth = old_color_depth
    bpy.context.scene.render.image_settings.color_mode = old_color_mode
    bpy.context.scene.view_settings.view_transform = old_view_transform
    bpy.context.scene.view_settings.look = old_look
    bpy.context.scene.view_settings.gamma = old_gamma
    bpy.context.scene.view_settings.exposure = old_exposure
    bpy.context.scene.sequencer_colorspace_settings.name = old_colorspace


def bake_texture(obj: bpy.types.Object, filepath: str):
    for inner in bpy.context.selected_objects:
        inner.select_set(False)

    obj.select_set(True)
    image_name = obj.name + '_BakedTexture'
    img = bpy.data.images.new(image_name, 1024, 1024)

    for mat in obj.data.materials:
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        texture_node = nodes.new('ShaderNodeTexImage')
        texture_node.name = 'Bake_node'
        texture_node.select = True
        nodes.active = texture_node
        texture_node.image = img  # Assign the image to the node

    bpy.context.view_layer.objects.active = obj
    prep_bake()
    try:
        bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, save_mode='EXTERNAL', width=1024, height=1024,
                            margin=16)

        img.save_render(filepath=filepath)
        print(f'saving baked {obj.name} to {filepath}')
    finally:
        print('finally block reached')
        post_bake()

        bpy.data.images.remove(img)

        for mat in obj.data.materials:
            for n in mat.node_tree.nodes:
                if n.name == 'Bake_node':
                    if n.image is not None:
                        bpy.data.images.remove(n.image)
                    mat.node_tree.nodes.remove(n)

                    print('removing node')
