# ##### BEGIN GPL LICENSE BLOCK #####
#
#  mesh2heightmap.py, a Blender addon
#  (c) 2018 Michel J. Anders (varkenvarken)
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
	"name": "mesh2heightmap",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 201812241102),
	"blender": (2, 79, 0),
	"location": "View3D > Object > Mesh2Heightmap",
	"description": "converts a mesh to a heightmap",
	"warning": "",
	"wiki_url": "https://github.com/varkenvarken/blenderaddons/blob/master/mesh2heightmap.py",
	"tracker_url": "",
	"category": "Object"}

import numpy as np
import bpy
from bpy.props import BoolProperty, StringProperty, IntProperty

class Mesh2Heightmap(bpy.types.Operator):
	"""converts the z-component of a mesh to a heightmap"""
	bl_idname = "object.mesh2heightmap"
	bl_label = "Mesh2Heightmap"
	bl_options = {'REGISTER','UNDO'}

	width = IntProperty(name="Width", default=128, min=64, soft_max=2048)
	height = IntProperty(name="Height", default=128, min=64, soft_max=2048)
	interpolate = BoolProperty(name="Interpolate", default=False)

	@classmethod
	def poll(cls, context):
		return (( context.active_object is not None ) 
			and (type(context.active_object.data) == bpy.types.Mesh)
			and (context.active_object.data.uv_layers.active is not None ))

	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)
		col.prop(self,'width')
		col.prop(self,'height')
		layout.prop(self,'interpolate')

	def execute(self, context):
		mesh = context.active_object.data
		width, height = self.width, self.height
		im = bpy.data.images.new("Heightmap", height, width, float_buffer=True)

		# initialize the heightmap to opaque black
		hm = np.zeros((width, height, 4), dtype=np.float32)
		hm[:,:,3] = 1.0

		# get uv coordinates of all loops
		uvlayer = mesh.uv_layers.active.data
		uv = np.empty(len(uvlayer)*2, dtype=np.float32)
		uvlayer.foreach_get('uv',uv)
		uv.shape = -1,2

		# get the object coordinates of all vertices
		co = np.empty(len(mesh.vertices)*3, dtype=
		np.float32)
		mesh.vertices.foreach_get('co', co)
		co.shape = -1,3

		# get the vertex indices of all loops
		vi = np.empty(len(mesh.loops), dtype=np.int32)
		mesh.loops.foreach_get('vertex_index',vi)

		# scale the z coordinate of the verts to the range [0,1]
		z = co[:,2][vi]
		zmax = np.max(z)
		zmin = np.min(z)
		zd = zmax - zmin
		z -= zmin
		z /= zd

		# scale the uv-coordinates to image dimensions
		# (they're still floats!)
		# not that we do NOT check if uvs are in range [0,1]
		uv[:,0] *= height-1
		uv[:,1] *= width-1
		uv = np.round(uv).astype(np.int32)

		# assign the height to each corresponding map coordinate
		# (just the rgb values, we leave alpha as is)
		for h,xy in zip(z,uv):
			hm[xy[1],xy[0],:3] = h

		# perform a linear interpolation for missing rows/columns
		# (will occur if map dimension is larger than number of
		# vertices in that same dimension)
		# NOTE: this will generate incorrect interpolation results
		# if the map size is more than twice the size of the grid
		# In which case it might be better to generate a map that
		# just fits and using an image manipulation program to scale up
		if self.interpolate:
			uniq0 = np.unique(uv[:,0])
			uniq1 = np.unique(uv[:,1])
			missing0 = np.setdiff1d(np.arange(height, dtype=np.int32), uniq0)
			missing1 = np.setdiff1d(np.arange(height, dtype=np.int32), uniq1)
			for y in missing1:
				hm[y,:] = (hm[y-1,:] + hm[y-1,:])/2
			for x in missing0:
				hm[:,x] = (hm[:,x-1] + hm[:,x+1])/2

		# copy the map to the new image.
		# always this way, i.e. flat copy, because assigning individual
		# pixels is way too slow
		im.pixels[:] = hm.flat[:]

		return {'FINISHED'}

def register():
	bpy.utils.register_class(Mesh2Heightmap)
	bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
	bpy.utils.unregister_class(Mesh2Heightmap)
	bpy.types.VIEW3D_MT_object.remove(menu_func)

def menu_func(self, context):
	self.layout.operator(Mesh2Heightmap.bl_idname, icon='PLUGIN')
