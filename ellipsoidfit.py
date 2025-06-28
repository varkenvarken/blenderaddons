# ##### BEGIN GPL LICENSE BLOCK #####
#
#  EllipsoidFit, (c) 2017,2025 Michel Anders (varkenvarken)
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
    "name": "EllipsoidFit",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 20250609143117),
    "blender": (4, 4, 0),  # tested with 4.4.0
    "location": "Edit mode 3d-view, Add-->EllipsoidFit",
    "description": "Add a single ellipsoid metaball that best fits a collection of selected vertices",
    "warning": "",
    "wiki_url": "https://github.com/varkenvarken/blenderaddons",
    "category": "Mesh",
}

import numpy as np

from math import pi,sin,cos,radians as rad
circle = np.array([[cos(rad(phi)),sin(rad(phi)),0] for phi in [30 * i for i in range(12)]])
sphere = np.empty((9,12,3))
for i in range(9):
	z = sin(0.9*pi*0.5*((i-4)/4))
	s = cos(0.9*pi*0.5*((i-4)/4))
	sphere[i] = (circle*s + [0,0,z])
sphere.shape = -1,3
quads = []
for i in range(8):
	for j in range(12):
		p0 = i*12 + j
		p1 = i*12 + (j+1)%12
		p2 = p1 + 12
		p3 = p0 + 12
		quads.append( (p0, p1, p2 , p3) )

def Fit(points):
    ctr = points.mean(axis=0)
    x = points - ctr
    M = np.cov(x.T)
    eigenvalues,eigenvectors = np.linalg.eig(M)
    order = eigenvalues.argsort()[::-1]  # largest to smallest
    print(x)
    print(eigenvalues)
    print(order)
    print(eigenvectors)
    return ctr, eigenvalues[order], eigenvectors[order]

import bpy
from mathutils import Matrix

import bmesh


class EllipsoidFit(bpy.types.Operator):
	bl_idname = 'mesh.ellipsoidfit'
	bl_label = 'EllipsoidFit'
	bl_options = {'REGISTER', 'UNDO'}

	size: bpy.props.FloatProperty(name="Size", description="Radius of the ellipsoid", default=1, min=0, soft_max=10)

	@classmethod
	def poll(self, context):
		return (context.mode == 'EDIT_MESH' and context.active_object.type == 'MESH')

	def execute(self, context):
		me = context.active_object.data
		count = len(me.vertices)
		if count > 0:  # degenerate mesh, but better safe than sorry
			
			shape = (count, 3)
			verts = np.empty(count*3, dtype=np.float32)
			selected = np.empty(count, dtype=bool)
			me.vertices.foreach_get('co', verts)
			me.vertices.foreach_get('select', selected)
			verts.shape = shape
			if np.count_nonzero(selected) >= 3 :
				ctr, sizes, directions = Fit(verts[selected])
				rot = np.linalg.inv(directions)
				verts = sphere * (sizes * self.size)
				verts = (verts @ rot) + ctr
				# can't use mesh.from_pydata here because that won't let us ADD to a mesh
				
				
				bm = bmesh.from_edit_mesh(me)
		
				for q in quads:
					v0 = bm.verts.new(verts[q[0]])
					v1 = bm.verts.new(verts[q[1]])
					v2 = bm.verts.new(verts[q[2]])
					v3 = bm.verts.new(verts[q[3]])
					f = bm.faces.new((v0, v1, v2, v3))
					f.smooth = True

				bmesh.update_edit_mesh(me)
			else:
				self.report({'WARNING'}, "Need at least 3 selected vertices to fit an ellipsoid")
		return {'FINISHED'}

def menu_func(self, context):
	self.layout.operator(EllipsoidFit.bl_idname, text="Fit metaball to selected",
						icon='PLUGIN')

def register():
	bpy.utils.register_class(EllipsoidFit)
	bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
	bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
	bpy.utils.unregister_class(EllipsoidFit)

if __name__ == "__main__":
	register()
