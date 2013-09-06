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
    "name": "Slope2vgroup",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 1),
    "blender": (2, 68, 0),
    "location": "View3D > Object > Slope",
    "description": "Replace active vertex group with weights representing the slope of a vertex",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"}

import bpy
from mathutils import Vector
from math import pi

class Slope2VGroup(bpy.types.Operator):
    bl_idname = "mesh.slope2vgroup"
    bl_label = "Slope2VGroup"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        p = (context.mode == 'OBJECT' and
             isinstance(context.scene.objects.active, bpy.types.Object) and
             isinstance(context.scene.objects.active.data, bpy.types.Mesh))
        return p
        
    def execute(self, context):
        ob = context.active_object
        vertex_group = ob.vertex_groups.active
        if vertex_group is None:
            bpy.ops.object.vertex_group_add()
            vertex_group = ob.vertex_groups.active
        mesh = ob.data
        for v in mesh.vertices:
            angle = 1 - v.normal.angle(Vector((0, 0, 1))) / pi
            vertex_group.add([v.index], angle, 'REPLACE')
        context.scene.update()
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(Slope2VGroup.bl_idname, text=bl_info['description'],
                         icon='PLUGIN')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.types.IVIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_module(__name__)
