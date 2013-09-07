# ##### BEGIN GPL LICENSE BLOCK #####
#
#  slope.py , a Blender addon
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
    "name": "Slope",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 2),
    "blender": (2, 68, 0),
    "location": "View3D > Weights > Slope  and  View3D > Paint > Slope",
    "description": "Replace active vertex group or vertex color layer with values representing the slope of a vertex",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"}

import bpy
from mathutils import Vector
from math import pi, pow

class Slope:
    
    def weight(self, normal):
        angle = normal.angle(Vector((0, 0, 1)))
        if self.mirror and angle > pi/2:
            angle = pi - angle
        weight = 0.0
        if angle <= self.low:
            weight = 1.0
        elif angle <= self.high:
            weight = 1 - (angle - self.low) / ( self.high - self.low )
            weight = pow(weight, self.power)
        return weight
        
class Slope2VGroup(bpy.types.Operator, Slope):
    bl_idname = "mesh.slope2vgroup"
    bl_label = "Slope2VGroup"
    bl_options = {'REGISTER', 'UNDO'}

    low = bpy.props.FloatProperty(name="Lower limit", description="Angles smaller than this get a unit weight", subtype="ANGLE", default=0, max=pi, min=0)
    high = bpy.props.FloatProperty(name="Upper limit", description="Angles larger than this get a zero weight", subtype="ANGLE", default=pi/2, max=pi, min=0.01)
    power = bpy.props.FloatProperty(name="Power", description="Shape of mapping curve", default=1, min=0, max=10)
    mirror = bpy.props.BoolProperty(name="Mirror", description="Limit angle to 90 degrees", default=False)

    @classmethod
    def poll(self, context):
        p = (context.mode == 'PAINT_WEIGHT' and
             isinstance(context.scene.objects.active, bpy.types.Object) and
             isinstance(context.scene.objects.active.data, bpy.types.Mesh))
        return p
        
    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        ob = context.active_object
        vertex_group = ob.vertex_groups.active
        if vertex_group is None:
            bpy.ops.object.vertex_group_add()
            vertex_group = ob.vertex_groups.active
        mesh = ob.data
        for v in mesh.vertices:
            vertex_group.add([v.index], self.weight(v.normal), 'REPLACE')
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        context.scene.update()
        return {'FINISHED'}


class Slope2VCol(bpy.types.Operator, Slope):
    bl_idname = "mesh.slope2vcol"
    bl_label = "Slope2Vcol"
    bl_options = {'REGISTER', 'UNDO'}

    low = bpy.props.FloatProperty(name="Lower limit", description="Angles smaller than this get a unit weight", subtype="ANGLE", default=0, max=pi, min=0)
    high = bpy.props.FloatProperty(name="Upper limit", description="Angles larger than this get a zero weight", subtype="ANGLE", default=pi/2, max=pi, min=0.01)
    power = bpy.props.FloatProperty(name="Power", description="Shape of mapping curve", default=1, min=0, max=10)
    mirror = bpy.props.BoolProperty(name="Mirror", description="Limit angle to 90 degrees", default=False)

    @classmethod
    def poll(self, context):
        p = (context.mode == 'PAINT_VERTEX' and
             isinstance(context.scene.objects.active, bpy.types.Object) and
             isinstance(context.scene.objects.active.data, bpy.types.Mesh))
        return p
        
    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        mesh = context.scene.objects.active.data
        vertex_colors = mesh.vertex_colors.active.data
        for poly in mesh.polygons:
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                vertex_colors[loop_index].color = [self.weight(poly.normal), 0, 0]
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        context.scene.update()
        return {'FINISHED'}


def menu_func_weight(self, context):
    self.layout.operator(Slope2VGroup.bl_idname, text="Slope",
                         icon='PLUGIN')


def menu_func_vcol(self, context):
    self.layout.operator(Slope2VCol.bl_idname, text="Slope",
                         icon='PLUGIN')


def register():
    bpy.utils.register_class(Slope2VCol)
    bpy.utils.register_class(Slope2VGroup)
    bpy.types.VIEW3D_MT_paint_weight.append(menu_func_weight)
    bpy.types.VIEW3D_MT_paint_vertex.append(menu_func_vcol)


def unregister():
    bpy.types.IVIEW3D_MT_paint_weight.remove(menu_func_weight)
    bpy.types.IVIEW3D_MT_paint_vertex.remove(menu_func_vcol)
    bpy.utils.unregister_class(Slope2VCol)
    bpy.utils.unregister_class(Slope2VGroup)
    