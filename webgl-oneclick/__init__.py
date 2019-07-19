# gtlf-one-click, a program to export an object as a self contained html page 
# The MIT License

# Copyright © 2019 Michel Anders

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

bl_info = {
    'name': 'glTF one click export',
    'author': 'Michel Anders',
    "version": (0, 0, 201907190852),
    'blender': (2, 80, 0),
    'location': 'File > Import-Export',
    'description': 'Export object as complete html page',
    'warning': '',
    'wiki_url': "",
    'tracker_url': "",
    'category': 'Import-Export',
}

import os.path
from shutil import copytree, copy2
from os import mkdir

import bpy
from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty)
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from io_scene_gltf2 import ExportGLTF2_Base

class Default(dict):
    def __missing__(self, key):
        return key

# Addon prefs
class GLTF2OneClickPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    stylesheet_name : StringProperty(name="Stylesheet name", default='main.css', description="relative to add-on dir or absolutepath starting with /")

    copyright :  StringProperty(name="Copyright", default='&copy;', description="Copyright, will we displayed below modelname")
        
    def draw(self, context):
        layout = self.layout
        col0 = layout.column()
        col0.prop(self, 'stylesheet_name')
        col0.prop(self, 'copyright')

class ExportGLTF2OneClick(bpy.types.Operator, ExportGLTF2_Base, ExportHelper):
    """Export as a complete glTF 2.0 page"""
    bl_idname = 'export_scene.gltfoneclick'
    bl_label = 'Export glTF one click'

    filename_ext = ''

    filter_glob: StringProperty(default='*.glb;*.gltf', options={'HIDDEN'})

    copy_threejs: BoolProperty(default=True, name="three.js", description="Copy three.js javascript components")
    
    copy_stylesheet: BoolProperty(default=True, name="stylesheet", description="Copy main.css stylesheet")

    showbackground: BoolProperty(default=True, name="Show background", description="Show environment map (if any)")

    credits:  StringProperty(name="Credits", default='', description="Credits, will be shown on the right hand side")
    
    ui_tab: EnumProperty(
        items=(('GENERAL', "General", "General settings"),
           ('MESHES', "Meshes", "Mesh settings"),
           ('OBJECTS', "Objects", "Object settings"),
           ('ANIMATION', "Animation", "Animation settings"),
           ('EXPORT', 'Export', 'Export settings')),
        name="ui_tab",
        description="Export setting categories",
    )

    def draw(self, context):
        super().draw(context)
        if self.ui_tab == 'EXPORT':
            self.draw_export_settings()

    def draw_export_settings(self):
        col = self.layout.box().column()
        col.prop(self, 'copy_threejs')
        col.prop(self, 'copy_stylesheet')
        col.prop(self, 'showbackground')
        col.prop(self, 'credits')

    def execute(self, context):
        result = super().execute(context)

        dest = os.path.dirname(self.filepath)
        src= __path__[0]

        settings = context.preferences.addons[__name__].preferences

        if self.copy_threejs:
            for directory in ('build', 'modules', 'draco', 'licenses'):
                destdir = os.path.join(dest,directory)
                srcdir = os.path.join(src,directory)
                if not os.path.exists(destdir):  # todo: option to force removal of existing directories
                    print('copytree',srcdir, destdir)
                    copytree(srcdir, destdir)

        # copy stylesheet
        stylesheet_name = settings.stylesheet_name
        print(stylesheet_name)
        if self.copy_stylesheet:
            if stylesheet_name.startswith("/") or os.path.splitdrive(stylesheet_name)[0] != '':
                copy2(stylesheet_name, dest)
            else:
                copy2(os.path.join(src,stylesheet_name),dest)
            stylesheet_name = os.path.basename(stylesheet_name)
        # copy the first environment map in the scene (if any)
        try:
            mkdir(os.path.join(dest,'textures'))
        except FileExistsError:
            pass
        try:
            envmap = [n for n in context.scene.world.node_tree.nodes if n.type == 'TEX_ENVIRONMENT'][0]
            envmap_file = bpy.path.abspath(envmap.image.filepath)
            copy2(envmap_file, os.path.join(dest,'textures',os.path.basename(envmap_file)))
        except Exception as e:
            print(e)
            envmap_file = ''

        modelname=os.path.splitext(os.path.basename(self.filepath))[0]
        mapping = Default(modelname=modelname,
                          modelfile=os.path.basename(bpy.path.ensure_ext(self.filepath, self.filename_ext)),
                          stylesheet=stylesheet_name,
                          build='./build',
                          jsm='./modules/jsm',
                          draco='./draco/gltf/',
                          textures='textures/',
                          environmentmap=os.path.basename(envmap_file),
                          showbackground='true' if self.showbackground else 'false',
                          credits=self.credits,
                          copyright=settings.copyright)

        # convert the html file
        with open(os.path.join(src,'model.html')) as f:
            print('read')
            with open(os.path.join(dest,modelname + '.html'), 'w') as fw:
                for line in f:
                    try:
                        fw.write(line % mapping)
                    except ValueError as e:
                        print(e,line)
        return result

def menu_func_export(self, context):
    self.layout.operator(ExportGLTF2OneClick.bl_idname, text='glTF one click')

def register():
    bpy.utils.register_class(GLTF2OneClickPreferences)
    bpy.utils.register_class(ExportGLTF2OneClick)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportGLTF2OneClick)
    bpy.utils.unregister_class(GLTF2OneClickPreferences)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
