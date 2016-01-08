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
	"version": (0, 0, 201601081359),
	"blender": (2, 76, 0),
	"location": "View3D > Object > DumpMesh",
	"description": "Dumps geometry information of active object in a text buffer",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Object"}

# to prevent problems with all sorts of quotes and stuff the code that will be included in the final output is here base64 encoded
# you can find the readable version on https://github.com/varkenvarken/blenderaddons ad createmesh.py

GPLblurb = b'IyAjIyMjIyBCRUdJTiBHUEwgTElDRU5TRSBCTE9DSyAjIyMjIwojCiMgIENyZWF0ZU1lc2gsIGEgQmxlbmRlciBhZGRvbgojICAoYykgMjAxNiBNaWNoZWwgSi4gQW5kZXJzICh2YXJrZW52YXJrZW4pCiMKIyAgVGhpcyBwcm9ncmFtIGlzIGZyZWUgc29mdHdhcmU7IHlvdSBjYW4gcmVkaXN0cmlidXRlIGl0IGFuZC9vcgojICBtb2RpZnkgaXQgdW5kZXIgdGhlIHRlcm1zIG9mIHRoZSBHTlUgR2VuZXJhbCBQdWJsaWMgTGljZW5zZQojICBhcyBwdWJsaXNoZWQgYnkgdGhlIEZyZWUgU29mdHdhcmUgRm91bmRhdGlvbjsgZWl0aGVyIHZlcnNpb24gMgojICBvZiB0aGUgTGljZW5zZSwgb3IgKGF0IHlvdXIgb3B0aW9uKSBhbnkgbGF0ZXIgdmVyc2lvbi4KIwojICBUaGlzIHByb2dyYW0gaXMgZGlzdHJpYnV0ZWQgaW4gdGhlIGhvcGUgdGhhdCBpdCB3aWxsIGJlIHVzZWZ1bCwKIyAgYnV0IFdJVEhPVVQgQU5ZIFdBUlJBTlRZOyB3aXRob3V0IGV2ZW4gdGhlIGltcGxpZWQgd2FycmFudHkgb2YKIyAgTUVSQ0hBTlRBQklMSVRZIG9yIEZJVE5FU1MgRk9SIEEgUEFSVElDVUxBUiBQVVJQT1NFLiAgU2VlIHRoZQojICBHTlUgR2VuZXJhbCBQdWJsaWMgTGljZW5zZSBmb3IgbW9yZSBkZXRhaWxzLgojCiMgIFlvdSBzaG91bGQgaGF2ZSByZWNlaXZlZCBhIGNvcHkgb2YgdGhlIEdOVSBHZW5lcmFsIFB1YmxpYyBMaWNlbnNlCiMgIGFsb25nIHdpdGggdGhpcyBwcm9ncmFtOyBpZiBub3QsIHdyaXRlIHRvIHRoZSBGcmVlIFNvZnR3YXJlIEZvdW5kYXRpb24sCiMgIEluYy4sIDUxIEZyYW5rbGluIFN0cmVldCwgRmlmdGggRmxvb3IsIEJvc3RvbiwgTUEgMDIxMTAtMTMwMSwgVVNBLgojCiMgIyMjIyMgRU5EIEdQTCBMSUNFTlNFIEJMT0NLICMjIyMjCg=='

OperatorDef = b'YmxfaW5mbyA9IHsKCSJuYW1lIjogIkNyZWF0ZU1lc2giLAoJImF1dGhvciI6ICJNaWNoZWwgQW5kZXJzICh2YXJrZW52YXJrZW4pIiwKCSJ2ZXJzaW9uIjogKDAsIDAsIDIwMTYwMTA4MTEyMiksCgkiYmxlbmRlciI6ICgyLCA3NiwgMCksCgkibG9jYXRpb24iOiAiVmlldzNEID4gT2JqZWN0ID4gQWRkIE1lc2ggPiBEdW1wZWRNZXNoIiwKCSJkZXNjcmlwdGlvbiI6ICJBZGRzIGEgbWVzaCBvYmplY3QgdG8gdGhlIHNjZW5lIHRoYXQgd2FzIGNyZWF0ZWQgd2l0aCB0aGUgRHVtcE1lc2ggYWRkb24iLAoJIndhcm5pbmciOiAiIiwKCSJ3aWtpX3VybCI6ICIiLAoJInRyYWNrZXJfdXJsIjogIiIsCgkiY2F0ZWdvcnkiOiAiQWRkIE1lc2gifQoKaW1wb3J0IGJweQppbXBvcnQgYm1lc2gKCmRlZiBnZW9tZXRyeSgpOgoJYm0gPSBibWVzaC5uZXcoKQoKCWZvciB2IGluIHZlcnRzOgoJCWJtLnZlcnRzLm5ldyh2KQoJYm0udmVydHMuZW5zdXJlX2xvb2t1cF90YWJsZSgpCgkKCWZvciBuLGUgaW4gZW51bWVyYXRlKGVkZ2VzKToKCQllZGdlID0gYm0uZWRnZXMubmV3KGJtLnZlcnRzW3ZdIGZvciB2IGluIGUpCgkJZWRnZS5zZWFtID0gc2VhbXNbbl0KCWJtLmVkZ2VzLmVuc3VyZV9sb29rdXBfdGFibGUoKQoJY2wgPSBibS5lZGdlcy5sYXllcnMuY3JlYXNlLm5ldygpCglmb3IgbixlIGluIGVudW1lcmF0ZShibS5lZGdlcyk6ICMgbm8gbmVlZCBmb3IgYm0uZWRnZXMudXBkYXRlX2luZGV4LCB3ZSBkb24ndCB1c2UgZS5pbmRleAoJCWVbY2xdID0gY3JlYXNlW25dCgkKCWZvciBmIGluIGZhY2VzOgoJCWJtLmZhY2VzLm5ldyhibS52ZXJ0c1t2XSBmb3IgdiBpbiBmKQoKCXJldHVybiBibQoKY2xhc3MgQ3JlYXRlTWVzaChicHkudHlwZXMuT3BlcmF0b3IpOgoJIiIiQWRkIGEgbGFkZGVyIG1lc2ggb2JqZWN0IHRvIHRoZSBzY2VuZSIiIgoJYmxfaWRuYW1lID0gIm1lc2guY3JlYXRlbWVzaCIKCWJsX2xhYmVsID0gIkNyZWF0ZU1lc2giCglibF9vcHRpb25zID0geydSRUdJU1RFUicsICdVTkRPJ30KCglAY2xhc3NtZXRob2QKCWRlZiBwb2xsKGNscywgY29udGV4dCk6CgkJcmV0dXJuIGNvbnRleHQubW9kZSA9PSAnT0JKRUNUJwoKCWRlZiBleGVjdXRlKHNlbGYsIGNvbnRleHQpOgoJCW1lID0gYnB5LmRhdGEubWVzaGVzLm5ldyhuYW1lPSdEdW1wZWRNZXNoJykKCQlvYiA9IGJweS5kYXRhLm9iamVjdHMubmV3KCdEdW1wZWRNZXNoJywgbWUpCgoJCWJtID0gZ2VvbWV0cnkoKQoKCQkjIHdyaXRlIHRoZSBibWVzaCB0byB0aGUgbWVzaAoJCWJtLnRvX21lc2gobWUpCgkJbWUuc2hvd19lZGdlX3NlYW1zID0gVHJ1ZQoJCW1lLnVwZGF0ZSgpCgkJYm0uZnJlZSgpCgoJCSMgYXNzb2NpYXRlIHRoZSBtZXNoIHdpdGggdGhlIG9iamVjdAoJCW9iLmRhdGEgPSBtZQoKCQkjIGxpbmsgdGhlIG9iamVjdCB0byB0aGUgc2NlbmUgJiBtYWtlIGl0IGFjdGl2ZSBhbmQgc2VsZWN0ZWQKCQljb250ZXh0LnNjZW5lLm9iamVjdHMubGluayhvYikKCQljb250ZXh0LnNjZW5lLnVwZGF0ZSgpCgkJY29udGV4dC5zY2VuZS5vYmplY3RzLmFjdGl2ZSA9IG9iCgkJb2Iuc2VsZWN0ID0gVHJ1ZQoKCQlyZXR1cm4geydGSU5JU0hFRCd9CgpkZWYgcmVnaXN0ZXIoKToKCWJweS51dGlscy5yZWdpc3Rlcl9tb2R1bGUoX19uYW1lX18pCglicHkudHlwZXMuSU5GT19NVF9tZXNoX2FkZC5hcHBlbmQobWVudV9mdW5jKQoKZGVmIHVucmVnaXN0ZXIoKToKCWJweS51dGlscy51bnJlZ2lzdGVyX21vZHVsZShfX25hbWVfXykKCWJweS50eXBlcy5JTkZPX01UX21lc2hfYWRkLnJlbW92ZShtZW51X2Z1bmMpCgpkZWYgbWVudV9mdW5jKHNlbGYsIGNvbnRleHQpOgoJc2VsZi5sYXlvdXQub3BlcmF0b3IoQ3JlYXRlTWVzaC5ibF9pZG5hbWUsIGljb249J1BMVUdJTicpCgppZiBfX25hbWVfXyA9PSAiX19tYWluX18iOgoJcmVnaXN0ZXIoKQo='


import bpy
from bpy.props import BoolProperty
from base64 import standard_b64decode as b64decode

class DumpMesh(bpy.types.Operator):
	"""Dumps mesh geometry information to a text buffer"""
	bl_idname = "object.dumpmesh"
	bl_label = "DumpMesh"
	bl_options = {'REGISTER','UNDO'}

	include_operator = BoolProperty(name="Add operator", 
							description="Add operator definition",
							default=True)

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
		output = bpy.data.texts.new(me.name + "_mesh_data.py")

		if self.include_operator:
			output.write(b64decode(GPLblurb).decode())

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

		if self.include_operator:
			output.write(b64decode(OperatorDef).decode())

		# force newly created text block on top if text editor is visible
		for a in context.screen.areas:
			for s in a.spaces:
				if s.type == 'TEXT_EDITOR':
					s.text = output

		return {'FINISHED'}

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_object.remove(menu_func)

def menu_func(self, context):
	self.layout.operator(DumpMesh.bl_idname, icon='PLUGIN')
