# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Edit mode origin tools, a Blender addon
#  (c) 2017,2018 Michel J. Anders (varkenvarken)
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
import numpy as np
from bpy.props import BoolProperty

bl_info = {
	"name": "Edit mode origin tools",
	"author": "michel anders (varkenvarken)",
	"version": (0, 0, 201803310907),
	"blender": (2, 79, 0),
	"location": "View3D > Mesh > Snap",
	"description": "Move origin to selected geometry and to lowest point in mesh",
	"warning": "",
	"wiki_url": "http://blenderthings.blogspot.com/",
	"tracker_url": "",
	"category": "Mesh"}


class OriginToSelected(bpy.types.Operator):
	'''Move origin to selected geometry'''
	bl_idname = "mesh.editmode_origin_to_selected"
	bl_label = "OriginToSelected"
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

class OriginToLowest(bpy.types.Operator):
	'''Move origin to lowest point in mesh'''
	bl_idname = "mesh.editmode_origin_to_lowest"
	bl_label = "OriginToLowest"
	bl_description = "Move the origin to lowest point"
	bl_options = {'REGISTER', 'UNDO'}

	center = BoolProperty(name='Center', default=True, description='lowest on z-axis but also centered below the center')

	@classmethod
	def poll(self, context):
		return ((context.mode == 'EDIT_MESH' or context.mode == 'OBJECT' )and context.active_object.type == 'MESH')

	def execute(self, context):
		if context.mode == 'EDIT_MESH':
			bpy.ops.object.editmode_toggle()
		me = context.active_object.data
		count = len(me.vertices)
		if count > 0:  # degenerate mesh, but better safe than sorry
			# get the vertex coords
			shape = (count, 3)
			verts = np.empty(count*3, dtype=np.float32)
			me.vertices.foreach_get('co', verts)
			verts.shape = shape
			# add a w coord of 1 by copying xyz over a xyzw array of all ones, because world matrix is 4x4
			verts2 = np.ones((count,4))
			verts2[:,:3] = verts
			# multiply with world matrix to get world coords
			M = np.array(context.active_object.matrix_world, dtype=np.float32)
			verts = (M @ verts2.T).T[:,:3]  # remember @ is the new python matrix multiplicator that numpy supports the double transpose is to get the 4 x 1 vectors to 1 x 4
			# get coords of vertex with lowest z value
			min_co = verts[np.argsort(verts[:,2])[0]]
			# replace x,y coordinates by center coords if selected
			if self.center:
				# get the center of all the transformed vertices
				center = np.average(verts, axis=0)
				# replace the x,y coords
				min_co[0:2] = center[0:2]
			context.scene.cursor_location = min_co
			bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
		if context.mode == 'EDIT_MESH':
			bpy.ops.object.editmode_toggle()
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.separator()
	self.layout.operator(OriginToSelected.bl_idname, text="Origin to selected")
	self.layout.operator(OriginToLowest.bl_idname, text="Origin to lowest point (World Z-axis)").center = False
	self.layout.operator(OriginToLowest.bl_idname, text="Origin to lowest point (World Z-axis, centered)").center = True


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_snap.append(menu_func)


def unregister():
	bpy.types.VIEW3D_MT_snap.remove(menu_func)
	bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
	register()
