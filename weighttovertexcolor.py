# ##### BEGIN GPL LICENSE BLOCK #####
#
#  weighttovertexcolor.py , a Blender addon to transfer weights to vertex colors and vice versa.
#  (c) 2015 Michel J. Anders (varkenvarken)
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

bl_info = {
	"name": "WeightToVertexColor",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 20150228),
	"blender": (2, 73, 0),
	"location": "View3D > Weight Paint > Weights > WeightToVertexColor\nView3D > Vertex Paint > Paint > VertexColorToWeight",
	"description": "Transfer weights or colors between the active vertex group/ vertex color map.",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Paint"}

import bpy
import bmesh
from bpy.props import BoolProperty, FloatProperty, EnumProperty, IntProperty, FloatVectorProperty
from mathutils import Vector, Color

def update_particle_systems(ob, vg):
	"""
	Force an update for any particle system that refers to the given vertex group
	"""
	for ps in ob.particle_systems:
		# if one vertex group property is triggered that refers to the give group, all will be triggered
		if ps.vertex_group_clump == vg.name:
			ps.vertex_group_clump = vg.name  # reassigning will trigger recalculation
		elif ps.vertex_group_density == vg.name:
			ps.vertex_group_density = vg.name  # reassigning will trigger recalculation
		elif ps.vertex_group_field == vg.name:
			ps.vertex_group_field = vg.name  # reassigning will trigger recalculation
		elif ps.vertex_group_kink == vg.name:
			ps.vertex_group_kink = vg.name  # reassigning will trigger recalculation
		elif ps.vertex_group_length == vg.name:
			ps.vertex_group_length = vg.name  # reassigning will trigger recalculation
		elif ps.vertex_group_rotation == vg.name:
			ps.vertex_group_rotation = vg.name  # reassigning will trigger recalculation
		elif ps.vertex_group_roughness_1 == vg.name:
			ps.vertex_group_roughness_1 = vg.name  # reassigning will trigger recalculation
		elif ps.vertex_group_roughness_2 == vg.name:
			ps.vertex_group_roughness_2 = vg.name  # reassigning will trigger recalculation
		elif ps.vertex_group_roughness_end == vg.name:
			ps.vertex_group_roughness_end = vg.name  # reassigning will trigger recalculation
		elif ps.vertex_group_roughness_size == vg.name:
			ps.vertex_group_roughness_size = vg.name  # reassigning will trigger recalculation
		elif ps.vertex_group_roughness_tangent == vg.name:
			ps.vertex_group_roughness_tangent = vg.name  # reassigning will trigger recalculation
		elif ps.vertex_group_roughness_velocity == vg.name:
			ps.vertex_group_roughness_velocity = vg.name  # reassigning will trigger recalculation

class VertexColorToWeight(bpy.types.Operator):
	bl_idname = "mesh.vertexcolortoweight"
	bl_label = "VertexColorToWeight"
	bl_options = {'REGISTER', 'UNDO'}

	channel	= EnumProperty (name="Channel", description="Channel to use as weight", items=[('R','Red','Red'),('G','Green','Green'),('B','Blue','Blue'),('M','All (Monochrome)','All (Monochrome)')])
	
	@classmethod
	def poll(self, context):
		"""
		Only visible in weight paint mode if the active object is a mesh.
		"""
		p = (context.mode == 'PAINT_WEIGHT' and
			isinstance(context.scene.objects.active, bpy.types.Object) and
			isinstance(context.scene.objects.active.data, bpy.types.Mesh))
		return p

	def execute(self, context):
		bpy.ops.object.mode_set(mode='OBJECT')

		scene = context.scene
		self.ob = context.active_object
		mesh = context.scene.objects.active.data

		# select the active vertex group or create one if it does not exist yet
		vertex_group = self.ob.vertex_groups.active
		if vertex_group is None:
			bpy.ops.object.vertex_group_add()
			vertex_group = self.ob.vertex_groups.active
		scene = context.scene

		# select the active vertex color layer or create one if it does not exist yet
		if mesh.vertex_colors.active is None:
			bpy.ops.mesh.vertex_color_add()
		vertex_colors = mesh.vertex_colors.active.data

		colors = {}
		corners = {}
		for loop in mesh.loops:
			vi = loop.vertex_index
			if vi not in colors :
				# have to copy here, otherwise we would refer to an immutable copy and additions would silently fail
				colors[vi] = Color(vertex_colors[loop.index].color)
				corners[vi] = 1.0
			else:
				colors[vi] += vertex_colors[loop.index].color
				corners[vi]+= 1.0
		if self.channel == 'R':
			for vindex in colors:			
				vertex_group.add([vindex], colors[vindex].r/corners[vindex], 'REPLACE')
		elif self.channel == 'G':
			for vindex in colors:			
				vertex_group.add([vindex], colors[vindex].g/corners[vindex], 'REPLACE')
		elif self.channel == 'B':
			for vindex in colors:			
				vertex_group.add([vindex], colors[vindex].b/corners[vindex], 'REPLACE')
		else:
			for vindex in colors:			
				vertex_group.add([vindex], sum(colors[vindex]/corners[vindex])/3.0, 'REPLACE')
		
		bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
		scene.update()
		
		update_particle_systems(self.ob, vertex_group)
		
		return {'FINISHED'}

class WeightToVertexColor(bpy.types.Operator):
	bl_idname = "mesh.weighttovertexcolor"
	bl_label = "WeightToVertexColor"
	bl_options = {'REGISTER', 'UNDO'}

	channel	= EnumProperty (name="Channel", description="Channel to transfer weight to", items=[('R','Red','Red'),('G','Green','Green'),('B','Blue','Blue'),('M','All (Monochrome)','All (Monochrome)')])
	
	@classmethod
	def poll(self, context):
		"""
		Only visible in vertex paint mode if the active object is a mesh.
		"""
		p = (context.mode == 'PAINT_VERTEX' and
			isinstance(context.scene.objects.active, bpy.types.Object) and
			isinstance(context.scene.objects.active.data, bpy.types.Mesh))
		return p

	def execute(self, context):
		bpy.ops.object.mode_set(mode='OBJECT')

		scene = context.scene
		self.ob = context.active_object
		mesh = context.scene.objects.active.data

		# select the active vertex group or create one if it does not exist yet
		vertex_group = self.ob.vertex_groups.active
		if vertex_group is None:
			bpy.ops.object.vertex_group_add()
			vertex_group = self.ob.vertex_groups.active
		scene = context.scene

		# select the active vertex color layer or create one if it does not exist yet
		if mesh.vertex_colors.active is None:
			bpy.ops.mesh.vertex_color_add()
		vertex_colors = mesh.vertex_colors.active.data

		for loop in mesh.loops:
			weight = vertex_group.weight(loop.vertex_index)
			if self.channel == 'R':
				vertex_colors[loop.index].color = Color((weight, 0, 0))
			elif self.channel == 'G':
				vertex_colors[loop.index].color = Color((0, weight, 0))
			elif self.channel == 'B':
				vertex_colors[loop.index].color = Color((0, 0, weight))
			else:
				vertex_colors[loop.index].color = Color((weight, weight, weight))
		
		bpy.ops.object.mode_set(mode='VERTEX_PAINT')
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.object.mode_set(mode='VERTEX_PAINT')
		scene.update()
		
		update_particle_systems(self.ob, vertex_group)
		
		return {'FINISHED'}

			
def menu_func_weight(self, context):
	self.layout.operator(VertexColorToWeight.bl_idname, text="VertexColorToWeight",
						icon='PLUGIN')

def menu_func_vcol(self, context):
	self.layout.operator(WeightToVertexColor.bl_idname, text="WeightToVertexColor",
						icon='PLUGIN')


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_paint_weight.append(menu_func_weight)
	bpy.types.VIEW3D_MT_paint_vertex.append(menu_func_vcol)


def unregister():
	bpy.types.VIEW3D_MT_paint_weight.remove(menu_func_weight)
	bpy.types.VIEW3D_MT_paint_vertex.remove(menu_func_vcol)
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
