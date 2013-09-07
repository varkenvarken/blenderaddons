# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Slope2vcol.py , a Blender addon
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

bl_info = {
    "name": "Slope2vcol",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 1),
    "blender": (2, 68, 0),
    "location": "View3D > Paint > Slope",
    "description": "Replace active vertex color layer with colors representing the slope of a face",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Paint"}

import bpy
from mathutils import Vector
from math import pi

class Slope2VCol(bpy.types.Operator):
    bl_idname = "mesh.slope2vcol"
    bl_label = "Slope2Vcol"
    bl_options = {'REGISTER', 'UNDO'}

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
            angle = 1 - poly.normal.angle(Vector((0, 0, 1))) / pi
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                vertex_colors[loop_index].color = [angle, 0, 0]
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        context.scene.update()
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(Slope2VCol.bl_idname, text=bl_info['description'],
                         icon='PLUGIN')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_paint_vertex.append(menu_func)


def unregister():
    bpy.types.IVIEW3D_MT_paint_vertex.remove(menu_func)
    bpy.utils.unregister_module(__name__)
