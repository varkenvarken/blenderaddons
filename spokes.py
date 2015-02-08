# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Spokes, a Blender addon to demonstrate parametric object
#  (c) 2015 Michel J. Anders (varkenvarken)
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
	"name": "Spokes",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 20150208),
	"blender": (2, 73, 0),
	"location": "View3D > Add > Mesh",
	"description": "Add an object with a configurable number of spokes",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Add Mesh"}

from math import pi
import bpy
from bpy.props import IntProperty, StringProperty
from mathutils import Vector, Euler


# Vector.rotate() does NOT return anything, contrary to what the docs say
# docs are now fixed (https://projects.blender.org/tracker/index.php?func=detail&aid=36518&group_id=9&atid=498)
# but unfortunately no rotated() function was added
def rotate(v, r):
	v2 = v.copy()
	v2.rotate(r)
	return v2

def spokes(n):
	up = Vector((0,1,0))
	angle = Euler((0,0,2*pi/float(n)),'XYZ')
	angle2 = Euler((0,0,pi/float(n)),'XYZ')
	of = rotate(up, angle2)
	
	verts = []
	for i in range(n):
		verts.append(up.copy())
		verts.append(up+of)
		up = rotate(up, angle)
		verts.append(up+of)
		of = rotate(of, angle)
		
	faces = []
	for i in range(n):
		faces.append((3*i,3*i+1,3*i+2,(3*i+3) % (n*3)))
	
	return verts, faces

def spokest(n):
	return [Vector((0,0,0)),Vector((0,1,0)),Vector((1,1,0))],[(0,1,2)]
	
def updateMesh(self, context):
	o = context.object

	verts, faces = spokes(o.numberofspokes)

	# create mesh &link object to scene
	emesh = o.data

	mesh = bpy.data.meshes.new(name='Spokes')
	mesh.from_pydata(verts, [], faces)

	mesh.update(calc_edges=True)

	for i in bpy.data.objects:
		if i.data == emesh:
			i.data = mesh

	name = emesh.name
	emesh.user_clear()
	bpy.data.meshes.remove(emesh)
	mesh.name = name
	if bpy.context.mode != 'EDIT_MESH':
		bpy.ops.object.editmode_toggle()
		bpy.ops.object.editmode_toggle()

bpy.types.Object.reg = StringProperty()

bpy.types.Object.numberofspokes = IntProperty(name="Number of spokes",
									description="Number of spokes",
									default=6,
									min=2,
									soft_max=50,
									update=updateMesh)

class Spokes(bpy.types.Panel):
	bl_idname = "Spokes"
	bl_label = "Spokes"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "modifier"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		if bpy.context.mode == 'EDIT_MESH':
			layout.label('Spokes doesn\'t work in the EDIT-Mode.')
		else:
			o = context.object
			if 'reg' in o:
				if o['reg'] == 'Spokes':
					box = layout.box()
					box.prop(o, 'numberofspokes')
				else:
					layout.operator('mesh.spokes_convert')
			else:
				layout.operator('mesh.spokes_convert')

class SpokesAdd(bpy.types.Operator):
	bl_idname = "mesh.spokes_add"
	bl_label = "Spokes"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(self, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		bpy.ops.mesh.primitive_cube_add()
		context.active_object.name = "Spokes"
		bpy.ops.mesh.spokes_convert('INVOKE_DEFAULT')
		return {'FINISHED'}

class SpokesConvert(bpy.types.Operator):
	bl_idname = 'mesh.spokes_convert'
	bl_label = 'Convert to Spokes object'
	bl_options = {"UNDO"}

	def invoke(self, context, event):
		o = context.object
		o.reg = 'Spokes'
		o.numberofspokes = 6 # assigning something forces call to updateMesh()
		return {"FINISHED"}

def menu_func(self, context):
	self.layout.operator(SpokesAdd.bl_idname, text="Add spokes mesh",
						icon='PLUGIN')

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
	bpy.types.INFO_MT_mesh_add.remove(menu_func)
	bpy.utils.unregister_module(__name__)
