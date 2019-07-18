from random import random,seed, shuffle
from time import time
import mathutils
from mathutils import Vector

from kdtree_native import Tree


def bench_kdtree_blender(tsize, qsize):

	pos=[Vector((random(),random(),random())) for p in range(tsize)]
	qpos=[Vector((random(),random(),random())) for p in range(qsize)]

	start = time()
	kd = mathutils.kdtree.KDTree(tsize)
	for i,p in enumerate(pos):
		kd.insert(p, i)
	kd.balance()
	buildtime = time()-start
	start = time()
	for p in qpos:
		(co, index, dist) = kd.find(p)
	querytime = time()-start
	return buildtime, querytime

def bench_kdtree_pure(tsize, qsize):

	pos=[Vector((random(),random(),random())) for p in range(tsize)]
	qpos=[Vector((random(),random(),random())) for p in range(qsize)]

	start = time()
	kd = Tree(tsize)
	for i,p in enumerate(pos):
		kd.insert(p, i)
	#kd.balance()
	buildtime = time()-start
	start = time()
	for p in qpos:
		(co, dist) = kd.nearest(p)
	querytime = time()-start
	return buildtime, querytime


tsize, qsize = 1000,10000

print(bench_kdtree_blender(tsize, qsize))
print(bench_kdtree_pure(tsize, qsize))

