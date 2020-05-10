# ##### BEGIN GPL LICENSE BLOCK #####
#
#  facearea.py , a Blender addon to calculate vertex colors based on face area.
#  (c) 2020 Michel J. Anders (varkenvarken)
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
	"name": "facearea",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 202005101258),
	"blender": (2, 83, 0),
	"location": "View3D > Vertex Paint > Weights > WeightLifter",
	"description": "",
	"warning": "",
	"wiki_url": "",
	"category": "Paint"}

import numpy as np
import bpy
import bmesh


class FaceArea(bpy.types.Operator):
	bl_idname = "paint.facearea"
	bl_label = "Face Area"
	bl_description = "Calculate vertex colors based on face area"
	bl_options = {'REGISTER', 'UNDO'}


	@classmethod
	def poll(self, context):
		"""
		Only visible in vertex paint mode if the active object is a mesh and has at least one vertex color layer
		"""
		p = (context.mode == 'PAINT_VERTEX' and
			isinstance(context.object, bpy.types.Object) and
			isinstance(context.object.data, bpy.types.Mesh) and
			len(context.object.data.vertex_colors)
			)
		return p

	def execute(self, context):
		bpy.ops.object.mode_set(mode='OBJECT')

		scene = context.scene
		self.ob = context.active_object
		mesh = context.object.data

		vertex_colors = mesh.vertex_colors.active.data

		areamap = {loop:f.area for f in mesh.polygons for loop in range(f.loop_start, f.loop_start + f.loop_total)}
		maxarea = max(areamap.values())
		print(maxarea)
		for i,area in areamap.items():
			w=area/maxarea
			vertex_colors[i].color[:3] = (w,w,w)

		bpy.ops.object.mode_set(mode='VERTEX_PAINT')
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.object.mode_set(mode='VERTEX_PAINT')

		return {'FINISHED'}


def menu_func_vcol(self, context):
	self.layout.operator(FaceArea.bl_idname,icon='PLUGIN')

classes = (FaceArea, )

register_classes, unregister_classes = bpy.utils.register_classes_factory(classes)

def register():
	register_classes()
	bpy.types.VIEW3D_MT_paint_vertex.append(menu_func_vcol)

def unregister():
	bpy.types.VIEW3D_MT_paint_vertex.remove(menu_func_vcol)
	unregister_classes()

if __name__ == "__main__":
	register()
