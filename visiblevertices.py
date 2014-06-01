# ##### BEGIN GPL LICENSE BLOCK #####
#
#  VisibleVertices.py , a Blender addon to weight paint vertices visible from the active camera.
#  (c) 2014 Michel J. Anders (varkenvarken)
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

# <pep8 compliant>

bl_info = {
	"name": "VisibleVertices",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 1),
	"blender": (2, 70, 0),
	"location": "View3D > Object > Visible Vertices",
	"description": "Replace active vertex group with weight = 1.0 if visible from active camera, 0.0 otherwise",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Mesh"}

import bpy
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri

def intersect_ray_quad_3d(quad, origin, destination):
	ray = destination - origin
	p = intersect_ray_tri(quad[0],quad[1],quad[2],ray,origin)
	if p is None:
		p = intersect_ray_tri(quad[2],quad[3],quad[0],ray,origin)
	return p
	
class VisibleVertices(bpy.types.Operator):
	bl_idname = "mesh.visiblevertices"
	bl_label = "VisibleVertices"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(self, context):
		p = (context.mode == 'PAINT_WEIGHT' and
			isinstance(context.scene.objects.active, bpy.types.Object) and
			isinstance(context.scene.objects.active.data, bpy.types.Mesh))
		return p
		
	def execute(self, context):
		bpy.ops.object.mode_set(mode='OBJECT')

		ob = context.active_object
		vertex_group = ob.vertex_groups.active
		if vertex_group is None:
			bpy.ops.object.vertex_group_add()
			vertex_group = ob.vertex_groups.active
		scene = context.scene
		cam_ob = scene.camera
		cam = bpy.data.cameras[cam_ob.name] # camera in scene is object type, not a camera type
		cam_mat = cam_ob.matrix_world
		view_frame = cam.view_frame(scene)	# without a scene the aspect ratio of the camera is not taken into account
		view_frame = [cam_mat * v for v in view_frame]
		cam_pos = cam_mat * Vector((0,0,0))
		view_center = sum(view_frame, Vector((0,0,0)))/len(view_frame)
		view_normal = (view_center - cam_pos).normalized()

		mesh_mat = ob.matrix_world
		mesh = ob.data
		for v in mesh.vertices:
			vertex_coords = mesh_mat * v.co
			intersection = intersect_ray_quad_3d(view_frame, vertex_coords, cam_pos)
			weight = 0.0 if intersection is None else 1.0
			vertex_group.add([v.index], weight, 'REPLACE')

		bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
		context.scene.update()
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(VisibleVertices.bl_idname, text="Visible Vertices",
						icon='PLUGIN')


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_paint_weight.append(menu_func)


def unregister():
	bpy.types.VIEW3D_MT_paint_weight.remove(menu_func)
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
	