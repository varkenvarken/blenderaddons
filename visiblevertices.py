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
	"version": (0, 0, 3),
	"blender": (2, 70, 0),
	"location": "View3D > Weight Paint > Weights > Visible Vertices",
	"description": "Replace active vertex group with weight > 0.0 if visible from active camera, 0.0 otherwise",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Mesh"}

import bpy
from bpy.props import BoolProperty, FloatProperty
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri

def intersect_ray_quad_3d(quad, origin, destination):
	ray = destination - origin
	p = intersect_ray_tri(quad[0],quad[1],quad[2],ray,origin)
	if p is None:
		p = intersect_ray_tri(quad[2],quad[3],quad[0],ray,origin)
	return p

def intersect_ray_scene(scene, origin, destination):
	direction = destination - origin
	result, object, matrix, location, normal = scene.ray_cast(origin + direction*0.0001, destination)
	if result:
		if object.type == 'Camera': # if have no idea if a camera can return true but just to play safe
			result = False
	return result		
	
class VisibleVertices(bpy.types.Operator):
	bl_idname = "mesh.visiblevertices"
	bl_label = "VisibleVertices"
	bl_options = {'REGISTER', 'UNDO'}

	fullScene = BoolProperty(name="Full Scene", default=True, description="Check wether the view is blocked by objects in the scene.")
	distWeight = BoolProperty(name="Distance Weight", default=True, description="Give less weight to vertices further away from the camera.")
	addModifier = BoolProperty(name="Add Modifier", default=True, description="Add a vertex weight modifier for additional control.")
	margin = FloatProperty(name="Camera Margin", default=0.0, description="Add extra margin to the visual area from te camera (might be negative as well).")

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

		if self.margin != 0.0:
			view_frame = [((v - view_center)*(1+self.margin))+view_center for v in view_frame] 
		
		mesh_mat = ob.matrix_world
		mesh = ob.data
		distances = []
		max_distance = 0
		min_distance = None
		for v in mesh.vertices:
			vertex_coords = mesh_mat * v.co
			d = None
			intersection = intersect_ray_quad_3d(view_frame, vertex_coords, cam_pos) # check intersection with the camera frame
			#print(intersection, end=" | ")
			if intersection is not None:
				d = (intersection - vertex_coords)
				if d.dot(view_normal) < 0: # only take into account vertices in front of the camera, not behind it.
					d = d.length
					if self.fullScene:
						if intersect_ray_scene(scene, vertex_coords, cam_pos):	# check intersection with all other objects in scene. We revert the direction, ie. look from the camera to avoid self intersection
							d = None
				else:
					d = None
			if d is not None:
				if d > max_distance :
					max_distance = d
				if min_distance is None or d < min_distance:
					min_distance = d
			distances.append((v.index, d))

		drange = max_distance - min_distance if min_distance is not None else max_distance # prevent exception if the was not a single visible vertex
		#print(min_distance, max_distance, drange)
		if self.distWeight and drange > 1e-7:
			#print("weighted")
			for vindex, d in distances:
				#print(d, end=' ')
				if d is None:
					vertex_group.add([vindex], 0.0, 'REPLACE')
				else:
					vertex_group.add([vindex], 1.0 - ((d - min_distance) / drange), 'REPLACE')
		else:
			#print("not weighted")
			for vindex, d in distances:
				#print(d, end='')
				if d is None:
					vertex_group.add([vindex], 0.0, 'REPLACE')
				else:
					vertex_group.add([vindex], 1.0 if d > 0.0 else 0.0, 'REPLACE')

		bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
		context.scene.update()
		
		if self.addModifier:
			bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_EDIT')
			ob.modifiers[-1].vertex_group = ob.vertex_groups.active.name
			ob.modifiers[-1].falloff_type = 'CURVE'
			# make modifier panel visible to atract some attention because this is a lesser known modifier
			ws = context.window_manager.windows
			for a in ws[0].screen.areas:
				if(a.type == 'PROPERTIES'):
					for s in a.spaces:
						if s.type == 'PROPERTIES':
							s.context = 'MODIFIER'

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
	