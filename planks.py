# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Floor Generator, a Blender addon
#  (c) 2013 Michel J. Anders (varkenvarken)
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
	"name": "Floor Generator",
	"author": "Michel Anders (varkenvarken) with contributions from Alain (Alain) and Floric (floric)",
	"version": (0, 0, 15),
	"blender": (2, 71, 0),
	"location": "View3D > Add > Mesh",
	"description": "Adds a mesh representing floor boards (planks)",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Add Mesh"}

from random import random as rand, seed, uniform as randuni
from math import pi as PI
import bpy
import bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, StringProperty
from mathutils import Vector, Euler


# Vector.rotate() does NOT return anything, contrary to what the docs say
# docs are now fixed (https://projects.blender.org/tracker/index.php?func=detail&aid=36518&group_id=9&atid=498)
# but unfortunately no rotated() function was added
def rotate(v, r):
	v2 = v.copy()
	v2.rotate(r)
	return v2

available_meshes = [(' None ','None',"")]

def availableMeshes(self, context):
	available_meshes.clear()
	for ob in bpy.data.objects:
		if ob.type == 'MESH' and ob.name != context.active_object.name:
			name = ob.name[:]
			available_meshes.append((name, name, ""))
	if(len(available_meshes)==0):
		available_meshes.append((' None ','None',"There appear to be no mesh objects in this scene"))
	return available_meshes
		
def plank(start, end, left, right, longgap, shortgap, rot=None):
	ll = Vector((start, left, 0))
	lr = Vector((start, right - longgap, 0))
	ul = Vector((end - shortgap, right - longgap, 0))
	ur = Vector((end - shortgap, left, 0))
	if rot:
		midpoint = Vector(((start + end)/2.0, (left + right)/ 2.0, 0))
		ll = rotate((ll - midpoint), rot) + midpoint
		lr = rotate((lr - midpoint), rot) + midpoint
		ul = rotate((ul - midpoint), rot) + midpoint
		ur = rotate((ur - midpoint), rot) + midpoint
	verts = (ll, lr, ul, ur)
	return verts


def planks(n, m,
		length, lengthvar,
		width, widthvar,
		longgap, shortgap,
		offset, randomoffset,
		nseed,
		randrotx, randroty, randrotz):

	#n=Number of planks, m=Floor Length, length = Planklength

	verts = []
	faces = []
	shortedges = []
	longedges = []

	seed(nseed)
	widthoffset = 0
	s = 0
	e = offset
	c = offset  # Offset per row
	ws = 0
	p = 0

	while p < n:
		p += 1
		w = width + randuni(0, widthvar)
		we = ws + w
		if randomoffset:
			e = randuni(4 * shortgap, length)  # we don't like negative plank lengths
		while (m - e) > (4 * shortgap):
			ll = len(verts)
			rot = Euler((randrotx * randuni(-1, 1), randroty * randuni(-1, 1), randrotz * randuni(-1, 1)), 'XYZ')
			verts.extend(plank(s, e, ws, we, longgap, shortgap, rot))
			faces.append((ll, ll + 1, ll + 2, ll + 3))
			shortedges.extend([(ll, ll + 1), (ll + 2, ll + 3)])
			longedges.extend([(ll + 1, ll + 2), (ll + 3, ll)])
			s = e
			e += length + randuni(0, lengthvar)
		ll = len(verts)
		rot = Euler((randrotx * randuni(-1, 1), randroty * randuni(-1, 1), randrotz * randuni(-1, 1)), 'XYZ')
		verts.extend(plank(s, m, ws, we, longgap, shortgap, rot))
		faces.append((ll, ll + 1, ll + 2, ll + 3))
		shortedges.extend([(ll, ll + 1), (ll + 2, ll + 3)])
		longedges.extend([(ll + 1, ll + 2), (ll + 3, ll)])
		s = 0
		#e = e - m
		if c <= (length):
			c = c + offset
		if c > (length):
			c = c - length
		e = c
		ws = we
	return verts, faces, shortedges, longedges


def shortside(vert):
	"""return true if 2 out of 3 connected vertices are x aligned"""
	x = vert.co.x
	n = 0
	for e in vert.link_edges:
		xo = e.other_vert(vert).co.x
		if abs(xo - x) < 1e-4:
			n += 1
	return n == 2


def updateMesh(self, context):
	o = context.object

	verts, faces, shortedges, longedges = planks(o.nplanks, o.length,
												o.planklength, o.planklengthvar,
												o.plankwidth, o.plankwidthvar,
												o.longgap, o.shortgap,
												o.offset, o.randomoffset,
												o.randomseed,
												o.randrotx, o.randroty, o.randrotz)

	# create mesh &link object to scene
	emesh = o.data

	mesh = bpy.data.meshes.new(name='Planks')
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

	bpy.ops.object.shade_smooth()

	# add uv-coords and per face random vertex colors
	mesh.uv_textures.new()
	uv_layer = mesh.uv_layers.active.data
	vertex_colors = mesh.vertex_colors.new().data
	for poly in mesh.polygons:
		offset = Vector((rand(), rand(), 0)) if o.randomuv else Vector((0, 0, 0))
		color = [rand(), rand(), rand()]
		for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
			coords = mesh.vertices[mesh.loops[loop_index].vertex_index].co
			uv_layer[loop_index].uv = (coords + offset).xy
			vertex_colors[loop_index].color = color

	# subdivide mesh and warp it
	warped = o.hollowlong > 0 or o.hollowshort > 0 or o.twist > 0
	if warped:
		bm = bmesh.new()
		bm.from_mesh(mesh)

		# calculate hollowness for each face
		dshortmap = {}
		dlongmap = {}
		for face in bm.faces:
			dshort = o.hollowshort * rand()
			dlong = o.hollowlong * rand()
			for v in face.verts:
				dshortmap[v.index] = dshort
				dlongmap[v.index] = dlong

		bm.to_mesh(mesh)
		bm.free()

		# at this point all new geometry is selected and subdivide works in all selection modes
		bpy.ops.object.editmode_toggle()
		bpy.ops.mesh.subdivide()  # bmesh subdivide doesn't work for me ...
		bpy.ops.object.editmode_toggle()

		bm = bmesh.new()
		bm.from_mesh(mesh)

		for v in bm.verts:
			if o.twist and len(v.link_edges) == 4:  # vertex in the middle of the plank
				dtwist = o.twist * randuni(-1, 1)
				for e in v.link_edges:
					v2 = e.other_vert(v)  # the vertices on the side of the plank
					if shortside(v2):
						for e2 in v2.link_edges:
							v3 = e2.other_vert(v2)
							if len(v3.link_edges) == 2:
								v3.co.z += dtwist
								dtwist = -dtwist  # one corner up, the other corner down
			elif len(v.link_edges) == 3:  # vertex in the middle of a side of the plank
				for e in v.link_edges:
					v2 = e.other_vert(v)
					if len(v2.link_edges) == 2:  # hollowness values are stored with the all original corner vertices
						dshort = dshortmap[v2.index]
						dlong = dlongmap[v2.index]
						break
				if shortside(v):
					v.co.z -= dlong
				else:
					v.co.z -= dshort

		creases = bm.edges.layers.crease.new()
		for edge in bm.edges:
			edge[creases] = 1
			for vert in edge.verts:
				if len(vert.link_edges) == 4:
					edge[creases] = 0
					break

		bm.to_mesh(mesh)
		bm.free()

	
	# remove all modifiers to make sure the boolean will be last & only modifier
	n = len(o.modifiers)
	while n > 0:
		n -= 1
		bpy.ops.object.modifier_remove(modifier=o.modifiers[-1].name)
	
	# add thickness
	# simply extruding would be simpler and cheaper but we get a warning convertViewVec: called in an invalid context
	# overriding the context of the operator to explicitly set the area crashes Blender, which is a known bug
	# http://blenderartists.org/forum/showthread.php?338387-addon-related-to-System-console-tells-me-quot-convertViewVec-called-in-an-invalid-contex
	# so we opt for the add-solidify-modifier-and-apply approach even though it's just a warning.
	#bpy.ops.object.editmode_toggle()
	#bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={'value':(0,0,self.thickness)})
	#bpy.ops.mesh.select_all(action='SELECT')
	#bpy.ops.mesh.normals_make_consistent(inside=False)
	#bpy.ops.object.editmode_toggle()
	bpy.ops.object.modifier_add(type='SOLIDIFY')
	o.modifiers[-1].thickness = self.thickness
	bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")
	bpy.ops.object.editmode_toggle()
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.normals_make_consistent(inside=False)
	bpy.ops.object.editmode_toggle()
	
	# intersect with a floorplan
	if self.usefloorplan and self.floorplan != ' None ':
		# make the floorplan the only active an selected object
		bpy.ops.object.select_all(action='DESELECT')
		context.scene.objects.active = bpy.data.objects[self.floorplan]
		bpy.data.objects[self.floorplan].select = True

		# duplicate the selected geometry into a separate object
		me = context.scene.objects.active.data
		selected_faces = [p.index for p in me.polygons if p.select]
		bpy.ops.object.editmode_toggle()
		bpy.ops.mesh.duplicate()
		bpy.ops.mesh.separate()
		bpy.ops.object.editmode_toggle()
		me = context.scene.objects.active.data
		for i in selected_faces:
			me.polygons[i].select = True

		# now there will be two selected objects
		# the one with the new name will be the copy
		for ob in context.selected_objects:
			if ob.name != self.floorplan:
				fpob = ob
		print('floorplan copy',fpob.name)
		
		# make that copy active and selected
		for ob in context.selected_objects:
			ob.select = False
		fpob.select = True
		context.scene.objects.active = fpob
		
		if True:
			# add thickness
			# let normals of select faces point in same direction
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.mesh.normals_make_consistent(inside=False)
			bpy.ops.object.editmode_toggle()
			# add solidify modifier
			# NOTE: for some reason bpy.ops.object.modifier_add doesn't work here
			# even though fpob at this point is verifyable the active and selected object ...
			mod = fpob.modifiers.new(name='Solidify', type='SOLIDIFY')
			mod.offset = 1.0 # in the direction of the normals
			mod.thickness = 2000 # very thick
			bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Solidify")
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.mesh.normals_make_consistent(inside=False)
			bpy.ops.object.editmode_toggle()
			fpob.location -= Vector((0,0,1000)) # actually this should be in the negative direction of the normals not just plain downward...
			
			# make the floorboards active and selected
			for ob in context.selected_objects:
				ob.select = False
			context.scene.objects.active = o
			o.select = True
			
			# add-and-apply a boolean modifier to get the intersection with the floorplan copy
			bpy.ops.object.modifier_add(type='BOOLEAN') # default is intersect
			o.modifiers[-1].object = fpob
			bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")
			# delete the copy
			bpy.ops.object.select_all(action='DESELECT')
			context.scene.objects.active = fpob
			fpob.select = True
			bpy.ops.object.delete()
			# make the floorboards active and selected
			context.scene.objects.active = o
			o.select = True
		
	if self.modify:
		mods = o.modifiers
		if len(mods) == 0: # always true
			bpy.ops.object.modifier_add(type='BEVEL')
			bpy.ops.object.modifier_add(type='EDGE_SPLIT')
			mods = o.modifiers
			mods[0].show_expanded = False
			mods[1].show_expanded = False
			mods[0].width = self.bevel
		if warped and not ('SUBSURF' in [m.type for m in mods]):
			bpy.ops.object.modifier_add(type='SUBSURF')
			mods[-1].show_expanded = False
			mods[-1].levels = 2
		if not warped and ('SUBSURF' in [m.type for m in mods]):
			bpy.ops.object.modifier_remove(modifier='Subsurf')

bpy.types.Object.reg = StringProperty(default='FloorBoards')

bpy.types.Object.length = FloatProperty(name="Floor Area Length",
										description="Length of the floor in Blender units",
										default=4,
										soft_min=0.5,
										soft_max=40.0,
										subtype='DISTANCE',
										unit='LENGTH',
										update=updateMesh)

bpy.types.Object.nplanks = IntProperty(name="Number of rows",
									description="Number of rows (the width)",
									default=5,
									soft_min=1,
									soft_max=50,
									update=updateMesh)

bpy.types.Object.planklength = FloatProperty(name="Plank Length",
											description="Length of a single plank",
											default=2,
											soft_min=0.5,
											soft_max=40.0,
											subtype='DISTANCE',
											unit='LENGTH',
											update=updateMesh)

bpy.types.Object.planklengthvar = FloatProperty(name="Max Length Var",
												description="Max Length variation of single planks",
												default=0.2,
												min=0,
												soft_max=40.0,
												subtype='DISTANCE',
												unit='LENGTH',
												update=updateMesh)

bpy.types.Object.plankwidth = FloatProperty(name="Plank Width",
											description="Width of a single plank",
											default=0.18,
											soft_min=0.05,
											soft_max=40.0,
											subtype='DISTANCE',
											unit='LENGTH',
											update=updateMesh)

bpy.types.Object.plankwidthvar = FloatProperty(name="Max Width Var",
											description="Max Width variation of single planks",
											default=0,
											min=0,
											soft_max=4.0,
											subtype='DISTANCE',
											unit='LENGTH',
											update=updateMesh)

bpy.types.Object.longgap = FloatProperty(name="Long Gap",
										description="Gap between long edges of planks",
										default=0.002,
										min=0,
										soft_max=0.01,
										step=0.01,
										precision=4,
										subtype='DISTANCE',
										unit='LENGTH',
										update=updateMesh)

bpy.types.Object.shortgap = FloatProperty(name="Short Gap",
										description="Gap between short edges of planks",
										default=0.0005,
										min=0,
										soft_max=0.01,
										step=0.01,
										precision=4,
										subtype='DISTANCE',
										unit='LENGTH',
										update=updateMesh)

bpy.types.Object.thickness = FloatProperty(name="Thickness",
										description="Thickness of planks",
										default=0.018,
										soft_max=0.1,
										soft_min=0.008,
										step=0.1,
										precision=3,
										subtype='DISTANCE',
										unit='LENGTH',
										update=updateMesh)

bpy.types.Object.bevel = FloatProperty(name="Bevel",
									description="Bevel width planks",
									default=0.001,
									min=0,
									soft_max=0.01,
									step=0.01,
									precision=4,
									subtype='DISTANCE',
									unit='LENGTH',
									update=updateMesh)

bpy.types.Object.offset = FloatProperty(name="Offset",
										description="Offset per row in Blender Units",
										default=0.4,
										min=0,
										soft_max=2,
										subtype='DISTANCE',
										unit='LENGTH',
										update=updateMesh)

bpy.types.Object.randomoffset = BoolProperty(name="Offset random",
											description="Uses random values for offset",
											default=True,
											update=updateMesh)

bpy.types.Object.randomseed = IntProperty(name="Random Seed",
										description="The seed governing random generation",
										default=0,
										min=0,
										update=updateMesh)

bpy.types.Object.randomuv = BoolProperty(name="Randomize UVs",
										description="Randomize the uv-offset of individual planks",
										default=True,
										update=updateMesh)

bpy.types.Object.modify = BoolProperty(name="Add modifiers",
									description="Add bevel and solidify modifiers to the planks",
									default=True,
									update=updateMesh)

bpy.types.Object.randrotx = FloatProperty(name="X Rotation",
										description="Random rotation of individual planks around x-axis",
										default=0,
										min=0,
										soft_max=0.01,
										step=(0.02 / 180) * PI,
										precision=4,
										subtype='ANGLE',
										unit='ROTATION',
										update=updateMesh)

bpy.types.Object.randroty = FloatProperty(name="Y Rotation",
										description="Random rotation of individual planks around y-axis",
										default=0,
										min=0,
										soft_max=0.01,
										step=(0.02 / 180) * PI,
										precision=4,
										subtype='ANGLE',
										unit='ROTATION',
										update=updateMesh)

bpy.types.Object.randrotz = FloatProperty(name="Z Rotation",
										description="Random rotation of individual planks around z-axis",
										default=0,
										min=0,
										soft_max=0.01,
										step=(0.02 / 180) * PI,
										precision=4,
										subtype='ANGLE',
										unit='ROTATION',
										update=updateMesh)

bpy.types.Object.hollowlong = FloatProperty(name="Hollowness along plank",
											description="Amount of curvature along a plank",
											default=0,
											min=0,
											soft_max=0.01,
											step=0.01,
											precision=4,
											update=updateMesh)

bpy.types.Object.hollowshort = FloatProperty(name="Hollowness across plank",
											description="Amount of curvature across a plank",
											default=0,
											min=0,
											soft_max=0.01,
											step=0.01,
											precision=4,
											update=updateMesh)

bpy.types.Object.twist = FloatProperty(name="Twist along plank",
									description="Amount of twist along a plank",
									default=0,
									min=0,
									soft_max=0.01,
									step=0.01,
									precision=4,
									update=updateMesh)

bpy.types.Object.floorplan = EnumProperty(name="Floorplan",
									description="Mesh to use as a floorplan",
									items = availableMeshes,
									update=updateMesh)

bpy.types.Object.usefloorplan = BoolProperty(name="Use Floorplan",
									description="use a mesh object as a floorplan",
									default=False,
									update=updateMesh)


class FloorBoards(bpy.types.Panel):
	bl_idname = "FloorBoards"
	bl_label = "Floorgenerator"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "modifier"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		if bpy.context.mode == 'EDIT_MESH':
			layout.label('Floorgenerator doesn\'t work in the EDIT-Mode.')
		else:
			o = context.object
			if 'reg' in o:
				if o['reg'] == 'FloorBoards':
					box = layout.box()
					box.label('Floordimensions:')
					box.prop(o, 'length')
					box.prop(o, 'nplanks')

					box.label('Planks:')
					box.prop(o, 'planklength')
					box.prop(o, 'planklengthvar')
					box.prop(o, 'plankwidth')
					box.prop(o, 'plankwidthvar')
					box.prop(o, 'thickness')
					columns = box.row()
					col1 = columns.column()
					col2 = columns.column()
					col1.prop(o, 'offset')
					col2.prop(o, 'randomoffset')
					if o.randomoffset is True:
						col1.enabled = False

					box.prop(o, 'longgap')
					box.prop(o, 'shortgap')
					box.prop(o, 'bevel')

					columns = box.row()
					col1 = columns.column()
					col2 = columns.column()
					col1.prop(o, 'randrotx')
					col1.prop(o, 'randroty')
					col1.prop(o, 'randrotz')
					col2.prop(o, 'hollowlong')
					col2.prop(o, 'hollowshort')
					col2.prop(o, 'twist')

					box.prop(o, 'randomseed')

					box.prop(o, 'usefloorplan')
					if o.usefloorplan:
						box.prop(o, 'floorplan')
					box.label('Miscellaneous:')
					row = box.row()
					row.prop(o, 'randomuv')
					row.prop(o, 'modify')
				else:
					layout.operator('mesh.floor_boards_convert')
			else:
				layout.operator('mesh.floor_boards_convert')


class FloorBoardsAdd(bpy.types.Operator):
	bl_idname = "mesh.floor_boards_add"
	bl_label = "FloorBoards"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(self, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		bpy.ops.mesh.primitive_cube_add()
		context.active_object.name = "FloorBoard"
		bpy.ops.mesh.floor_boards_convert('INVOKE_DEFAULT')
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(FloorBoardsAdd.bl_idname, text="Add floor board mesh",
						icon='PLUGIN')


class FloorBoardsConvert(bpy.types.Operator):
	bl_idname = 'mesh.floor_boards_convert'
	bl_label = 'Convert to Floorobject'
	bl_options = {"UNDO"}

	def invoke(self, context, event):
		o = context.object
		o.reg = 'FloorBoards'
		o.length = 4
		return {"FINISHED"}


def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
	bpy.types.INFO_MT_mesh_add.remove(menu_func)
	bpy.utils.unregister_module(__name__)
