# ##### BEGIN GPL LICENSE BLOCK #####
#
#  export-opengl.py 
#  (c) 2018 Michel Anders (varkenvarken)
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
	"name": "Export OpenGL",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 201807310826),
	"blender": (2, 79, 0),
	"location": "File > Export > OpenGL",
	"description": "Export the active object as a Python OpenGL snippet",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Import-Export"}

import numpy as np
import bpy
import bmesh

from bpy.props import (
        StringProperty,
        BoolProperty,
        FloatProperty,
        EnumProperty,
        )
from bpy_extras.io_utils import (
        ExportHelper,
        path_reference_mode,
        )
        
class ExportOpenGL(bpy.types.Operator, ExportHelper):
	bl_idname = 'mesh.exportopengl'
	bl_label = 'Export mesh as OpenGL snippet'
	bl_options = {'REGISTER','UNDO'}

	filename_ext = ".py"
	filter_glob = StringProperty(default="*.py", options={'HIDDEN'})

	vfunc = 'bgl.glVertex3f'
	nfunc = 'bgl.glNormal3f'
	preamble = "import bgl\n\ndef %s():\n\tshapelist = bgl.glGenLists(1)\n\tbgl.glNewList(shapelist, bgl.GL_COMPILE)\n\tbgl.glBegin(bgl.GL_TRIANGLES)\n"
	postamble= "\tbgl.glEnd()\n\tbgl.glEndList()\n\treturn shapelist"

	def execute(self, context):
		mesh = context.object.data
		bm = bmesh.new()
		bm.from_mesh(mesh)
		bm.calc_tessface()
		bmesh.ops.triangulate(bm, faces=bm.faces)
		bm.normal_update()

		with open(self.filepath,'w') as f:
			f.write(self.preamble % mesh.name)
			for face in bm.faces:
				for v in face.verts:
					f.write('\t%s(%.4f,%4f,%4f)\n' % (self.nfunc, v.normal.x, v.normal.y, v.normal.z))
					f.write('\t%s(%.4f,%4f,%4f)\n' % (self.vfunc, v.co.x, v.co.y, v.co.z))
			f.write(self.postamble)

		bm.free()
		return {'FINISHED'}

def menu_func(self, context):
	self.layout.operator(ExportOpenGL.bl_idname, text=ExportOpenGL.bl_label, icon='PLUGIN')

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
	bpy.types.INFO_MT_file_export.remove(menu_func)
	bpy.utils.unregister_module(__name__)
