# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Random vertex colors, a Blender addon
#  (c) 2013,2019 Michel J. Anders (varkenvarken)
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

# a special thank you to Linus Yng and @ambi for their feedback on the
# numpy related changes.


from random import random
import bpy

from time import process_time as time

from bpy.props import BoolProperty
import numpy as np

bl_info = {
	"name": "Random vertex colors",
	"author": "michel anders (varkenvarken)",
	"version": (0, 0, 201904081105),
	"blender": (2, 80, 0),
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
		mesh = context.active_object.data
		vertex_colors = mesh.vertex_colors.active.data
		polygons = mesh.polygons
		verts = mesh.vertices
		npolygons = len(polygons)
		nverts = len(verts)
		nloops = len(vertex_colors)

		startloop = np.empty(npolygons, dtype=np.int32)
		numloops = np.empty(npolygons, dtype=np.int32)
		polygon_indices = np.empty(npolygons, dtype=np.int32)

		polygons.foreach_get('index', polygon_indices)
		polygons.foreach_get('loop_start', startloop)
		polygons.foreach_get('loop_total', numloops)

		colors = np.random.random_sample((npolygons,4)).astype(np.float32)
		loopcolors = np.empty((nloops,4), dtype=np.float32)

		loopcolors[startloop] = colors[polygon_indices]
		numloops -= 1
		nz = np.flatnonzero(numloops)
		while len(nz):
			startloop[nz] += 1
			loopcolors[startloop[nz]] = colors[polygon_indices[nz]]
			numloops[nz] -= 1
			nz = np.flatnonzero(numloops)

		loopcolors = loopcolors.flatten()
		vertex_colors.foreach_set("color", loopcolors)

		bpy.ops.object.mode_set(mode='VERTEX_PAINT')
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.object.mode_set(mode='VERTEX_PAINT')
		context.scene.update()
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(RandomVertexColors.bl_idname, text=bl_info['description'],
						 icon='PLUGIN')


def register():
	bpy.utils.register_class(RandomVertexColors)
	bpy.types.VIEW3D_MT_paint_vertex.append(menu_func)


def unregister():
	bpy.types.VIEW3D_MT_paint_vertex.remove(menu_func)
	bpy.utils.unregister_class(RandomVertexColors)


if __name__ == "__main__":
	register()
