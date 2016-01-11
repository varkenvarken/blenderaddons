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
	"version": (0, 0, 201601111116),
	"blender": (2, 76, 0),
	"location": "View3D > Object > DumpMesh",
	"description": "Dumps geometry information of active object in a text buffer",
	"warning": "",
	"wiki_url": "https://github.com/varkenvarken/blenderaddons/blob/master/dumpmesh.py",
	"tracker_url": "",
	"category": "Object"}

# to prevent problems with all sorts of quotes and stuff the code that will be included in the final output is here base64 encoded
# you can find the readable version on https://github.com/varkenvarken/blenderaddons/blob/master/createmesh%20.py

GPLblurb = b'IyAjIyMjIyBCRUdJTiBHUEwgTElDRU5TRSBCTE9DSyAjIyMjIwojCiMgIENyZWF0ZU1lc2gsIGEgQmxlbmRlciBhZGRvbgojICAoYykgMjAxNiBNaWNoZWwgSi4gQW5kZXJzICh2YXJrZW52YXJrZW4pCiMKIyAgVGhpcyBwcm9ncmFtIGlzIGZyZWUgc29mdHdhcmU7IHlvdSBjYW4gcmVkaXN0cmlidXRlIGl0IGFuZC9vcgojICBtb2RpZnkgaXQgdW5kZXIgdGhlIHRlcm1zIG9mIHRoZSBHTlUgR2VuZXJhbCBQdWJsaWMgTGljZW5zZQojICBhcyBwdWJsaXNoZWQgYnkgdGhlIEZyZWUgU29mdHdhcmUgRm91bmRhdGlvbjsgZWl0aGVyIHZlcnNpb24gMgojICBvZiB0aGUgTGljZW5zZSwgb3IgKGF0IHlvdXIgb3B0aW9uKSBhbnkgbGF0ZXIgdmVyc2lvbi4KIwojICBUaGlzIHByb2dyYW0gaXMgZGlzdHJpYnV0ZWQgaW4gdGhlIGhvcGUgdGhhdCBpdCB3aWxsIGJlIHVzZWZ1bCwKIyAgYnV0IFdJVEhPVVQgQU5ZIFdBUlJBTlRZOyB3aXRob3V0IGV2ZW4gdGhlIGltcGxpZWQgd2FycmFudHkgb2YKIyAgTUVSQ0hBTlRBQklMSVRZIG9yIEZJVE5FU1MgRk9SIEEgUEFSVElDVUxBUiBQVVJQT1NFLiAgU2VlIHRoZQojICBHTlUgR2VuZXJhbCBQdWJsaWMgTGljZW5zZSBmb3IgbW9yZSBkZXRhaWxzLgojCiMgIFlvdSBzaG91bGQgaGF2ZSByZWNlaXZlZCBhIGNvcHkgb2YgdGhlIEdOVSBHZW5lcmFsIFB1YmxpYyBMaWNlbnNlCiMgIGFsb25nIHdpdGggdGhpcyBwcm9ncmFtOyBpZiBub3QsIHdyaXRlIHRvIHRoZSBGcmVlIFNvZnR3YXJlIEZvdW5kYXRpb24sCiMgIEluYy4sIDUxIEZyYW5rbGluIFN0cmVldCwgRmlmdGggRmxvb3IsIEJvc3RvbiwgTUEgMDIxMTAtMTMwMSwgVVNBLgojCiMgIyMjIyMgRU5EIEdQTCBMSUNFTlNFIEJMT0NLICMjIyMjCg=='

OperatorDef = b'YmxfaW5mbyA9IHsKCSJuYW1lIjogIkNyZWF0ZU1lc2giLAoJImF1dGhvciI6ICJNaWNoZWwgQW5kZXJzICh2YXJrZW52YXJrZW4pIiwKCSJ2ZXJzaW9uIjogKDAsIDAsIDIwMTYwMTExMTIxMiksCgkiYmxlbmRlciI6ICgyLCA3NiwgMCksCgkibG9jYXRpb24iOiAiVmlldzNEID4gT2JqZWN0ID4gQWRkIE1lc2ggPiBEdW1wZWRNZXNoIiwKCSJkZXNjcmlwdGlvbiI6ICJBZGRzIGEgbWVzaCBvYmplY3QgdG8gdGhlIHNjZW5lIHRoYXQgd2FzIGNyZWF0ZWQgd2l0aCB0aGUgRHVtcE1lc2ggYWRkb24iLAoJIndhcm5pbmciOiAiIiwKCSJ3aWtpX3VybCI6ICJodHRwczovL2dpdGh1Yi5jb20vdmFya2VudmFya2VuL2JsZW5kZXJhZGRvbnMvYmxvYi9tYXN0ZXIvY3JlYXRlbWVzaCUyMC5weSIsCgkidHJhY2tlcl91cmwiOiAiIiwKCSJjYXRlZ29yeSI6ICJBZGQgTWVzaCJ9CgppbXBvcnQgYnB5CmltcG9ydCBibWVzaAoKZGVmIGdlb21ldHJ5KCk6CgoJIyB3ZSBjaGVjayBpZiBjZXJ0YWluIGxpc3RzIGFuZCBkaWN0cyBhcmUgZGVmaW5lZAoJaGF2ZV9zZWFtcyAJCT0gJ3NlYW1zJyArIHN1ZmZpeCBpbiBnbG9iYWxzKCkKCWhhdmVfY3JlYXNlIAk9ICdjcmVhc2UnICsgc3VmZml4IGluIGdsb2JhbHMoKQoJaGF2ZV9zZWxlY3RlZCAJPSAnc2VsZWN0ZWQnICsgc3VmZml4IGluIGdsb2JhbHMoKQoJaGF2ZV91diAJCT0gJ3V2JyArIHN1ZmZpeCBpbiBnbG9iYWxzKCkKCgkjIHdlIGRlbGliZXJhdGVseSBzaGFkb3cgdGhlIGdsb2JhbCBlbnRyaWVzIHNvIHdlIGRvbid0IGhhdmUgdG8gZGVhbAoJIyB3aXRoIHRoZSBzdWZmaXggaWYgaXQncyB0aGVyZQoJdmVydHMgCQk9IGdsb2JhbHMoKVsndmVydHMnICsgc3VmZml4XQoJZWRnZXMgCQk9IGdsb2JhbHMoKVsnZWRnZXMnICsgc3VmZml4XQoJZmFjZXMgCQk9IGdsb2JhbHMoKVsnZmFjZXMnICsgc3VmZml4XQoJaWYgaGF2ZV9zZWFtczoJCXNlYW1zIAkJPSBnbG9iYWxzKClbJ3NlYW1zJyArIHN1ZmZpeF0KCWlmIGhhdmVfY3JlYXNlOgkJY3JlYXNlIAkJPSBnbG9iYWxzKClbJ2NyZWFzZScgKyBzdWZmaXhdCglpZiBoYXZlX3NlbGVjdGVkOglzZWxlY3RlZCAJPSBnbG9iYWxzKClbJ3NlbGVjdGVkJyArIHN1ZmZpeF0KCWlmIGhhdmVfdXY6CQkJdXYgCQkJPSBnbG9iYWxzKClbJ3V2JyArIHN1ZmZpeF0KCglibSA9IGJtZXNoLm5ldygpCgoJZm9yIHYgaW4gdmVydHM6CgkJYm0udmVydHMubmV3KHYpCglibS52ZXJ0cy5lbnN1cmVfbG9va3VwX3RhYmxlKCkgICMgZW5zdXJlcyBibS52ZXJ0cyBjYW4gYmUgaW5kZXhlZAoJYm0udmVydHMuaW5kZXhfdXBkYXRlKCkgICAgICAgICAjIGVuc3VyZXMgYWxsIGJtLnZlcnRzIGhhdmUgYW4gaW5kZXggKD0gZGlmZmVyZW50IHRoaW5nISkKCglmb3IgbixlIGluIGVudW1lcmF0ZShlZGdlcyk6CgkJZWRnZSA9IGJtLmVkZ2VzLm5ldyhibS52ZXJ0c1t2XSBmb3IgdiBpbiBlKQoJCWlmIGhhdmVfc2VhbXM6CgkJCWVkZ2Uuc2VhbSA9IHNlYW1zW25dCgkJaWYgaGF2ZV9zZWxlY3RlZDoKCQkJZWRnZS5zZWxlY3QgPSBzZWxlY3RlZFtuXQoKCWJtLmVkZ2VzLmVuc3VyZV9sb29rdXBfdGFibGUoKQoJYm0uZWRnZXMuaW5kZXhfdXBkYXRlKCkKCglpZiBoYXZlX2NyZWFzZToKCQljbCA9IGJtLmVkZ2VzLmxheWVycy5jcmVhc2UubmV3KCkKCQlmb3IgbixlIGluIGVudW1lcmF0ZShibS5lZGdlcyk6CgkJCWVbY2xdID0gY3JlYXNlW25dCgoJZm9yIGYgaW4gZmFjZXM6CgkJYm0uZmFjZXMubmV3KGJtLnZlcnRzW3ZdIGZvciB2IGluIGYpCgoJYm0uZmFjZXMuZW5zdXJlX2xvb2t1cF90YWJsZSgpCglibS5mYWNlcy5pbmRleF91cGRhdGUoKQoKCWlmIGhhdmVfdXY6CgkJdXZfbGF5ZXIgPSBibS5sb29wcy5sYXllcnMudXYubmV3KCkKCQlmb3IgZmFjZSBpbiBibS5mYWNlczoKCQkJZm9yIGxvb3AgaW4gZmFjZS5sb29wczoKCQkJCWxvb3BbdXZfbGF5ZXJdLnV2ID0gdXZbZmFjZS5pbmRleF1bbG9vcC52ZXJ0LmluZGV4XQoKCXJldHVybiBibQoKY2xhc3MgQ3JlYXRlTWVzaChicHkudHlwZXMuT3BlcmF0b3IpOgoJIiIiQWRkIGEgbGFkZGVyIG1lc2ggb2JqZWN0IHRvIHRoZSBzY2VuZSIiIgoJYmxfaWRuYW1lID0gIm1lc2guY3JlYXRlbWVzaCIKCWJsX2xhYmVsID0gIkNyZWF0ZU1lc2giCglibF9vcHRpb25zID0geydSRUdJU1RFUicsICdVTkRPJ30KCglAY2xhc3NtZXRob2QKCWRlZiBwb2xsKGNscywgY29udGV4dCk6CgkJcmV0dXJuIGNvbnRleHQubW9kZSA9PSAnT0JKRUNUJwoKCWRlZiBleGVjdXRlKHNlbGYsIGNvbnRleHQpOgoJCW1lID0gYnB5LmRhdGEubWVzaGVzLm5ldyhuYW1lPSdEdW1wZWRNZXNoJykKCQlvYiA9IGJweS5kYXRhLm9iamVjdHMubmV3KCdEdW1wZWRNZXNoJywgbWUpCgoJCWJtID0gZ2VvbWV0cnkoKQoKCQkjIHdyaXRlIHRoZSBibWVzaCB0byB0aGUgbWVzaAoJCWJtLnRvX21lc2gobWUpCgkJbWUuc2hvd19lZGdlX3NlYW1zID0gVHJ1ZQoJCW1lLnVwZGF0ZSgpCgkJYm0uZnJlZSgpCgoJCSMgYXNzb2NpYXRlIHRoZSBtZXNoIHdpdGggdGhlIG9iamVjdAoJCW9iLmRhdGEgPSBtZQoKCQkjIGxpbmsgdGhlIG9iamVjdCB0byB0aGUgc2NlbmUgJiBtYWtlIGl0IGFjdGl2ZSBhbmQgc2VsZWN0ZWQKCQljb250ZXh0LnNjZW5lLm9iamVjdHMubGluayhvYikKCQljb250ZXh0LnNjZW5lLnVwZGF0ZSgpCgkJY29udGV4dC5zY2VuZS5vYmplY3RzLmFjdGl2ZSA9IG9iCgkJb2Iuc2VsZWN0ID0gVHJ1ZQoKCQlyZXR1cm4geydGSU5JU0hFRCd9CgpkZWYgcmVnaXN0ZXIoKToKCWJweS51dGlscy5yZWdpc3Rlcl9tb2R1bGUoX19uYW1lX18pCglicHkudHlwZXMuSU5GT19NVF9tZXNoX2FkZC5hcHBlbmQobWVudV9mdW5jKQoKZGVmIHVucmVnaXN0ZXIoKToKCWJweS51dGlscy51bnJlZ2lzdGVyX21vZHVsZShfX25hbWVfXykKCWJweS50eXBlcy5JTkZPX01UX21lc2hfYWRkLnJlbW92ZShtZW51X2Z1bmMpCgpkZWYgbWVudV9mdW5jKHNlbGYsIGNvbnRleHQpOgoJc2VsZi5sYXlvdXQub3BlcmF0b3IoQ3JlYXRlTWVzaC5ibF9pZG5hbWUsIGljb249J1BMVUdJTicpCgppZiBfX25hbWVfXyA9PSAiX19tYWluX18iOgoJcmVnaXN0ZXIoKQo='


import bpy
from bpy.props import BoolProperty, StringProperty, IntProperty
from base64 import standard_b64decode as b64decode

class DumpMesh(bpy.types.Operator):
	"""Dumps mesh geometry information to a text buffer"""
	bl_idname = "object.dumpmesh"
	bl_label = "DumpMesh"
	bl_options = {'REGISTER','UNDO'}

	include_operator = BoolProperty(name="Add operator", 
							description="Add operator definition",
							default=True)

	suffix = StringProperty(name="Suffix",
							description="Suffix to add to list names",
							default="")

	compact = BoolProperty(name="Compact",
							description="Omit newlines and other whitespace",
							default=True)

	seams = BoolProperty(name="Seams",
							description="Include edge seams if present",
							default=True)

	crease = BoolProperty(name="Crease",
							description="Include edge crease layer if present (active layer only)",
							default=True)

	selected = BoolProperty(name="Selected",
							description="Include edge selection",
							default=True)

	uvs = BoolProperty(name="UV",
							description="Include uv values of loops if present (active layer only)",
							default=True)

	digits = IntProperty(name="Digits",
							description="Number of decimal places in vertex coordinates",
							default=4,
							min=1, max=9)

	def format_vertex(self, v):
		return ("({co[0]:.%dg},{co[1]:.%dg},{co[2]:.%dg})"%(self.digits,self.digits,self.digits)).format(co=v)

	def format_uv(self, v):
		return ("({co[0]:.%dg},{co[1]:.%dg})"%(self.digits,self.digits)).format(co=v)

	def draw(self, context):
		layout = self.layout
		layout.prop(self,'include_operator')
		layout.prop(self, 'suffix')
		row = layout.row()
		row.prop(self, 'compact')
		row.prop(self, 'digits')
		layout.prop(self,'seams')
		layout.prop(self,'crease')
		layout.prop(self,'selected')
		layout.prop(self,'uvs')

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

		nl = "" if self.compact else "\n"
		tb = "" if self.compact else "\t"

		if self.include_operator:
			output.write(b64decode(GPLblurb).decode())

		output.write("suffix = '%s'\n\n"%self.suffix)

		output.write("verts%s = [%s" % (self.suffix, nl))
		for v in verts:
			output.write(tb + self.format_vertex(v.co) + "," + nl)
		output.write("]\n\n")

		output.write("faces%s = [%s" % (self.suffix, nl))
		for f in faces:
			output.write(tb + str(tuple(f.vertices)) + "," + nl)
		output.write("]\n\n")

		output.write("edges%s = [%s" % (self.suffix, nl))
		for e in edges:
			output.write(tb + str(tuple(e.vertices)) + "," + nl)
		output.write("]\n\n")

		if self.seams:
			output.write("seams%s = {%s" % (self.suffix, nl))
			for e in edges:
				output.write(tb + str(e.index) + ": " + str(e.use_seam) + "," + nl)
			output.write("}\n\n")

		if self.crease:
			output.write("crease%s = {%s" % (self.suffix, nl))
			for e in edges:
				output.write(tb + str(e.index) + ": " + str(e.crease) + "," + nl)
			output.write("}\n\n")

		if self.selected:
			output.write("selected%s = {%s" % (self.suffix, nl))
			for e in edges:
				output.write(tb + str(e.index) + ": " + str(e.select) + "," + nl)
			output.write("}\n\n")

		if self.uvs and me.uv_layers.active_index > -1:
			uv_layer = me.uv_layers.active.data
			output.write("uv%s = {%s" % (self.suffix, nl))
			for poly in me.polygons:
				output.write(tb + str(poly.index) + ": {" + nl)
				for loop_index in poly.loop_indices:
					output.write(tb + tb + str(me.loops[loop_index].vertex_index) + ": " + self.format_uv(uv_layer[loop_index].uv) + "," + nl)
				output.write(tb + "}," + nl)
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
