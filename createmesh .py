# ##### BEGIN GPL LICENSE BLOCK #####
#
#  CreateMesh, a Blender addon
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
	"name": "CreateMesh",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 201601131151),
	"blender": (2, 76, 0),
	"location": "View3D > Object > Add Mesh > DumpedMesh",
	"description": "Adds a mesh object to the scene that was created with the DumpMesh addon",
	"warning": "",
	"wiki_url": "https://github.com/varkenvarken/blenderaddons/blob/master/createmesh%20.py",
	"tracker_url": "",
	"category": "Add Mesh"}

import bpy
import bmesh

class DumpMesh:

	# most elements in an attribute layer can be assigned to directly
	# if they are floats and if they are Vectors (or Colors) they can
	# be assigned a tuple without problems. However, some specific types
	# need the value to be assigned to a specific attribute and for
	# those we have a mapping here. BMTexPoly does not behave and is not
	# documented well (Blender 2.76) so we ignore it. 
	attributemapping = dict(BMLoopUV=lambda ob,v: setattr(ob,'uv',v),
							BMVertSkin=lambda ob,v: setattr(ob,'radius',v),
							BMTexPoly=lambda ob,v: None)

	def valmap(self, sample):
		name = sample.__class__.__name__
		if name in self.attributemapping:
			return self.attributemapping[name]
		return None

	def geometry(self):

		bm = bmesh.new()

		verts = self.__class__.verts
		edges = self.__class__.edges
		faces = self.__class__.faces
		
		for n,v in enumerate(verts):
			bm.verts.new(v)
		bm.verts.ensure_lookup_table()  # ensures bm.verts can be indexed
		bm.verts.index_update()         # ensures all bm.verts have an index (= different thing!)
		if hasattr(self.__class__,'vert_attributes'):
			for attr, values in self.__class__.vert_attributes.items():
				for v,val in zip(bm.verts, values):
					setattr(v,attr,val)

		for n,e in enumerate(edges):
			edge = bm.edges.new(bm.verts[v] for v in e)
		bm.edges.ensure_lookup_table()
		bm.edges.index_update()
		if hasattr(self.__class__,'edge_attributes'):
			for attr, values in self.__class__.edge_attributes.items():
				for e,val in zip(bm.edges, values):
					setattr(e,attr,val)

		for n,f in enumerate(faces):
			bm.faces.new(bm.verts[v] for v in f)
		bm.faces.ensure_lookup_table()
		bm.faces.index_update()
		if hasattr(self.__class__,'face_attributes'):
			for attr, values in self.__class__.face_attributes.items():
				for f,val in zip(bm.faces, values):
					setattr(f,attr,val)

		for etype in ('verts', 'edges', 'faces'):
			seq = getattr(bm, etype)
			bmlayers = seq.layers
			if hasattr(self.__class__, etype + '_layers'):
				for layertype, layers in getattr(self.__class__, etype + '_layers').items():
					bmlayertype = getattr(bmlayers, layertype)
					for layername, values in layers.items():
						bmlayer = bmlayertype.new(layername) # fresh object so we don't check if the layer already exists
						valmap = self.valmap(seq[0][bmlayer])
						for n, ele in enumerate(seq):
							if valmap is None:
								ele[bmlayer] = values[n]
							else:
								valmap(ele[bmlayer],values[n])

		bmlayers = bm.loops.layers
		if hasattr(self.__class__, 'loops_layers'):
			for layertype, layers in getattr(self.__class__, 'loops_layers').items():
				bmlayertype = getattr(bmlayers, layertype)
				attrname = self.__class__.attributemapping[layertype] if layertype in self.__class__.attributemapping else None
				for layername, values in layers.items():
					bmlayer = bmlayertype.new(layername) # fresh object so we don't check if the layer already exists
					# we assume all loops will be numbered in ascending order
					# bm.faces[i].loops.index_update() is of no use, since it
					# start numbering again at 0 for this set of loops, so there
					# is no way to update the indices of all loop in in go,
					# except by converting the bm to a regular mesh, in which
					# case it happens automagically.
					loopindex = 0
					for face in bm.faces:
						for loop in face.loops:
							val = values[face.index][loopindex]
							valmap = self.valmap(loop[bmlayer])
							if valmap is None:
								loop[bmlayer] = val
							else:
								valmap(loop[bmlayer],val)
							loopindex += 1

		return bm

	# bmesh.types.BMesh cannot be subclassed, but this way we can almost
	# let DumpMesh derived classes behave like a class factory whose
	# instances return a BMesh

	def __call__(self):
		return self.geometry()

class Cube(DumpMesh):
	verts = [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1),]

	edges = [(0, 1),(1, 3),(3, 2),(2, 0),(3, 7),(7, 6),(6, 2),(7, 5),(5, 4),(4, 6),(5, 1),(0, 4),]

	faces = [(1, 3, 2, 0),(3, 7, 6, 2),(7, 5, 4, 6),(5, 1, 0, 4),(0, 2, 6, 4),(5, 7, 3, 1),]

	verts_layers = {'bevel_weight': {}, 'deform': {}, 'float': {}, 'int': {}, 'paint_mask': {}, 'shape': {}, 'skin': {'': {0:(0.25, 0.25),1:(0.25, 0.25),2:(0.25, 0.25),3:(0.25, 0.25),4:(0.25, 0.25),5:(0.25, 0.25),6:(0.25, 0.25),7:(0.25, 0.25),}, }, 'string': {}, 	}

	edges_layers = {'bevel_weight': {}, 'crease': {'SubSurfCrease': {0:0.0,1:0.0,2:0.0,3:0.0,4:0.0,5:1.0,6:0.0,7:1.0,8:1.0,9:1.0,10:0.0,11:0.0,}, }, 'float': {}, 'freestyle': {}, 'int': {}, 'string': {}, 	}

	faces_layers = {'float': {}, 'freestyle': {}, 'int': {}, 'string': {}, 'tex': {'UVMap': {0:None,1:None,2:None,3:None,4:None,5:None,}, }, 	}

	loops_layers = {'color': {'Col': {0: {0:(1.0, 1.0, 1.0),1:(1.0, 1.0, 1.0),2:(1.0, 1.0, 1.0),3:(1.0, 1.0, 1.0),},1: {4:(1.0, 1.0, 1.0),5:(1.0, 1.0, 1.0),6:(1.0, 1.0, 1.0),7:(1.0, 1.0, 1.0),},2: {8:(1.0, 1.0, 1.0),9:(1.0, 1.0, 1.0),10:(1.0, 1.0, 1.0),11:(1.0, 1.0, 1.0),},3: {12:(1.0, 0.15294118225574493, 0.14901961386203766),13:(1.0, 0.007843137718737125, 0.0),14:(1.0, 0.007843137718737125, 0.0),15:(1.0, 0.007843137718737125, 0.0),},4: {16:(1.0, 1.0, 1.0),17:(1.0, 1.0, 1.0),18:(1.0, 1.0, 1.0),19:(1.0, 1.0, 1.0),},5: {20:(1.0, 1.0, 1.0),21:(1.0, 1.0, 1.0),22:(1.0, 1.0, 1.0),23:(1.0, 1.0, 1.0),},},},'float': {},'int': {},'string': {},'uv': {'UVMap': {0: {0:(0.33333346247673035, 0.6666666269302368),1:(0.33333340287208557, 0.3333333730697632),2:(0.6666666865348816, 0.3333333432674408),3:(0.6666667461395264, 0.6666666269302368),},1: {4:(3.973642037635727e-08, 0.6666666865348816),5:(0.0, 0.33333340287208557),6:(0.333333283662796, 0.3333333432674408),7:(0.3333333432674408, 0.6666666269302368),},2: {8:(1.291433733285885e-07, 0.3333333432674408),9:(0.0, 8.940693874137651e-08),10:(0.3333333134651184, 0.0),11:(0.33333340287208557, 0.33333325386047363),},3: {12:(0.33333340287208557, 3.9736416823643594e-08),13:(0.6666666865348816, 0.0),14:(0.6666667461395264, 0.33333325386047363),15:(0.33333346247673035, 0.3333333134651184),},4: {16:(1.0, 0.0),17:(1.0, 0.33333322405815125),18:(0.6666667461395264, 0.33333322405815125),19:(0.6666667461395264, 2.9802313505911115e-08),},5: {20:(0.0, 0.6666667461395264),21:(0.33333325386047363, 0.6666666865348816),22:(0.333333283662796, 0.9999999403953552),23:(4.967052547044659e-08, 0.9999999403953552),},},},	}

	vert_attributes = {
	'normal' : [(-0.5773491859436035, -0.5773491859436035, -0.5773491859436035), (-0.5773491859436035, -0.5773491859436035, 0.5773491859436035), (-0.5773491859436035, 0.5773491859436035, -0.5773491859436035), (-0.5773491859436035, 0.5773491859436035, 0.5773491859436035), (0.5773491859436035, -0.5773491859436035, -0.5773491859436035), (0.5773491859436035, -0.5773491859436035, 0.5773491859436035), (0.5773491859436035, 0.5773491859436035, -0.5773491859436035), (0.5773491859436035, 0.5773491859436035, 0.5773491859436035)],
	'select' : [False, True, False, True, False, True, False, True],
	}

	edge_attributes = {
	'seam' : [False, False, False, False, False, False, False, False, False, False, False, False],
	'smooth' : [True, True, True, True, True, True, True, True, True, True, True, True],
	'select' : [False, True, False, False, True, False, False, True, False, False, True, False],
	}

	face_attributes = {
	'normal' : [(-1.0, 0.0, 0.0), (0.0, 1.0, -0.0), (1.0, 0.0, -0.0), (0.0, -1.0, 0.0), (-0.0, 0.0, -1.0), (-0.0, 0.0, 1.0)],
	'smooth' : [False, False, False, False, False, False],
	'select' : [False, False, False, False, False, True],
	}



meshes = [ Cube ]

class CreateMesh(bpy.types.Operator):
	"""Add mesh objects to the scene"""
	bl_idname = "mesh.createmesh"
	bl_label = "CreateMesh"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'

	def execute(self, context):
		for mesh in meshes:
			meshfactory = mesh()

			me = bpy.data.meshes.new(name=meshfactory.__class__.__name__)
			ob = bpy.data.objects.new(meshfactory.__class__.__name__, me)

			bm = meshfactory()

			# write the bmesh to the mesh
			bm.to_mesh(me)
			me.show_edge_seams = True
			me.update()
			bm.free()

			# associate the mesh with the object
			ob.data = me

			# link the object to the scene & make it active and selected
			context.scene.objects.link(ob)
			context.scene.update()
			context.scene.objects.active = ob
			ob.select = True

		return {'FINISHED'}

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_mesh_add.remove(menu_func)

def menu_func(self, context):
	self.layout.operator(CreateMesh.bl_idname, icon='PLUGIN')

if __name__ == "__main__":
	register()
