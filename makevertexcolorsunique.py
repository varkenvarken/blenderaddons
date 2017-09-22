# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Make vertex colors unique, a Blender addon
#  (c) 2017 Michel J. Anders (varkenvarken)
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

from math import pow
import bpy
import numpy as np

bl_info = {
	"name": "Make vertex colors unique",
	"author": "michel anders (varkenvarken)",
	"version": (0, 0, 201709220951),
	"blender": (2, 79, 0),
	"location": "View3D > Object > Make vertex colors unique",
	"description": "Make vertex colors present in the active vertex color layer of all selected objects unique",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Paint"}

def color_set(n):
	n += 2  # to exclude pure black and pure white later
	N = 2
	if n >= 8 :
		N = 1 + int(pow(n-1, 1/3))
	colors = np.empty(N*N*N*3, dtype=np.float32)
	colors.shape = N,N,N,3
	M = N - 1
	for r in range(N):
		for g in range(N):
			for b in range(N):
				colors[r,g,b] = [r/M, g/M, b/M]
	colors.shape = -1,3
	np.random.shuffle(colors[1:n-1])  # we exclude pure black and white to prevent confusion with non masked areas
	return colors[1:n-1]

def unique_2d(a):  # Blender 2.79 does not inlude numpy 1.13 so we do not have an axis argument in np.unique, but see https://stackoverflow.com/questions/16970982/find-unique-rows-in-numpy-array
	b = a[np.lexsort(a.T)]
	return b[np.concatenate(([True], np.any(b[1:] != b[:-1],axis=1)))]

class UniqVertexColors(bpy.types.Operator):

	bl_idname = "mesh.unique_vertex_colors"
	bl_label = "UniqueVertexColors"
	bl_options = {'REGISTER', 'UNDO', 'PRESET'}

	createvcol = bpy.props.BoolProperty(name="Create VCol", default=False, description="Create missing vertex color layers in selected objects that do not have them")

	@classmethod
	def poll(self, context):
		p = context.mode == 'OBJECT'
		return p

	def execute(self, context):
		# first we determine the number of colors present in all objects
		colors = {}
		for ob in context.selected_objects:
			if ob.type == 'MESH':
				mesh = ob.data
				if mesh.vertex_colors.active is None:
					if self.createvcol:
						mesh.vertex_colors.new()
					else:
						continue

				vertex_colors = mesh.vertex_colors.active.data
				nloops = len(vertex_colors)

				loopcolors = np.empty(nloops*3, dtype=np.float32)
				vertex_colors.foreach_get("color", loopcolors)
				loopcolors.shape = nloops,3

				colors[ob.name] = unique_2d(loopcolors)

		ncolors = sum(len(col) for col in colors.values())
		print(ncolors)

		if ncolors > 0 :
			unique_colors = color_set(ncolors)
			color_idxs = list(range(len(unique_colors)))

			for name, cols in colors.items():
				# update the lookup dict, selecting a unique color for all colors occuring in this vertex color layer
				colmap = {}  # we need to clear it for each object because objects might have duplicate original colors
				for c in cols:
					tc = tuple(c)
					if tc not in colmap: # we have no mapping yet
						# we first check if the same color is present in the set of remapped colors to
						# keep things as constant as possible
						match = np.where(np.all(np.isclose(unique_colors,c, atol=0.01), axis=1))[0]
						if len(match) and match[0] in color_idxs:
							colmap[tc] = unique_colors[match[0]]
							color_idxs.remove(match[0])
						else: # if we didn't find it we simple pick one
							colmap[tc] = unique_colors[color_idxs.pop()]

				# get the vertex colors for each loop
				ob = bpy.data.objects[name]
				mesh = ob.data
				vertex_colors = mesh.vertex_colors.active.data
				nloops = len(vertex_colors)
				loopcolors = np.empty(nloops*3, dtype=np.float32)
				vertex_colors.foreach_get("color", loopcolors)
				loopcolors.shape = nloops,3

				# remap the colors
				for p in mesh.polygons:
					for i in range(p.loop_start, p.loop_start+p.loop_total):
						loopcolors[i] = colmap[tuple(loopcolors[i])]

				# return the vertex colors
				vertex_colors.foreach_set("color", np.array(loopcolors).flatten())

		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(UniqVertexColors.bl_idname, text=bl_info['name'],
						 icon='PLUGIN')


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
	bpy.types.VIEW3D_MT_object.remove(menu_func)
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
