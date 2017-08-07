# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Snap and transform, a Blender addon
#  (c) 2017 Michel J. Anders (varkenvarken)
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

import bpy

bl_info = {
	"name": "Snap and transform",
	"author": "michel anders (varkenvarken)",
	"version": (0, 0, 201708071053),
	"blender": (2, 78, 0),
	"location": "View3D > Mesh > Snap > Snap and transform",
	"description": "Snap cursor to selected geometry and move origin to same position",
	"warning": "",
	"wiki_url": "http://blenderthings.blogspot.com/",
	"tracker_url": "",
	"category": "Mesh"}


class SnapAndTransform(bpy.types.Operator):

	bl_idname = "mesh.select_and_transform"
	bl_label = "SnapAndTransform"
	bl_description = "Snap cursor to selected geometry and move origin to same position"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(self, context):
		return (context.mode == 'EDIT_MESH')

	def execute(self, context):
		# we could do all the calculations ourselves but just calling
		# the available operators is way simpler and that is what code
		# reuse is about :-)
		bpy.ops.view3d.snap_cursor_to_selected()
		bpy.ops.object.editmode_toggle()
		bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
		bpy.ops.object.editmode_toggle()
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.separator()
	self.layout.operator(SnapAndTransform.bl_idname, text="Snap and transform")


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_snap.append(menu_func)


def unregister():
	bpy.types.VIEW3D_MT_snap.remove(menu_func)
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
