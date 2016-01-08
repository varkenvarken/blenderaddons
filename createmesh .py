# ##### BEGIN GPL LICENSE BLOCK #####
#
#  CreateMesh, a Blender addon
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

verts = [
	(-1.0, -1.0, -1.0),
	(-1.0, -1.0, 1.0),
	(-1.0, 1.0, -1.0),
	(-1.0, 1.0, 1.0),
	(1.0, -1.0, -1.0),
	(1.0, -1.0, 1.0),
	(1.0, 1.0, -1.0),
	(1.0, 1.0, 1.0),
]

faces = [
	(1, 3, 2, 0),
	(3, 7, 6, 2),
	(7, 5, 4, 6),
	(5, 1, 0, 4),
	(0, 2, 6, 4),
	(5, 7, 3, 1),
]

edges = [
	(0, 1),
	(1, 3),
	(3, 2),
	(2, 0),
	(3, 7),
	(7, 6),
	(6, 2),
	(7, 5),
	(5, 4),
	(4, 6),
	(5, 1),
	(0, 4),
]

seams = {
	0: True,
	1: True,
	2: True,
	3: True,
	4: False,
	5: True,
	6: False,
	7: True,
	8: True,
	9: True,
	10: False,
	11: False,
}

crease = {
	0: 0.0,
	1: 1.0,
	2: 0.0,
	3: 0.0,
	4: 1.0,
	5: 0.0,
	6: 0.0,
	7: 1.0,
	8: 0.0,
	9: 0.0,
	10: 1.0,
	11: 0.0,
}



bl_info = {
	"name": "CreateMesh",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 201601081122),
	"blender": (2, 76, 0),
	"location": "View3D > Object > Add Mesh > DumpedMesh",
	"description": "Adds a mesh object to the scene that was created with the DumpMesh addon",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Add Mesh"}

import bpy
import bmesh

def geometry():
	bm = bmesh.new()

	for v in verts:
		bm.verts.new(v)
	bm.verts.ensure_lookup_table()
	
	for n,e in enumerate(edges):
		edge = bm.edges.new(bm.verts[v] for v in e)
		edge.seam = seams[n]
	bm.edges.ensure_lookup_table()
	cl = bm.edges.layers.crease.new()
	for n,e in enumerate(bm.edges): # no need for bm.edges.update_index, we don't use e.index
		e[cl] = crease[n]
	
	for f in faces:
		bm.faces.new(bm.verts[v] for v in f)

	return bm

class CreateMesh(bpy.types.Operator):
	"""Add a ladder mesh object to the scene"""
	bl_idname = "mesh.createmesh"
	bl_label = "CreateMesh"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		me = bpy.data.meshes.new(name='DumpedMesh')
		ob = bpy.data.objects.new('DumpedMesh', me)

		bm = geometry()

		# write the bmesh to the mesh
		bm.to_mesh(me)
		me.show_edge_seams = True
		me.update()
		bm.free()

		# associate the mesh with the object
		ob.data = me

		# link the object to the scene & make it active and selected
		context.scene.objects.link(ob)
		context.scene.update()
		context.scene.objects.active = ob
		ob.select = True

		return {'FINISHED'}

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_mesh_add.remove(menu_func)

def menu_func(self, context):
	self.layout.operator(CreateMesh.bl_idname, icon='PLUGIN')

if __name__ == "__main__":
	register()
