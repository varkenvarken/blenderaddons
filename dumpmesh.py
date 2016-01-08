# ##### BEGIN GPL LICENSE BLOCK #####
#
#  DumpMesh, a Blender addon
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

bl_info = {
	"name": "DumpMesh",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 201601081008),
	"blender": (2, 76, 0),
	"location": "View3D > Object > DumpMesh",
	"description": "Dumps geometry information of active object in a text buffer",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Object"}

import bpy

class DumpMesh(bpy.types.Operator):
	"""Dumps mesh geometry information to a text buffer"""
	bl_idname = "object.dumpmesh"
	bl_label = "DumpMesh"
	bl_options = {'REGISTER'}

	@classmethod
	def poll(cls, context):
		return (( context.active_object is not None ) 
			and (type(context.active_object.data) == bpy.types.Mesh))

	def execute(self, context):
		ob = context.active_object
		me = ob.data
		verts = me.vertices
		faces = me.polygons
		edges = me.edges
		output = bpy.data.texts.new(me.name + "_mesh_data")

		output.write("verts = [\n")
		for v in verts:
			output.write("\t" + str(tuple(v.co)) + ",\n")
		output.write("]\n\n")

		output.write("faces = [\n")
		for f in faces:
			output.write("\t" + str(tuple(f.vertices)) + ",\n")
		output.write("]\n\n")

		output.write("edges = [\n")
		for e in edges:
			output.write("\t" + str(tuple(e.vertices)) + ",\n")
		output.write("]\n\n")

		output.write("seams = {\n")
		for e in edges:
			output.write("\t" + str(e.index) + ": " + str(e.use_seam) + ",\n")
		output.write("}\n\n")

		output.write("crease = {\n")
		for e in edges:
			output.write("\t" + str(e.index) + ": " + str(e.crease) + ",\n")
		output.write("}\n\n")

		return {'FINISHED'}

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_object.remove(menu_func)

def menu_func(self, context):
	self.layout.operator(DumpMesh.bl_idname, icon='PLUGIN')
