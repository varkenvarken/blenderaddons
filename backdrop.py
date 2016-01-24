# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Backdrop.py , a Blender addon to create a backdrop that fits the active camera.
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
	"name": "BackDrop",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 201601241147),
	"blender": (2, 76, 0),
	"location": "View3D > Add > Backdrop",
	"description": "Create a backdrop that completely fits the view from the active camera",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Add Mesh"}

from math import radians
import bpy
import bmesh
from bpy.props import IntProperty, FloatProperty, BoolProperty
from mathutils import Vector, Quaternion
from mathutils.geometry import interpolate_bezier


class BackDrop(bpy.types.Operator):
	bl_idname = "mesh.backdrop"
	bl_label = "BackDrop"
	bl_options = {'REGISTER', 'UNDO'}

	margin 		= FloatProperty(name="Camera Margin",	default=0.0,
		description="Add extra margin to the visual area from te camera (might be negative as well).")

	lift 		= FloatProperty(name="Lift",			default=0.0,
		description="Elevation of far edge of backdrop")

	distance 	= FloatProperty(name="Level",			default=2.0,
		description="Distance below camera")

	zero 		= BoolProperty (name="Zero level",		default=True,
		description="Position backdrop at z = 0")

	angle 		= FloatProperty(name="Curvature",		default=radians(0), subtype='ANGLE', precision=0,
		description="Curvature of backdrop with non-zero Lift")

	subdivisions= IntProperty  (name="Subdivisions",	default=5, min=0, soft_max=20,
		description="Number of subdivisions in backdrop grid")

	@classmethod
	def poll(self, context):
		return (context.mode == 'OBJECT') and (context.scene.camera is not None)

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.prop(self, 'zero')
		if not self.zero:
			row.prop(self, 'distance')
		layout.prop(self, 'margin')
		layout.prop(self, 'lift')
		layout.prop(self, 'angle')
		layout.prop(self, 'subdivisions')
		if self.impossible:
			box = layout.box()
			box.enabled = False
			box.label("Impossible to create a backdrop, uncheck zero level?")

	def backdrop(self, context):
		# calculate the view frame in world coordinates
		# (i.e. the far plane of the view frustum)
		scene = context.scene
		cam_ob = scene.camera
		cam = bpy.data.cameras[cam_ob.name] # camera in scene is object type, not a camera type
		cam_mat = cam_ob.matrix_world
		view_frame = cam.view_frame(scene)	# without a scene the aspect ratio of the camera is not taken into account
		view_frame = [cam_mat * v for v in view_frame]
		cam_pos = cam_mat * Vector((0,0,0))
		view_center = sum(view_frame, Vector((0,0,0)))/len(view_frame)
		view_normal = (view_center - cam_pos).normalized()

		# enlarge the view frame beyond the actual cam boundaries if requested
		if self.margin != 0.0:
			view_frame = [((v - view_center)*(1+self.margin))+view_center for v in view_frame]

		# calculate the intersection with a horizontal plane below the camera
		# the top edge is intersected with an artificially offset ground plane
		# so it will intersected with the lifted far end of our backdrop
		overts = []
		refz = cam_pos.z if self.zero else self.distance
		for n,vf in enumerate(view_frame):
			v = (vf - cam_pos).normalized()
			d = 0.0 if n in (1,2) else self.lift
			zf =  (d - refz) / v.z
			if zf <= 0.0 :
				break
			overts.append(zf * v)

		# create two edge loops (the right and left side of the intersection
		# of the view frustum with the backdrop). We curve it downward we a
		# bezier interpolation. This curvature can be controlled somewhat
		# with a rotation angle but this is far from ideal yet
		verts = []
		edges = []

		vs = Vector(overts[2])
		ve = Vector(overts[3])
		rotaxis = (vs - ve).cross(Vector((0,0,-1))).normalized()
		rot = Quaternion(rotaxis, self.angle)
		handle2 = ve + rot * Vector((0,0,-self.lift))
		handle1 = vs + (vs - ve).normalized()
		points = interpolate_bezier(vs, handle1, handle2, ve, self.subdivisions+1)

		verts.extend(points)
		edges.extend((i,i+1) for i in range(len(points)-1))

		vs = Vector(overts[0])
		ve = Vector(overts[1])
		rotaxis = (ve - vs).cross(Vector((0,0,-1))).normalized()
		rot = Quaternion(rotaxis, self.angle)
		handle2 = ve + (ve - vs).normalized()
		handle1 = vs + rot * Vector((0,0,-self.lift))
		points = interpolate_bezier(ve, handle2, handle1, vs, self.subdivisions+1)
		points.reverse()

		offset = len(verts)
		verts.extend(points)
		edges.extend((offset+i,offset+i+1) for i in range(len(points)-1))

		return verts, edges


	def execute(self, context):
		verts, edges = self.backdrop(context)

		# it is possible that the camera points upward and we cannot 
		# create a backdrop. In that scenario no verts are returned and
		# we signal something in the user interface.
		self.impossible = True

		if len(verts):
			self.impossible = False

			# create an empty mesh object
			mesh = bpy.data.meshes.new("BackDrop")
			ob = bpy.data.objects.new("BackDrop", mesh)

			context.scene.objects.link(ob)
			context.scene.update()
			context.scene.objects.active = ob
			ob.select = True

			# create a new empty bmesh and fill it with our geometry
			bm = bmesh.new()

			for v in verts:
				bm.verts.new(v)
			bm.verts.ensure_lookup_table()

			for e1,e2 in edges:
				bm.edges.new((bm.verts[e1],bm.verts[e2]))
			bm.edges.ensure_lookup_table()

			# bridge the two edgeloops and subdivide the new edges
			geom = bmesh.ops.bridge_loops(bm, edges=bm.edges[:])
			bmesh.ops.subdivide_edges(bm, edges=geom['edges'], cuts=self.subdivisions)

			# transfer to mesh object 
			bm.to_mesh(mesh)
			bm.free()
			mesh.update()

			# add a subsurf modifier
			bpy.ops.object.shade_smooth()
			mod = ob.modifiers.new(name='Subsurf', type='SUBSURF')
			mod.levels = 2
			mod.render_levels = 2

			# set the location of the backdrop to coincide with the camera
			# and parent it to the cam as well so it will move with it
			ob.location = context.scene.camera.location
			context.scene.objects.active = context.scene.camera
			bpy.ops.object.parent_set(type='OBJECT')
			context.scene.objects.active = ob

		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(BackDrop.bl_idname, text="Backdrop",
						icon='PLUGIN')


def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_add.append(menu_func)


def unregister():
	bpy.types.INFO_MT_add.remove(menu_func)
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
	
