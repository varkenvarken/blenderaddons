# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Select Similar Verts, a Blender addon
#  (c) 2016 Michel J. Anders (varkenvarken)
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

import numpy as np
from random import random, seed
import bpy
import bmesh
from bpy.props import FloatProperty
from collections import defaultdict

bl_info = {
	"name": "Select Similar Verts",
	"author": "michel anders (varkenvarken)",
	"version": (0, 0, 201611251114),
	"blender": (2, 78, 0),
	"location": "View3D > Select > Select_similar > Neighborhood",
	"description": "Select vertices by neighborhood similarity",
	"warning": "",
	"wiki_url": "http://blenderthings.blogspot.com/",
	"tracker_url": "",
	"category": "Mesh"}


class SelectSimilarVerts(bpy.types.Operator):

	bl_idname = "mesh.select_similar_vertices"  # note that the second part of this name may *not* be the same as the basename of this file! Otherwise register_module() will fail
	bl_label = "SelectSimilarVerts"
	bl_options = {'REGISTER', 'UNDO'}

	similarity = FloatProperty(name="Similarity", default=0.9, description="similarity of environment")

	@classmethod
	def poll(self, context):
		return (context.mode == 'EDIT_MESH')  # and context.tool_settings.mesh_select_mode[0] # vertex select is too strict because in other modes verts are implicitly selected

	@staticmethod
	def variance3v(coords, indices):
		verts = coords[indices]
		center = verts.mean(axis=0)
		dirs = verts - center
		lengths = np.einsum('ij,ij->i',dirs,dirs)
		return np.var(lengths)

	def execute(self, context):
		# make sure changes in selection will be visible
		bpy.ops.object.editmode_toggle()
		bpy.ops.object.editmode_toggle()
		# gather the selected verts
		mesh = context.active_object.data
		selected = {v.index for v in mesh.vertices if v.select }
		if selected:
			# create a mapping vertex -> poligons
			vertex_polygons = defaultdict(set)
			for p in mesh.polygons:
				pi = p.index
				for vi in p.vertices:
					vertex_polygons[vi].add(pi)

			# get the normals of all polygons
			fnormals = np.empty(len(mesh.polygons) * 3)
			mesh.polygons.foreach_get('normal', fnormals)
			fnormals.shape = -1,3

			# get the normals of all verts
			vnormals = np.empty(len(mesh.vertices) * 3)
			mesh.vertices.foreach_get('normal', vnormals)
			vnormals.shape = -1,3

			# calculate the average of the angles between the vertex and face normals
			# TODO: convert to proper numpy and do it all in one go
			angles = defaultdict(float)
			n_angles = {}
			for vi,pis in vertex_polygons.items():
				for pi in pis:
					angles[vi] += vnormals[vi].dot(fnormals[pi])
				angles[vi] /= len(pis)
				n_angles[vi] = len(pis)

			# calculate the set of allowed angles
			s_angles = set(angles[vi] for vi in selected)
			sn_angles = set(n_angles[vi] for vi in selected)

			# select matching vertices
			bpy.ops.object.editmode_toggle()  # selecting must be done in object mode
			# TODO: this has potential for speed-up 
			for vi in range(len(vnormals)):
				if n_angles[vi] in sn_angles:
					v_angle = angles[vi]
					for ref in s_angles:
						if abs(v_angle - ref) <= 1 - self.similarity:
							mesh.vertices[vi].select = True
							break

			bpy.ops.object.editmode_toggle()

		return {'FINISHED'}


def menu_func(self, context):
	self.layout.separator()
	self.layout.operator(SelectSimilarVerts.bl_idname, text="Neighborhood",
						icon='PLUGIN')


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_select_similar.append(menu_func)


def unregister():
	bpy.types.VIEW3D_MT_edit_mesh_select_similar.remove(menu_func)
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
