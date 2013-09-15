# ##### BEGIN GPL LICENSE BLOCK #####
#
#  height.py , a Blender addon
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
    "name": "Height",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 1),
    "blender": (2, 68, 0),
    "location": "View3D > Weights > Height  and  View3D > Paint > Height",
    "description": "Replace active vertex group or vertex color layer with values representing the coordinates or height of the vertices",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"}

from math import pi, pow
from re import search
import bpy
from mathutils import Vector


class Height2VGroup(bpy.types.Operator):
    bl_idname = "mesh.height2vgroup"
    bl_label = "Height2VGroup"
    bl_options = {'REGISTER', 'UNDO'}

    low = bpy.props.FloatProperty(name="Lower limit", description="Relative distances smaller than this get a zero weight", unit='LENGTH', subtype="DISTANCE", default=0, min=0, max=1)
    high = bpy.props.FloatProperty(name="Upper limit", description="Relative distances greater than this get a unit weight", unit='LENGTH', subtype="DISTANCE", default=1, min=0, max=1)
    power = bpy.props.FloatProperty(name="Power", description="Shape of mapping curve", default=1, min=0, max=10)
    abs = bpy.props.BoolProperty(name="Absolute", description="Treat negative distances as positive", default=False)
    axis = bpy.props.EnumProperty(name="Axis", description="Axis along which the distance is measured",
                                  items=[("X", "X-axis", "X-Axis"), ("Y", "Y-axis", "Y-Axis"), ("Z", "Z-axis", "Z-Axis")], default="Z")
    worldspace = bpy.props.BoolProperty(name="World space", description="Use world space instead of object space coordinates", default=False)
    
    @classmethod
    def poll(self, context):
        p = (context.mode == 'PAINT_WEIGHT' and
             isinstance(context.scene.objects.active, bpy.types.Object) and
             isinstance(context.scene.objects.active.data, bpy.types.Mesh))
        return p

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        ob = context.active_object
        wmat = ob.matrix_world
        vertex_group = ob.vertex_groups.active
        if vertex_group is None:
            bpy.ops.object.vertex_group_add()
            vertex_group = ob.vertex_groups.active
        mesh = ob.data
        i = {"X":0,"Y":1,"Z":2}[self.axis]
        if self.abs:
            if self.worldspace:
                mind = min([abs((wmat * v.co)[i]) for v in mesh.vertices])
                maxd = max([abs((wmat * v.co)[i]) for v in mesh.vertices])
            else:
                mind = min([abs(v.co[i]) for v in mesh.vertices])
                maxd = max([abs(v.co[i]) for v in mesh.vertices])
        else:
            if self.worldspace:
                mind = min([(wmat * v.co)[i] for v in mesh.vertices])
                maxd = max([(wmat * v.co)[i] for v in mesh.vertices])
            else:
                mind = min([v.co[i] for v in mesh.vertices])
                maxd = max([v.co[i] for v in mesh.vertices])            
        for v in mesh.vertices:
            if self.worldspace:
                d = (wmat * v.co)[i]
            else:
                d = v.co[i]
            if self.abs:
                d = abs(d)
            w = pow((d - mind) / (maxd - mind), self.power)
            if w < self.low:
                w = 0
            elif w > self.high:
                w = 1
            vertex_group.add([v.index], w, 'REPLACE')
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        context.scene.update()
        return {'FINISHED'}


def menu_func_weight(self, context):
    self.layout.operator(Height2VGroup.bl_idname, text="Height",
                         icon='PLUGIN')


def register():
    bpy.utils.register_class(Height2VGroup)
    bpy.types.VIEW3D_MT_paint_weight.append(menu_func_weight)


def unregister():
    bpy.types.IVIEW3D_MT_paint_weight.remove(menu_func_weight)
    bpy.utils.unregister_class(Height2VGroup)
