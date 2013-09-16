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
    "version": (0, 0, 2),
    "blender": (2, 68, 0),
    "location": "View3D > Weights > Height  and  View3D > Paint > Height",
    "description": "Replace active vertex group or vertex color layer with values representing the coordinates or height of the vertices",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh"}

from math import pow
from re import search
import bpy
from mathutils import Vector


class Height:

    def extremes(self, mesh, wmat):
        i = {"X": 0, "Y": 1, "Z": 2}[self.axis]
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
        return mind, maxd

    def map(self, coords, mind, maxd, wmat):
        i = {"X": 0, "Y": 1, "Z": 2}[self.axis]
        if self.worldspace:
            d = (wmat * coords)[i]
        else:
            d = coords[i]
        if self.abs:
            d = abs(d)
        w = pow((d - mind) / (maxd - mind), self.power)
        if w < self.low:
            w = 0
        elif w > self.high:
            w = 1
        if self.invert:
            w = 1 - w
        return w


class Height2VGroup(bpy.types.Operator, Height):
    bl_idname = "mesh.height2vgroup"
    bl_label = "Height2VGroup"
    bl_options = {'REGISTER', 'UNDO'}

    low = bpy.props.FloatProperty(name="Lower limit", description="Relative distances smaller than this get a zero weight", unit='LENGTH', subtype="DISTANCE", default=0, min=0, max=1)
    high = bpy.props.FloatProperty(name="Upper limit", description="Relative distances greater than this get a unit weight", unit='LENGTH', subtype="DISTANCE", default=1, min=0, max=1)
    power = bpy.props.FloatProperty(name="Power", description="Shape of mapping curve", default=1, min=0, max=10)
    abs = bpy.props.BoolProperty(name="Absolute", description="Treat negative distances as positive", default=False)
    invert = bpy.props.BoolProperty(name="Invert", description="Invert the resulting values", default=False)
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

        mind, maxd = self.extremes(mesh, wmat)
        for v in mesh.vertices:
            w = self.map(v.co, mind, maxd, wmat)
            vertex_group.add([v.index], w, 'REPLACE')

        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        context.scene.update()
        return {'FINISHED'}


class Height2VCol(bpy.types.Operator, Height):
    bl_idname = "mesh.height2vcol"
    bl_label = "Height2VCol"
    bl_options = {'REGISTER', 'UNDO'}

    low = bpy.props.FloatProperty(name="Lower limit", description="Relative distances smaller than this get a zero weight", unit='LENGTH', subtype="DISTANCE", default=0, min=0, max=1)
    high = bpy.props.FloatProperty(name="Upper limit", description="Relative distances greater than this get a unit weight", unit='LENGTH', subtype="DISTANCE", default=1, min=0, max=1)
    power = bpy.props.FloatProperty(name="Power", description="Shape of mapping curve", default=1, min=0, max=10)
    abs = bpy.props.BoolProperty(name="Absolute", description="Treat negative distances as positive", default=False)
    invert = bpy.props.BoolProperty(name="Invert", description="Invert the resulting values", default=False)
    axis = bpy.props.EnumProperty(name="Axis", description="Axis along which the distance is measured",
                                  items=[("X", "X-axis", "X-Axis"), ("Y", "Y-axis", "Y-Axis"), ("Z", "Z-axis", "Z-Axis")], default="Z")
    worldspace = bpy.props.BoolProperty(name="World space", description="Use world space instead of object space coordinates", default=False)
    curve = bpy.props.BoolProperty(name="Use brush curve", description="Apply brush curve after calculculating values", default=False)

    @classmethod
    def poll(self, context):
        p = (context.mode == 'PAINT_VERTEX' and
             isinstance(context.scene.objects.active, bpy.types.Object) and
             isinstance(context.scene.objects.active.data, bpy.types.Mesh))
        return p

    def draw(self, context):  # provide a draw function here to show use brush option only with versions that have the new initialize function
        layout = self.layout
        if not self.curve:
            layout.prop(self, 'low')
            layout.prop(self, 'high')
            layout.prop(self, 'power')
            layout.prop(self, 'abs')
            layout.prop(self, 'invert')
        layout.prop(self, 'axis')
        layout.prop(self, 'worldspace')
        # checking for a specific build is a bit tricky as it may contain other chars than just digits
        if int(search(r'\d+', str(bpy.app.build_revision)).group(0)) > 60054:
            layout.prop(self, 'curve')
            if self.curve:
                layout.label('Click Paint -> Height to see effect after changing brush curve')

    def execute(self, context):
        if self.curve:
            # see: https://projects.blender.org/tracker/index.php?func=detail&aid=36688
            bcurvemap = context.tool_settings.vertex_paint.brush.curve
            bcurvemap.initialize()
            bcurve = bcurvemap.curves[0]
        wmat = context.scene.objects.active.matrix_world
        mesh = context.scene.objects.active.data
        vertex_colors = mesh.vertex_colors.active.data

        mind, maxd = self.extremes(mesh, wmat)
        for poly in mesh.polygons:
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                # use average coordinate of face. Why Vector()? well sometimes Blender's Pyhthon API
                # is not very orthogonal. It beats me why Vertex.co is a vector and MeshPolygon.center isn't ...
                weight = self.map(Vector(poly.center), mind, maxd, wmat)
                if self.curve:
                    weight = bcurve.evaluate(1.0 - weight)
                vertex_colors[loop_index].color = [weight, weight, weight]
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        context.scene.update()
        return {'FINISHED'}


def menu_func_weight(self, context):
    self.layout.operator(Height2VGroup.bl_idname, text="Height",
                         icon='PLUGIN')


def menu_func_vcol(self, context):
    self.layout.operator(Height2VCol.bl_idname, text="Height",
                         icon='PLUGIN')


def register():
    bpy.utils.register_class(Height2VGroup)
    bpy.utils.register_class(Height2VCol)
    bpy.types.VIEW3D_MT_paint_vertex.append(menu_func_vcol)
    bpy.types.VIEW3D_MT_paint_weight.append(menu_func_weight)


def unregister():
    bpy.types.IVIEW3D_MT_paint_weight.remove(menu_func_weight)
    bpy.types.VIEW3D_MT_paint_vertex.remove(menu_func_vcol)
    bpy.utils.unregister_class(Height2VGroup)
    bpy.utils.unregister_class(Height2VCol)
