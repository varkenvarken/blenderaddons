# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Random vertex colors, a Blender addon
#  (c) 2013 Michel J. Anders (varkenvarken)
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

from random import random
import bpy

bl_info = {
    "name": "Random vertex colors",
    "author": "michel anders (varkenvarken)",
    "version": (0, 0, 1),
    "blender": (2, 68, 0),
    "location": "View3D > Paint > Add random vertex colors",
    "description": "Add random vertex colors to individual faces.",
    "warning": "",
    "wiki_url": "http://blenderthings.blogspot.com/2013/08/random-vertex-colors-simple-addon.html",
    "tracker_url": "",
    "category": "Paint"}


class RandomVertexColors(bpy.types.Operator):

    bl_idname = "mesh.random_vertex_colors"
    bl_label = "RandomVertexColors"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    @classmethod
    def poll(self, context):
        # Check if we have a mesh object active and are in vertex paint mode
        p = (context.mode == 'PAINT_VERTEX' and
             isinstance(context.scene.objects.active, bpy.types.Object) and
             isinstance(context.scene.objects.active.data, bpy.types.Mesh))
        return p

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        mesh = context.scene.objects.active.data
        vertex_colors = mesh.vertex_colors.active.data
        for poly in mesh.polygons:
            color = [random(), random(), random()]
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                vertex_colors[loop_index].color = color
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        context.scene.update()
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(RandomVertexColors.bl_idname, text=bl_info['description'],
                         icon='PLUGIN')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_paint_vertex.append(menu_func)


def unregister():
    bpy.types.IVIEW3D_MT_paint_vertex.remove(menu_func)
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
