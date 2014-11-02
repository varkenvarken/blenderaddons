# ##### BEGIN GPL LICENSE BLOCK #####
#
#  drystone.py , a Blender addon to create a wall of irregularly stacked stones.
#  (c) 2014 Michel J. Anders (varkenvarken)
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
	"name": "DryStone",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 20141102),
	"blender": (2, 71, 0),
	"location": "View3D > Add > Mesh > DryStone",
	"description": "Add a mesh of irregular stacked blocks.",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Add Mesh"}

import bpy
import bmesh
from bpy.props import BoolProperty, FloatProperty, EnumProperty, IntProperty, FloatVectorProperty
from mathutils import Vector
from mathutils.noise import noise
from random import random, seed, randint, choice, sample
from math import pi, acos

def vertical(edge):
	d = edge.verts[0].co - edge.verts[1].co
	return abs(d.x) < abs(d.y)

def fully_connected(vert):
	return len(vert.link_edges) > 3

def edge_angle(vert,e1,e2):
	v1 = e1.other_vert(vert).co - vert.co
	v2 = e2.other_vert(vert).co - vert.co
	v1.normalize()
	v2.normalize()
	return acos(v1.dot(v2))

def vertical_t_joint(vert):
	if len(vert.link_edges) == 3:
		e0 = vert.link_edges[0]
		e1 = vert.link_edges[1]
		e2 = vert.link_edges[2]
		v0 = vertical(e0)
		v1 = vertical(e1)
		v2 = vertical(e2)
		if not(v0 or v1) and (edge_angle(vert,e0,e1) > .97*pi): return True
		if not(v1 or v2) and (edge_angle(vert,e1,e2) > .97*pi): return True
		if not(v2 or v0) and (edge_angle(vert,e2,e0) > .97*pi): return True
	return False

def non_gap(edge):
	v0 = edge.verts[0]
	v1 = edge.verts[1]
	return (fully_connected(v0) or vertical_t_joint(v0)) and (fully_connected(v1) or vertical_t_joint(v1))

def non_corner(vert):
	for edge in vert.link_edges:
		vert1 = edge.other_vert(vert)
		if not (vertical_t_joint(vert1) or fully_connected(vert1)):
			return False
	return True

def v_inside(vert):
	return abs(abs(vert.co[0]) - 1.0) > 0.001 or abs(abs(vert.co[1]) - 1.0) > 0.001
	
def inside(edge):
	if v_inside(edge.verts[0]): return True
	return v_inside(edge.verts[1])

def get_internal_edges(bm):
	s = []
	for edge in bm.edges:
		if vertical(edge) and inside(edge) and non_gap(edge):
			s.append(edge)
	return s

def get_internal_verts(bm):
	return [vert for vert in bm.verts if fully_connected(vert) and non_corner(vert)]

def get_movable_edges(bm):
	s = []
	for edge in bm.edges:
		if vertical(edge) and vertical_t_joint(edge.verts[0]) and vertical_t_joint(edge.verts[1]):
			s.append(edge)
	return s
	
class DryStone(bpy.types.Operator):
	
	"""Add an irregular mesh of blocks"""
	
	bl_idname = "mesh.drystone"
	bl_label = "Add a mesh of irregular stacked blocks"
	bl_options = {'REGISTER', 'UNDO'}    

	xsub		= IntProperty  (name="X Subdividions"		, description="Number of subsivisions in the x direction", min=4, soft_max=100  , default=30)
	ysub		= IntProperty  (name="Y Subdividions"		, description="Number of subsivisions in the y direction", min=4, soft_max=100  , default=10)
	nv			= IntProperty  (name="Quad blocks"   		, description="Number of big square blocks"              , min=0, soft_max=100  , default=15)
	ne			= IntProperty  (name="Long blocks"   		, description="Number of longer blocks"                  , min=0, soft_max=200  , default=100)
	seed 		= IntProperty  (name="Random Seed"   		, description="Random Seed"                              , min=0                , default=0)
	randomedge	= FloatProperty(name="Random Edge"   		, description="Randomize movable edges"                  , min=0.0, max=0.5     , default=0.3)
	randomvert	= FloatProperty(name="Random Vert"   		, description="Randomize vertices"                       , min=0.0, max=0.5     , default=0.4)
	zrandom		= FloatProperty(name="Random Displacement"	, description="Randomize block depth"                    , min=0.0, max=0.5     , default=0.01)
	randomuv 	= BoolProperty (name="Randomize UVs"		, description="Randomize the uv-offset of individual stones", default=True)
										
				
	@classmethod
	def poll(self, context):
		"""
		Only visible in object mode.
		"""
		return (context.mode == 'OBJECT')
	
	def execute(self, context):
		seed(self.seed)
		bpy.ops.mesh.primitive_grid_add(x_subdivisions=self.xsub, y_subdivisions=self.ysub, enter_editmode=True)
		# TODO make spacing of horizontal rows somewhat variable
		obj = bpy.context.edit_object
		me = obj.data
		bm = bmesh.from_edit_mesh(me)
		bm.faces.active = None
		
		for i in range(self.nv):
			verts = get_internal_verts(bm)
			if len(verts):
				vert = choice(verts)
				bmesh.ops.dissolve_faces(bm, faces=vert.link_faces, use_verts=False)
				
		for i in range(self.ne):
			edges = get_internal_edges(bm)
			if len(edges):
				edge = choice(edges)
				bmesh.ops.dissolve_faces(bm, faces=edge.link_faces, use_verts=False)
				
		for edge in get_movable_edges(bm):
			x = (random()*2-1)*self.randomedge*(2.0/self.xsub)*0.5
			edge.verts[0].co.x += x
			edge.verts[1].co.x += x
		for vert in bm.verts:
			x = (noise(vert.co)*2-1)*self.randomvert*(2.0/self.xsub)*0.5
			y = (noise(vert.co+Vector((11.1,13.12,17.14)))*2-1)*self.randomvert*(2.0/self.ysub)*0.5
			vert.co.x += x
			vert.co.y += y
		
		extruded_faces = bmesh.ops.extrude_discrete_faces(bm, faces=bm.faces)['faces']
		bm.verts.index_update()
		for face in extruded_faces:
			vindices = [v.index for v in face.verts]
			for vert in face.verts:
				for e in vert.link_edges:
					overt = e.other_vert(vert)
					if overt.index not in vindices:
						overt.tag = True
		bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.tag], context=1)

		for face in bm.faces:
			z = (random()*2-1) * self.zrandom
			for vert in face.verts:
				vert.co.z += z
		
		bmesh.update_edit_mesh(me, True)
		bpy.ops.object.editmode_toggle()
		obj.scale.x = self.xsub/10.0
		obj.scale.y = self.ysub/10.0

		# add random uv and vcolor
		me.uv_textures.new()
		uv_layer = me.uv_layers.active.data
		vertex_colors = me.vertex_colors.new().data
		for poly in me.polygons:
			offset = Vector((random(), random(), 0)) if obj.randomuv else Vector((0, 0, 0))
			color = [random(), random(), random()]
			for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
				coords = me.vertices[me.loops[loop_index].vertex_index].co
				uv_layer[loop_index].uv = (coords + offset).xy
				vertex_colors[loop_index].color = color
		
		
		bpy.ops.object.modifier_add(type='SOLIDIFY')
		bpy.context.object.modifiers["Solidify"].offset = 1
		bpy.context.object.modifiers["Solidify"].thickness = 0.1
		bpy.ops.object.modifier_add(type='BEVEL')
		bpy.context.object.modifiers["Bevel"].width = 0.01
		bpy.context.object.modifiers["Bevel"].segments = 2

		return {'FINISHED'}

def menu_func(self, context):
	self.layout.operator(DryStone.bl_idname, icon='MESH_CUBE')
	
	
def register():
	bpy.utils.register_class(DryStone)
	bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
	bpy.utils.unregister_class(DryStone)
	bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
	register()