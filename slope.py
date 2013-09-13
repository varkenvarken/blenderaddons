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
    "version": (0, 0, 4),
    "blender": (2, 68, 0),
    "location": "View3D > Weights > Slope  and  View3D > Paint > Slope",
    "description": "Replace active vertex group or vertex color layer with values representing the slope of a face",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"}

from math import pi, pow
from re import search
import bpy
from mathutils import Vector


class Slope:

    def weight(self, normal, reference=Vector((0, 0, 1))):
        angle = normal.angle(reference)
        if self.mirror and angle > pi / 2:
            angle = pi - angle
        weight = 0.0
        if angle <= self.low:
            weight = 1.0
        elif angle <= self.high:
            weight = 1 - (angle - self.low) / (self.high - self.low)
            weight = pow(weight, self.power)
        return weight


class Slope2VGroup(bpy.types.Operator, Slope):
    bl_idname = "mesh.slope2vgroup"
    bl_label = "Slope2VGroup"
    bl_options = {'REGISTER', 'UNDO'}

    low = bpy.props.FloatProperty(name="Lower limit", description="Angles smaller than this get a unit weight", subtype="ANGLE", default=0, max=pi, min=0)
    high = bpy.props.FloatProperty(name="Upper limit", description="Angles larger than this get a zero weight", subtype="ANGLE", default=pi / 2, max=pi, min=0.01)
    power = bpy.props.FloatProperty(name="Power", description="Shape of mapping curve", default=1, min=0, max=10)
    mirror = bpy.props.BoolProperty(name="Mirror", description="Limit angle to 90 degrees", default=False)
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
        reference = Vector((0, 0, 1))
        if self.worldspace:
            reference = reference * wmat
        for v in mesh.vertices:
            vertex_group.add([v.index], self.weight(v.normal, reference), 'REPLACE')
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
    high = bpy.props.FloatProperty(name="Upper limit", description="Angles larger than this get a zero weight", subtype="ANGLE", default=pi / 2, max=pi, min=0.01)
    power = bpy.props.FloatProperty(name="Power", description="Shape of mapping curve", default=1, min=0, max=10)
    mirror = bpy.props.BoolProperty(name="Mirror", description="Limit angle to 90 degrees", default=False)
    curve = bpy.props.BoolProperty(name="Use brush curve", description="Apply brush curve after calculculating values", default=False)
    normal = bpy.props.BoolProperty(name="Map normal", description="Convert face normal to vertex colors instead of slope angle", default=False)
    worldspace = bpy.props.BoolProperty(name="World space", description="Use world space instead of object space coordinates", default=False)

    @classmethod
    def poll(self, context):
        p = (context.mode == 'PAINT_VERTEX' and
             isinstance(context.scene.objects.active, bpy.types.Object) and
             isinstance(context.scene.objects.active.data, bpy.types.Mesh))
        return p

    def execute(self, context):
        if self.curve:
            # see: https://projects.blender.org/tracker/index.php?func=detail&aid=36688
            bcurvemap = context.tool_settings.vertex_paint.brush.curve
            bcurvemap.initialize()
            bcurve = bcurvemap.curves[0]
        wmat = context.scene.objects.active.matrix_world
        mesh = context.scene.objects.active.data
        vertex_colors = mesh.vertex_colors.active.data
        for poly in mesh.polygons:
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                pnormal = poly.normal
                if self.normal:
                    if self.worldspace:
                        pnormal = wmat * pnormal
                    vertex_colors[loop_index].color = list(map(lambda x: (x + 1) / 2, pnormal.normalized()))  # afaik a normal is not necessarily normalized
                else:
                    if self.worldspace:
                        weight = self.weight(pnormal, Vector((0, 0, 1)) * wmat)
                    else:
                        weight = self.weight(pnormal)
                    if self.curve:
                        weight = bcurve.evaluate(1.0 - weight)
                    vertex_colors[loop_index].color = [weight, weight, weight]
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        context.scene.update()
        return {'FINISHED'}

    def draw(self, context):  # provide a draw function here to show use brush option only with versions that have the new initialize function
        layout = self.layout
        if not self.curve and not self.normal:
            layout.prop(self, 'low')
            layout.prop(self, 'high')
            layout.prop(self, 'power')
        if not self.curve:
            layout.prop(self, 'normal')
        if not self.normal:
            layout.prop(self, 'mirror')
        layout.prop(self, 'worldspace')
        # checking for a specific build is a bit tricky as it may contain other chars than just digits
        if int(search(r'\d+', str(bpy.app.build_revision)).group(0)) > 60054:
            if not self.normal:
                layout.prop(self, 'curve')
                if self.curve:
                    layout.label('Click Paint -> Slope to see effect after changing brush curve')


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
