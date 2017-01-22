import bpy
from mathutils import kdtree
from itertools import permutations as perm
from functools import lru_cache
from time import time
from math import factorial as fac

bl_info = {
	"name": "Chain selected objects",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 201701220957),
	"blender": (2, 78, 0),
	"location": "View3D > Object > Chain selected objects",
	"description": """Combine selected objects to a list of parent-child relations based on proximity""",
	"category": "Object"}

def object_list(objects):
	"""
	Return the shortest Hamiltonian path through a collection of objects.

	This is calculated using a brute force method that is certainly not
	intented for real life use because for example going from ten to
	eleven objects will increase the running time elevenfold and even
	with caching expensive distance calculations this quickly becomes
	completely unworkable.

	But this routine is intended as our baseline algorithm that is meant
	to be replaced with an approximation algorithm that is 'good enough'
	for our purposes.
	"""
	@lru_cache()
	def distance_squared(a,b):
		return (objects[a].location-objects[b].location).length_squared

	def length_squared(chain):
		sum = 0.0
		for i in range(len(chain)-1):
			sum += distance_squared(chain[i],chain[i+1])
		return sum

	s = time()

	shortest_d2 = 1e30
	shortest_chain = None

	n_half = fac(len(objects))//2
	for i,chain in enumerate(perm(range(len(objects)))):
		if i >= n_half:
			break
		d2 = length_squared(chain)
		if d2 < shortest_d2:
			shortest_d2 = d2
			shortest_chain = chain

	print("{n:d} objects {t:.1f}s".format(t=time()-s, n=len(objects)))

	return [objects[i] for i in shortest_chain]

def object_list2(objects, active=0):
	"""
	Return an approximate shortest path through objects starting at the
	active index using the nearest neighbor heuristic.
	"""

	s = time()

	# calculate a kd tree to quickly answer nearest neighbor queries
	kd = kdtree.KDTree(len(objects))
	for i, ob in enumerate(objects):
		kd.insert(ob.location, i)
	kd.balance()

	current = objects[active]
	chain = [current]  # we start at the chosen object
	added = {active}
	for i in range(1,len(objects)):  # we know how many objects to add
		# when looking for the nearest neighbor we start with two neigbors
		# (because we include the object itself in the search) and if
		# the other neigbors is not yet in the chain we add it, otherwise
		# we expand our search to a maximum of the total number of objects
		for n in range(2,len(objects)):
			neighbors = { index for _,index,_ in kd.find_n(current.location, n) }
			neighbors -= added
			if neighbors:  # strictly speaking we shoudl assert that len(neighbors) == 1
				chain.extend(objects[i] for i in neighbors)
				added |= neighbors
				break
		current = chain[-1]

	print("{n:d} objects {t:.1f}s".format(t=time()-s, n=len(objects)))

	return chain

class ChainSelectedObjects(bpy.types.Operator):
	bl_idname = 'object.chainselectedobjects'
	bl_label = 'Chain selected objects'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(self, context):
		return (context.mode == 'OBJECT' 
			and len(context.selected_objects) > 1)

	def execute(self, context):
		so = context.selected_objects.copy()
		objects = object_list2(so, so.index(context.active_object))
		for ob in objects:
			ob.select = False

		ob = objects.pop()
		first = ob
		while objects:
			context.scene.objects.active = ob
			child = objects.pop()
			child.select = True
			bpy.ops.object.parent_set(keep_transform=True)
			child.select = False
			ob = child
		first.select = True
		context.scene.objects.active = first
		return {"FINISHED"}


def menu_func(self, context):
	self.layout.operator(
		ChainSelectedObjects.bl_idname,
		text=ChainSelectedObjects.bl_label,
		icon='PLUGIN')


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
	bpy.types.VIEW3D_MT_object.remove(menu_func)
	bpy.utils.unregister_module(__name__)
