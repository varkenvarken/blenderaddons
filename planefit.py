# ##### BEGIN GPL LICENSE BLOCK #####
#
#  PLaneFit, (c) 2017,2018 Michel Anders (varkenvarken)
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
    "name": "PlaneFit",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 201805050933),
    "blender": (2, 79, 0),
    "location": "Edit mode 3d-view, Add-->PlaneFit",
    "description": "Add a plane that best fits a collection of selected vertices",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

import numpy as np

def planeFit(points):
    ctr = points.mean(axis=0)
    x = points - ctr
    M = np.cov(x.T)
    eigenvalues,eigenvectors = np.linalg.eig(M)
    normal = eigenvectors[:,eigenvalues.argmin()]
    return ctr,normal

def orthopoints(normal):
	m = np.argmax(normal)
	x = np.ones(3,dtype=np.float32)
	x[m] = 0
	x /= np.linalg.norm(x)
	x = np.cross(normal, x)
	y = np.cross(normal, x)
	return x,y

import bpy

class PlaneFit(bpy.types.Operator):
	bl_idname = 'mesh.planefit'
	bl_label = 'PlaneFit'
	bl_options = {'REGISTER', 'UNDO'}

	size = bpy.props.FloatProperty(name="Size", description="Size of the plane", default=1, min=0, soft_max=10)
	separate = bpy.props.BoolProperty(name="Separate", description="Generate the plane as a separate object", default=False)

	@classmethod
	def poll(self, context):
		return (context.mode == 'EDIT_MESH' and context.active_object.type == 'MESH')

	def execute(self, context):
		bpy.ops.object.editmode_toggle()
		ob = context.active_object
		me = ob.data
		count = len(me.vertices)
		if count > 0:  # degenerate mesh, but better safe than sorry
			shape = (count, 3)
			verts = np.empty(count*3, dtype=np.float32)
			selected = np.empty(count, dtype=np.bool)
			me.vertices.foreach_get('co', verts)
			me.vertices.foreach_get('select', selected)
			verts.shape = shape
			if np.count_nonzero(selected) >= 3 :
				ctr, normal = planeFit(verts[selected])
				dx, dy = orthopoints(normal)
				if self.separate:
					bpy.ops.mesh.primitive_plane_add(location = ob.location)
					me = context.active_object.data
					for vi,co in zip(me.polygons[0].vertices, [ctr+dx*self.size, ctr+dy*self.size, ctr-dx*self.size, ctr-dy*self.size]):
						me.vertices[vi].co = co
					context.scene.objects.active = ob
				else:
					# can't use mesh.from_pydata here because that won't let us ADD to a mesh
					me.vertices.add(4)
					me.vertices[count  ].co = ctr+dx*self.size
					me.vertices[count+1].co = ctr+dy*self.size
					me.vertices[count+2].co = ctr-dx*self.size
					me.vertices[count+3].co = ctr-dy*self.size
					lcount = len(me.loops)
					me.loops.add(4)
					pcount = len(me.polygons)
					me.polygons.add(1)
					me.polygons[pcount].loop_total = 4
					me.polygons[pcount].loop_start = lcount
					me.polygons[pcount].vertices = [count,count+1,count+2,count+3]
					me.update(calc_edges=True)
			else:
				self.report({'WARNING'}, "Need at least 3 selected vertices to fit a plane through")
		bpy.ops.object.editmode_toggle()
		return {'FINISHED'}

def menu_func(self, context):
	self.layout.operator(PlaneFit.bl_idname, text="Fit plane to selected",
						icon='PLUGIN')
	self.layout.operator(PlaneFit.bl_idname, text="Fit separate plane to selected",
						icon='PLUGIN').separate=True

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
	bpy.types.INFO_MT_mesh_add.remove(menu_func)
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
