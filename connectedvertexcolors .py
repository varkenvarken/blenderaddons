# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Connected vertex colors, a Blender addon
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

from random import random, seed
import bpy
import bmesh
from bpy.props import IntProperty

bl_info = {
	"name": "Connected vertex colors",
	"author": "michel anders (varkenvarken)",
	"version": (0, 0, 1),
	"blender": (2, 68, 0),
	"location": "View3D > Paint > Add connected vertex colors",
	"description": "Add random vertex colors to connected vertices.",
	"warning": "",
	"wiki_url": "http://blenderthings.blogspot.com/2013/08/coloring-connected-vertices.html",
	"tracker_url": "",
	"category": "Paint"}


class ConnectedVertexColors(bpy.types.Operator):

	bl_idname = "mesh.connected_vertex_colors"
	bl_label = "ConnectedVertexColors"
	bl_options = {'REGISTER', 'UNDO'}

	seed = IntProperty(name="Seed", default=0, description="random seed. A different value gives a different but repeatable result.")

	@classmethod
	def poll(self, context):
		# Check if we have a mesh object active and are in vertex paint mode
		p = (context.mode == 'PAINT_VERTEX' and
			isinstance(context.scene.objects.active, bpy.types.Object) and
			isinstance(context.scene.objects.active.data, bpy.types.Mesh))
		return p

	@staticmethod
	def connected_verts(v):
		v.tag = True
		for edge in v.link_edges:
			ov = edge.other_vert(v)
			if (ov is not None) and not ov.tag:
				ov.tag = True
				yield ov
				for cv in ConnectedVertexColors.connected_verts(ov):
					cv.tag = True
					yield cv
					
	@staticmethod
	def assign_vertex_colors(vertex_colors, me):
		bm = bmesh.new()
		bm.from_mesh(me)
		vcolors = {}
		for v in bm.verts:
			v.tag = False
		for v in bm.verts:
			if v.index in vcolors:
				continue
			else:
				vcolors[v.index] = [random(), random(), random()]
			for cv in ConnectedVertexColors.connected_verts(v):
				vcolors[cv.index] = vcolors[v.index]
					
		bm.free()
		for poly in me.polygons:
			for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
				vertex_colors[loop_index].color = vcolors[me.loops[loop_index].vertex_index]
			
	def execute(self, context):
		bpy.ops.object.mode_set(mode='OBJECT')
		mesh = context.scene.objects.active.data
		vertex_colors = mesh.vertex_colors.active.data
		
		seed(self.seed)
		ConnectedVertexColors.assign_vertex_colors(vertex_colors, mesh)
		
		bpy.ops.object.mode_set(mode='VERTEX_PAINT')
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.object.mode_set(mode='VERTEX_PAINT')
		context.scene.update()
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(ConnectedVertexColors.bl_idname, text=bl_info['description'],
						icon='PLUGIN')


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_paint_vertex.append(menu_func)


def unregister():
	bpy.types.IVIEW3D_MT_paint_vertex.remove(menu_func)
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
