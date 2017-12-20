# ##### BEGIN GPL LICENSE BLOCK #####
#
#  LineFit, (c) 2017 Michel Anders (varkenvarken)
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
    "name": "LineFit",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 201712201343),
    "blender": (2, 79, 0),
    "location": "Edit mode 3d-view, Add-->LineFit",
    "description": "Add a single edge to the mesh that best fits a collection of selected vertices",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

import numpy as np

def lineFit(points):
    ctr = points.mean(axis=0)
    x = points - ctr
    M = np.cov(x.T)
    eigenvalues,eigenvectors = np.linalg.eig(M)
    direction = eigenvectors[:,eigenvalues.argmax()]
    return ctr,direction

import bpy

class LineFit(bpy.types.Operator):
	bl_idname = 'mesh.linefit'
	bl_label = 'LineFit'
	bl_options = {'REGISTER', 'UNDO'}

	size = bpy.props.FloatProperty(name="Length", description="Length of the line segment", default=1, min=0, soft_max=10)

	@classmethod
	def poll(self, context):
		return (context.mode == 'EDIT_MESH' and context.active_object.type == 'MESH')

	def execute(self, context):
		bpy.ops.object.editmode_toggle()
		me = context.active_object.data
		count = len(me.vertices)
		if count > 0:  # degenerate mesh, but better safe than sorry
			shape = (count, 3)
			verts = np.empty(count*3, dtype=np.float32)
			selected = np.empty(count, dtype=np.bool)
			me.vertices.foreach_get('co', verts)
			me.vertices.foreach_get('select', selected)
			verts.shape = shape
			if np.count_nonzero(selected) >= 2 :
				ctr, direction = lineFit(verts[selected])
				# can't use mesh.from_pydata here because that won't let us ADD to a mesh
				me.vertices.add(2)
				me.vertices[count  ].co = ctr-direction*self.size
				me.vertices[count+1].co = ctr+direction*self.size
				ecount = len(me.edges)
				me.edges.add(1)
				me.edges[ecount].vertices = [count,count+1]
				me.update(calc_edges=False)
			else:
				self.report({'WARNING'}, "Need at least 2 selected vertices to fit a line through")
		bpy.ops.object.editmode_toggle()
		return {'FINISHED'}

def menu_func(self, context):
	self.layout.operator(LineFit.bl_idname, text="Fit line to selected",
						icon='PLUGIN')

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
	bpy.types.INFO_MT_mesh_add.remove(menu_func)
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
