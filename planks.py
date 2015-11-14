# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Floor Generator, a Blender addon
#  (c) 2013,2015 Michel J. Anders (varkenvarken)
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
	"name": "Floor Generator",
	"author": "Michel Anders (varkenvarken) with contributions from Alain, Floric and Lell. The idea to add patterns is based on Cedric Brandin's (clarkx) parquet addon",
	"version": (0, 0, 201511141025),
	"blender": (2, 76, 0),
	"location": "View3D > Add > Mesh",
	"description": "Adds a mesh representing floor boards (planks)",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Add Mesh"}

from random import random as rand, seed, uniform as randuni, randrange
from math import pi as PI, sqrt, radians
from copy import deepcopy
from itertools import zip_longest
import bpy
import bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, StringProperty
from mathutils import Vector, Euler

D180 = radians(180)
D90 = radians(90)
D45 = radians(45)
W2 = sqrt(2)

# Vector.rotate() does NOT return anything, contrary to what the docs say
# docs are now fixed (https://projects.blender.org/tracker/index.php?func=detail&aid=36518&group_id=9&atid=498)
# but unfortunately no rotated() function was added
def rotate(v, r):
	v2 = deepcopy(v)
	v2.rotate(r)
	return v2

def rotatep(v, r, p):
	v2 = v - p
	v2.rotate(r)
	return v2 + p

def vcenter(verts):
	return sum(verts,Vector())/len(verts)

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

def swap(c, i, j):
	p1 = deepcopy(c[i])
	p2 = deepcopy(c[j])
	c[i] = p2
	c[j] = p1

def swapx(c, i):
	p1 = c[i]
	p2 = c[i+1]
	x1min = min(v.x for v in p1)
	x1max = max(v.x for v in p1)
	x2min = min(v.x for v in p2)
	x2max = max(v.x for v in p2)
	dx1 = Vector((x2min - x1min,0,0))
	dx2 = Vector((x2max - x1max,0,0))
	c[i+1] = [v - dx1 for v in p2]
	c[i] = [v + dx2 for v in p1]
	
	
def getMaterialList(obj):
	materials = []
	for slot in obj.material_slots:
		materials.append((slot.link, slot.name, slot.material.name, slot.material.use_fake_user))
		slot.material.use_fake_user = True # we remove the mesh so any linked data is invalidated. setting a fake user will keep our material 'live'
	return materials

def rebuildMaterialList(obj, lst):
	for slot, (link, slotname, materialname, use_fake_user) in enumerate(lst):
		bpy.ops.object.material_slot_add()
		obj.material_slots[slot].link = link
		obj.material_slots[slot].material = bpy.data.materials[materialname]
		obj.material_slots[slot].material.use_fake_user = use_fake_user

def assignRandomMaterial(slot_n):
	bpy.ops.object.mode_set(mode = 'EDIT') # Go to edit mode to create bmesh
	obj = bpy.context.object

	bm = bmesh.from_edit_mesh(obj.data) # Create bmesh object from object mesh

	for face in bm.faces: # Iterate over all of the object's faces
		face.material_index = randrange(slot_n) # Assign random material to face
	obj.data.update() # Update the mesh from the bmesh data
	bpy.ops.object.mode_set(mode = 'OBJECT') # Return to object mode

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

def planklw(length, width, rot=None):
	ll = Vector((0, 0, 0))
	lr = Vector((length, 0, 0))
	ul = Vector((length, width, 0))
	ur = Vector((0, width, 0))
	if rot:
		ll = rotate(ll, rot)
		lr = rotate(lr, rot)
		ul = rotate(ul, rot)
		ur = rotate(ur, rot)
	verts = (ll, lr, ul, ur)
	return verts


def planks(n, m,
		length, lengthvar,
		width, widthvar,
		longgap, shortgap,
		offset, randomoffset,
		nseed,
		randrotx, randroty, randrotz,
		originx, originy):

	#n=Number of planks, m=Floor Length, length = Planklength

	verts = []
	faces = []
	uvs = []
	
	seed(nseed)
	widthoffset = 0
	s = 0
	e = offset
	c = offset  # Offset per row
	ws = 0
	p = 0

	while p < n:
		p += 1
		
		uvs.append([])
		
		w = width + randuni(0, widthvar)
		we = ws + w
		if randomoffset:
			e = randuni(4 * shortgap, length)  # we don't like negative plank lengths
		while (m - e) > (4 * shortgap):
			ll = len(verts)
			rot = Euler((randrotx * randuni(-1, 1), randroty * randuni(-1, 1), randrotz * randuni(-1, 1)), 'XYZ')
			pverts = plank(s - originx, e - originx, ws - originy, we - originy, longgap, shortgap, rot)
			verts.extend(pverts)
			uvs[-1].append(deepcopy(pverts))
			faces.append((ll, ll + 3, ll + 2, ll + 1))
			s = e
			e += length + randuni(0, lengthvar)
		ll = len(verts)
		rot = Euler((randrotx * randuni(-1, 1), randroty * randuni(-1, 1), randrotz * randuni(-1, 1)), 'XYZ')
		pverts = plank(s - originx, m - originx, ws - originy, we - originy, longgap, shortgap, rot)
		verts.extend(pverts)
		uvs[-1].append(deepcopy(pverts))
		faces.append((ll, ll + 3, ll + 2, ll + 1))
		s = 0
		#e = e - m
		if c <= (length):
			c = c + offset
		if c > (length):
			c = c - length
		e = c
		ws = we
		# randomly swap uvs of planks. Note: we only swap within one set of planks because different sets can have different widths.
		nplanks = len(uvs[-1])
		if nplanks < 2 : continue
		for pp in range(nplanks//2): # // to make sure it stays an int
			i = randrange(nplanks-1)
			swapx(uvs[-1],i)
		
	fuvs = [uv for col in uvs for plank in col for uv in plank]
	return verts, faces, fuvs

def herringbone(rows, cols, planklength, plankwidth, longgap, shortgap, nseed, randrotx, randroty, randrotz, originx, originy):
	verts = []
	faces = []
	uvs = []
	
	seed(nseed)
	
	ll=0
	longside = (planklength-shortgap)/sqrt(2.0)
	shortside = (plankwidth-longgap)/sqrt(2.0)
	vstep = Vector((0,plankwidth * sqrt(2.0),0))
	hstepl = Vector((planklength * sqrt(2.0),0,0))
	hstep = Vector((planklength/sqrt(2.0)-(plankwidth-longgap)/sqrt(2.0),planklength/sqrt(2.0)+(plankwidth-longgap)/sqrt(2.0),0))
	
	dy = Vector((0,-planklength/sqrt(2.0),0))
	
	pu = [Vector((0,0,0)),Vector((longside,0,0)),Vector((longside,shortside,0)),Vector((0,shortside,0))]
	
	pv = [Vector((0,0,0)),Vector((longside,longside,0)),Vector((longside-shortside,longside+shortside,0)),Vector((-shortside,shortside,0))]
	rot = Euler((0,0,-PI/2),"XYZ")
	pvm = [rotate(v, rot)+hstep for v in pv]
	
	midpointpv = sum(pv,Vector())/4.0
	midpointpvm = sum(pvm,Vector())/4.0

	o = Vector((-originx, -originy, 0))
	midpointpvo = midpointpv - o
	midpointpvmo = midpointpvm - o

	for col in range(cols):
		for row in range(rows):
			# CLEANUP: this could be shorter: for P in pv,pvm 
			rot = Euler((randrotx * randuni(-1, 1), randroty * randuni(-1, 1), randrotz * randuni(-1, 1)), 'XYZ')
			pvo = [ v + o for v in pv]
			pverts = [rotate(v - midpointpvo, rot) + midpointpvo  + row * vstep + col * hstepl + dy for v in pvo]
			verts.extend(deepcopy(pverts))
			uvs.append([v + Vector((col*2*longside,row*shortside,0)) for v in pu])
			faces.append((ll, ll + 1, ll + 2, ll + 3))
			ll = len(verts)
			rot = Euler((randrotx * randuni(-1, 1), randroty * randuni(-1, 1), randrotz * randuni(-1, 1)), 'XYZ')
			pvmo = [ v + o for v in pvm]
			pverts = [rotate(v - midpointpvmo, rot) + midpointpvmo  + row * vstep + col * hstepl + dy for v in pvmo]
			verts.extend(deepcopy(pverts))
			uvs.append([v + Vector(((1+col*2)*longside,row*shortside,0)) for v in pu])
			faces.append((ll, ll + 1, ll + 2, ll + 3))
			ll = len(verts)
	
	for i in range(len(uvs)):
		pp1 = randrange(len(uvs))
		pp2 = randrange(len(uvs))
		swap(uvs,pp1,pp2)
		
	fuvs = [v for p in uvs for v in p]
	return verts, faces, fuvs
	
def square(rows, cols, planklength, n, border, longgap, shortgap, nseed, randrotx, randroty, randrotz, originx, originy):
	verts = []
	verts2 = []
	faces = []
	faces2 = []
	uvs = []
	uvs2 = []
	seed(nseed)
	
	ll=0
	ll2=0
	net_planklength = planklength - 2.0 * border
	
	plankwidth = net_planklength/n
	longside = (net_planklength-shortgap)
	shortside = (plankwidth-longgap)
	stepv = Vector((0,planklength ,0))
	steph = Vector((planklength,0 ,0))
	nstepv = Vector((0,plankwidth ,0))
	nsteph = Vector((plankwidth,0 ,0))
	
	pv = [Vector((0,0,0)),Vector((longside,0,0)),Vector((longside,shortside,0)),Vector((0,shortside,0))]
	rot = Euler((0,0,-PI/2),"XYZ")
	pvm = [rotate(v, rot) + Vector((0,planklength - border,0)) for v in pv]
	
	midpointpv = sum(pv,Vector())/4.0
	midpointpvm = sum(pvm,Vector())/4.0
	
	offseth = Vector((border, border, 0))
	offsetv = Vector((border, 0, 0))
	
	bw = border - shortgap
	b1 = [(0,longgap/2.0,0),(0,planklength - longgap/2.0,0),(bw,planklength - longgap/2.0 - border,0),(bw,longgap/2.0 + border,0)]
	b1 = [Vector(v) for v in b1]
	d = Vector((planklength/2.0, planklength/2.0, 0))
	rot = Euler((0,0,-  PI/2),"XYZ")
	b2 = [rotate(v-d,rot)+d for v in b1]
	rot = Euler((0,0,-  PI  ),"XYZ")
	b3 = [rotate(v-d,rot)+d for v in b1]
	rot = Euler((0,0,-3*PI/2),"XYZ")
	b4 = [rotate(v-d,rot)+d for v in b1]

	o = Vector((-originx, -originy, 0))

	# CLEANUP: duplicate code, suboptimal loop nesting and a lot of repeated calculations
	# note that the uv map we create here is always aligned in the same direction even though planks alternate. This matches the saw direction in real life
	for col in range(cols):
		for row in range(rows):
			# add the regular planks
			for p in range(n):
				rot = Euler((randrotx * randuni(-1, 1), randroty * randuni(-1, 1), randrotz * randuni(-1, 1)), 'XYZ')
				if (col ^ row) %2 == 1:
					pverts = [rotate(v - midpointpv, rot) + midpointpv + row * stepv + col * steph + nstepv * p + offseth + o for v in pv]
					uverts = [v + row * stepv + col * steph + nstepv * p for v in pv]
				else:
					pverts = [rotate(v - midpointpv, rot) + midpointpv + row * stepv + col * steph + nsteph * p + offsetv + o for v in pvm]
					uverts = [v + row * stepv + col * steph + nstepv * p for v in pv]
				verts.extend(deepcopy(pverts))
				uvs.append(deepcopy(uverts))
				faces.append((ll, ll + 1, ll + 2, ll + 3))
				ll = len(verts)
			# add the border planks
			if bw > 0.001:
				for vl in b1,b2,b3,b4:
					rot = Euler((randrotx * randuni(-1, 1), randroty * randuni(-1, 1), randrotz * randuni(-1, 1)), 'XYZ')
					midpointvl = sum(vl,Vector())/4.0
					verts2.extend([rotate(v - midpointvl, rot) + midpointvl + row * stepv + col * steph + o for v in vl])
					uvs2.append(deepcopy([v + row * stepv + col * steph for v in b1])) # again, always the unrotated uvs to match the saw direction
					faces2.append((ll2, ll2 + 3, ll2 + 2, ll2 + 1))
					ll2 = len(verts2)
						
	for i in range(len(uvs)):
		pp1 = randrange(len(uvs))
		pp2 = randrange(len(uvs))
		swap(uvs,pp1,pp2)
	for i in range(len(uvs2)):
		pp1 = randrange(len(uvs2))
		pp2 = randrange(len(uvs2))
		swap(uvs2,pp1,pp2)
	
	fuvs = [v for p in uvs for v in p]
	fuvs2 = [v for p in uvs2 for v in p]
	
	return verts + verts2, faces + [(f[0]+ll,f[1]+ll,f[2]+ll,f[3]+ll) for f in faces2], fuvs + fuvs2
	
def shortside(vert):
	"""return true if length of 2 out of 3 connected vertices is equal to the min length of the connected edges"""
	n = 0
	el = [e.calc_length() for e in vert.link_edges]
	mel = min(el)
	for e in el:
		if abs(e - mel) < 1e-4 :
			n += 1
	return n == 2

def versaille(rows, cols, planklength, plankwidth,longgap=0, shortgap=0, randrotx=0, randroty=0, randrotz=0, originx=0, originy=0, switch=False):

	o = Vector((-originx, -originy, 0)) * planklength

	# (8*w+w/W2)*W2 + w = 8*w*W2+w = (8*W2+1)*w = 1 
	w = 1.0 / (8*W2+2)
	#w1 = 1 - w
	q = w/W2
	#k = w*4*W2-w
	#s = (k - w)/2
	#d = ((s+2*w)/W2)/2
	#S = s/W2
	sg = shortgap
	s2 = sg/W2
	lg = longgap

	dd=-q if switch else 0

	planks1 = (
		# rectangles
		(0,[(0+sg,0,0), (w*5-sg,0,0), (w*5-sg,w,0), (0+sg,w,0)]),
		(0,[(6*w+sg,0,0), (w*11-sg,0,0), (w*11-sg,w,0), (6*w+sg,w,0)]),
		(90,[(5*w,-2*w+sg,0), (w*6,-2*w+sg,0), (w*6,3*w-sg,0), (5*w,3*w-sg,0)]),
		(0,[(3*w+sg,3*w,0), (w*8-sg,3*w,0), (w*8-sg,w*4,0), (3*w+sg,w*4,0)]),
		(0,[(3*w+sg,-3*w,0), (w*8-sg,-3*w,0), (w*8-sg,w*-2,0), (3*w+sg,w*-2,0)]),
		(90,[(5*w,4*w+sg,0),(6*w,4*w+sg,0),(6*w,6*w-sg,0),(5*w,6*w-sg,0)]),
		(90,[(5*w,-3*w-sg,0),(5*w,-5*w+sg,0),(6*w,-5*w+sg,0),(6*w,-3*w-sg,0)]),
		# squares
		(0,[(0+sg,w+sg,0), (w*2-sg,w+sg,0), (w*2-sg,w*3-sg,0), (0+sg,w*3-sg,0)]),
		(0,[(3*w+sg,w+sg,0), (w*5-sg,w+sg,0), (w*5-sg,w*3-sg,0), (3*w+sg,w*3-sg,0)]),
		(0,[(6*w+sg,w+sg,0), (w*8-sg,w+sg,0), (w*8-sg,w*3-sg,0), (6*w+sg,w*3-sg,0)]),
		(0,[(9*w+sg,w+sg,0), (w*11-sg,w+sg,0), (w*11-sg,w*3-sg,0), (9*w+sg,w*3-sg,0)]),
		(0,[(0+sg,-2*w+sg,0), (w*2-sg,-2*w+sg,0), (w*2-sg,0-sg,0), (0+sg,0-sg,0)]),
		(0,[(3*w+sg,-2*w+sg,0), (w*5-sg,-2*w+sg,0), (w*5-sg,0-sg,0), (3*w+sg,0-sg,0)]),
		(0,[(6*w+sg,-2*w+sg,0), (w*8-sg,-2*w+sg,0), (w*8-sg,0-sg,0), (6*w+sg,0-sg,0)]),
		(0,[(9*w+sg,-2*w+sg,0), (w*11-sg,-2*w+sg,0), (w*11-sg,0-sg,0), (9*w+sg,0-sg,0)]),
		(0,[(3*w+sg,4*w+sg,0),(5*w-sg,4*w+sg,0),(5*w-sg,6*w-sg,0),(3*w+sg,6*w-sg,0)]),
		(0,[(6*w+sg,4*w+sg,0),(8*w-sg,4*w+sg,0),(8*w-sg,6*w-sg,0),(6*w+sg,6*w-sg,0)]),
		(0,[(3*w+sg,-5*w+sg,0),(5*w-sg,-5*w+sg,0),(5*w-sg,-3*w-sg,0),(3*w+sg,-3*w-sg,0)]),
		(0,[(6*w+sg,-5*w+sg,0),(8*w-sg,-5*w+sg,0),(8*w-sg,-3*w-sg,0),(6*w+sg,-3*w-sg,0)]),
		
		# pointed
		(0,[(0+sg,3*w,0),(2*w-sg,3*w,0),(2*w-sg,4*w,0),(w+sg,4*w,0)]),
		#left
		(0,[(w+sg,4*w,0),(2*w-sg,4*w,0),(2*w-sg,5*w-sg*2,0)]),
		
		(0,[(9*w+sg,3*w,0),(11*w-sg,3*w,0),(10*w-sg,4*w,0),(9*w+sg,4*w,0)]),
		#top
		(0,[(9*w+sg,4*w,0),(10*w-sg,4*w,0),(9*w+sg,5*w-sg*2,0)]),
		
		(0,[(0+sg,-2*w,0),(w+sg,-3*w,0),(2*w-sg,-3*w,0),(2*w-sg,-2*w,0)]),
		#bottom
		(0,[(1*w+sg,-3*w,0),(2*w-sg,-4*w+sg+sg,0),(2*w-sg,-3*w,0)]),
		
		(0,[(9*w+sg,-3*w,0),(10*w-sg,-3*w,0),(11*w-sg,-2*w,0),(9*w+sg,-2*w,0)]),
		#right
		(0,[(9*w+sg,-3*w,0),(9*w+sg,-4*w+sg*2,0),(10*w-sg,-3*w,0)]),
		
		# long pointed
		(90,[(2*w,0-sg,0),(2*w,-4*w+sg,0),(3*w,-5*w+sg,0),(3*w,0-sg,0)]),
		(90,[(8*w,0-sg,0),(8*w,-5*w+sg,0),(9*w,-4*w+sg,0),(9*w,0-sg,0)]),
		(90,[(2*w,w+sg,0),(3*w,w+sg,0),(3*w,6*w-sg,0),(2*w,5*w-sg,0)]),
		(90,[(8*w,w+sg,0),(9*w,w+sg,0),(9*w,5*w-sg,0),(8*w,6*w-sg,0)]),
		# corner planks
		(90,[(0,-2*w+sg,0),(0,3*w-sg,0),(-1*w,2*w-sg,0),(-1*w,-1*w+sg,0)]),
		(90,[(11*w,-2*w+sg,0),(12*w,-1*w+sg,0),(12*w,2*w-sg,0),(11*w,3*w-sg,0)]),
		(0,[(3*w+sg,-5*w,0),(4*w+sg,-6*w,0),(7*w-sg,-6*w,0),(8*w-sg,-5*w,0)]),
		(0,[(3*w+sg,6*w,0),(8*w-sg,6*w,0),(7*w-sg,7*w,0),(4*w+sg,7*w,0)]),
		# corner triangles
		(90,[(-w-s2,-w+s2*2,0),(-w-s2,2*w-s2*2,0),(-2.5*w+s2,0.5*w,0)]),
		(90,[(12*w+s2,2*w-s2*2,0),(12*w+s2,-w+s2*2,0),(13.5*w-s2,0.5*w,0)]),
		(0,[(4*w+s2*2,7*w+s2,0),(7*w-s2*2,7*w+s2,0),(5.5*w,8.5*w-s2,0)]),
		(0,[(4*w+s2*2,-6*w-s2,0),(5.5*w,-7.5*w+s2,0),(7*w-s2*2,-6*w-s2,0)]),
		
		# border planks
		# bottom
		(45,[(-2.5*w-q+q+dd+lg,0.5*w+q-q-dd-lg,0),(-2.5*w-2*q+q+dd+lg+lg,0.5*w-q-dd+lg-lg,0),(5.5*w-q+lg-lg,-7.5*w-q+lg+lg,0),(5.5*w-lg,-7.5*w+lg,0)]),
		# right
		(135,[(5.5*w-q+lg,-7.5*w-q+lg,0),(5.5*w+lg-lg,-7.5*w-2*q+lg+lg,0),(13.5*w+2*q+dd-lg-lg,0.5*w+dd-lg+lg,0),(13.5*w+q+dd-lg,0.5*w+q+dd-lg,0)]),
		#top
		(45,[(13.5*w-dd-lg,0.5*w+dd+lg,0),(13.5*w+q-dd-lg-lg,0.5*w+q+dd-lg+lg,0),(5.5*w+q-lg+lg,8.5*w+q-lg-lg,0),(5.5*w+lg,8.5*w-lg,0)]),
		#left
		(135,[(-2.5*w-q-dd+lg,0.5*w-q-dd+lg,0),(5.5*w+q-lg,8.5*w+q-lg,0),(5.5*w-lg+lg,8.5*w+2*q-lg-lg,0),(-2.5*w-q-q-dd+lg+lg,0.5*w+q-q-dd+lg-lg,0)])
	)
	
	verts = []
	faces = []
	uvs = []
	left = 0
	center = Vector((5.5*w,0.5*w,0))*planklength
	delta = Vector((w, -10*q, 0)) * planklength
	for col in range(cols):
		start = 0
		for row in range(rows):
			origin = Vector((start, left, 0))
			for uvrot,p in planks1:
				ll = len(verts)
				rot = Euler((randrotx * randuni(-1, 1), randroty * randuni(-1, 1), randrotz * randuni(-1, 1)), 'XYZ')
				# randomly rotate the plank a little bit around its own center
				pverts = [rotate(Vector(v)*planklength, rot) for v in p]
				pverts = [origin + delta + o + rotatep(v, Euler((0,0,radians(45)),'XYZ'), center) for v in pverts]
				
				verts.extend(pverts)
				midpoint = vcenter(pverts)
				if uvrot > 0:
					print(uvrot)
					print([v - midpoint for v in pverts])
					print([rotatep(v, Euler((0,0,radians(uvrot)),'XYZ'), midpoint) - midpoint for v in pverts])
					print()
				uvs.append([rotatep(v, Euler((0,0,radians(uvrot)),'XYZ'), midpoint) for v in pverts])
				faces.append((ll, ll + 3, ll + 2, ll + 1) if len(pverts)==4 else (ll, ll + 2, ll + 1))


			start += planklength
		left += planklength
	
	fuvs = [v for p in uvs for v in p]
	
	return verts, faces, fuvs
	
def updateMesh(self, context):
	o = context.object

	material_list = getMaterialList(o)
		
	if o.pattern == 'Regular':
		nplanks = (o.width + o.originy) / o.plankwidth
		verts, faces, uvs = planks(nplanks, o.length + o.originx,
												o.planklength, o.planklengthvar,
												o.plankwidth, o.plankwidthvar,
												o.longgap, o.shortgap,
												o.offset, o.randomoffset,
												o.randomseed,
												o.randrotx, o.randroty, o.randrotz,
												o.originx, o.originy)
	elif o.pattern == 'Herringbone':
		# note that there is a lot of extra length and width here to make sure that  we create a pattern w.o. gaps at the edges
		v = o.plankwidth * sqrt(2.0)
		w = o.planklength * sqrt(2.0)
		nplanks = int((o.width+o.planklength + o.originy*2) / v)+1
		nplanksc = int((o.length + o.originx*2) / w)+1
		verts, faces, uvs = herringbone(nplanks, nplanksc,
												o.planklength, o.plankwidth,
												o.longgap, o.shortgap,
												o.randomseed,
												o.randrotx, o.randroty, o.randrotz,
												o.originx, o.originy)
	elif o.pattern == 'Square':
		rows = int((o.width + o.originy)/ o.planklength)+1
		cols = int((o.length + o.originx)/ o.planklength)+1
		verts, faces, uvs = square(rows, cols, o.planklength, o.nsquare, o.border, o.longgap, o.shortgap, o.randomseed,
									o.randrotx, o.randroty, o.randrotz,
									o.originx, o.originy)
	elif o.pattern == 'Versaille':
		rows = int((o.width + o.originy)/ o.planklength)+2
		cols = int((o.length + o.originx)/ o.planklength)+2
		verts, faces, uvs = versaille(rows, cols, 
										o.planklength, o.plankwidth,
										o.longgap, o.shortgap,
										o.randrotx, o.randroty, o.randrotz,
										o.originx, o.originy,
										o.borderswitch)

	# create mesh &link object to scene
	emesh = o.data

	mesh = bpy.data.meshes.new(name='Planks')
	mesh.from_pydata(verts, [], faces)

	mesh.update(calc_edges=True)

	# more than one object can refer to the same emesh
	for i in bpy.data.objects:
		if i.data == emesh:
			i.data = mesh

	name = emesh.name
	emesh.user_clear() # this way the old mesh is marked as used by noone and not saved on exit
	bpy.data.meshes.remove(emesh)
	mesh.name = name
	if bpy.context.mode != 'EDIT_MESH':
		bpy.ops.object.editmode_toggle()
		bpy.ops.object.editmode_toggle()

	bpy.ops.object.shade_smooth()

	# add uv-coords and per face random vertex colors
	rot = Euler((0,0,o.uvrotation))
	mesh.uv_textures.new()
	uv_layer = mesh.uv_layers.active.data
	vertex_colors = mesh.vertex_colors.new().data
	offset = Vector()
	# note that the uvs that are returned are shuffled
	for poly in mesh.polygons:
		color = [rand(), rand(), rand()]
		if o.randomuv == 'Random':
			offset = Vector((rand(), rand(), 0))
		elif o.randomuv == 'Packed':
			x = []
			y = []
			for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
				x.append(uvs[mesh.loops[loop_index].vertex_index].x)
				y.append(uvs[mesh.loops[loop_index].vertex_index].y)
			offset = Vector((-min(x), -min(y), 0))
		for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
			if o.randomuv == 'Shuffle':
				coords = uvs[mesh.loops[loop_index].vertex_index]
			elif o.randomuv == 'Random':
				coords = mesh.vertices[mesh.loops[loop_index].vertex_index].co + offset
			elif o.randomuv == 'Packed':
				coords = uvs[mesh.loops[loop_index].vertex_index] + offset
			else:
				coords = mesh.vertices[mesh.loops[loop_index].vertex_index].co
			coords = Vector(coords) # copy
			coords.x *= o.uvscalex
			coords.y *= o.uvscaley
			coords.rotate(rot)
			uv_layer[loop_index].uv = coords.xy
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
	bpy.ops.object.mode_set(mode='EDIT')
	bm = bmesh.from_edit_mesh(o.data)
	
	# extrude to give thickness
	ret=bmesh.ops.extrude_face_region(bm,geom=bm.faces[:])
	ret=bmesh.ops.translate(bm,vec=Vector((0,0,self.thickness)),verts=[el for el in ret['geom'] if isinstance(el, bmesh.types.BMVert)] )
	
	# trim excess flooring
	ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(o.length,0,0), plane_no=(1,0,0), clear_outer=True)
	ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(0,0,0), plane_no=(-1,0,0), clear_outer=True)
	ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(0,o.width,0), plane_no=(0,1,0), clear_outer=True)
	ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(0,0,0), plane_no=(0,-1,0), clear_outer=True)
	
	# fill in holes caused by the trimming
	open_edges = [e for e in bm.edges if len(e.link_faces)==1]
	bmesh.ops.edgeloop_fill(bm, edges=open_edges, mat_nr=0, use_smooth=False)
	
	creases = bm.edges.layers.crease.active
	if creases is not None:
		for edge in open_edges:
			edge[creases] = 1

	bmesh.update_edit_mesh(o.data)
	bpy.ops.object.mode_set(mode='OBJECT')
	
	# intersect with a floorplan. Note the floorplan must be 2D (all z-coords must be identical) and a closed polygon.
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
		
		# make that copy active and selected
		for ob in context.selected_objects:
			ob.select = False
		fpob.select = True
		context.scene.objects.active = fpob
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
		
		# at this point the floorplan object is the active and selected object
		if True:
			# make the floorboards active and selected
			for ob in context.selected_objects:
				ob.select = False
			context.scene.objects.active = o
			o.select = True
			
			# add-and-apply a boolean modifier to get the intersection with the floorplan copy
			bpy.ops.object.modifier_add(type='BOOLEAN') # default is intersect
			o.modifiers[-1].object = fpob
			if True:
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
			#bpy.ops.object.modifier_add(type='EDGE_SPLIT')
			mods = o.modifiers
			mods[0].show_expanded = False
			#mods[1].show_expanded = False
			mods[0].width = self.bevel
			mods[0].segments = 2
			mods[0].limit_method = 'ANGLE'
			mods[0].angle_limit = (85/90.0)*PI/2
		if warped and not ('SUBSURF' in [m.type for m in mods]):
			bpy.ops.object.modifier_add(type='SUBSURF')
			mods[-1].show_expanded = False
			mods[-1].levels = 2
		if not warped and ('SUBSURF' in [m.type for m in mods]):
			bpy.ops.object.modifier_remove(modifier='Subsurf')

	if self.preservemats and len(material_list)>0:
		rebuildMaterialList(o, material_list)    
		assignRandomMaterial(len(material_list))
		
bpy.types.Object.reg = StringProperty(default='FloorBoards')

bpy.types.Object.length = FloatProperty(name="Length",
										description="Length (X) of the floor in Blender units",
										default=4,
										soft_min=0.5,
										soft_max=40.0,
										subtype='DISTANCE',
										unit='LENGTH',
										update=updateMesh)

bpy.types.Object.width = FloatProperty(name="Width",
										description="Width (Y) of the floor in Blender units",
										default=4,
										soft_min=0.5,
										soft_max=40.0,
										subtype='DISTANCE',
										unit='LENGTH',
										update=updateMesh)

bpy.types.Object.planklength = FloatProperty(name="Length",
											description="Length of a single plank",
											default=2,
											soft_min=0.5,
											soft_max=40.0,
											subtype='DISTANCE',
											unit='LENGTH',
											update=updateMesh)

bpy.types.Object.planklengthvar = FloatProperty(name="Var",
												description="Max Length variation of single planks",
												default=0.2,
												min=0,
												soft_max=40.0,
												subtype='DISTANCE',
												unit='LENGTH',
												update=updateMesh)

bpy.types.Object.plankwidth = FloatProperty(name="Width",
											description="Width of a single plank",
											default=0.18,
											soft_min=0.05,
											soft_max=40.0,
											subtype='DISTANCE',
											unit='LENGTH',
											update=updateMesh)

bpy.types.Object.plankwidthvar = FloatProperty(name="Var",
											description="Max Width variation of single planks",
											default=0,
											min=0,
											soft_max=4.0,
											subtype='DISTANCE',
											unit='LENGTH',
											update=updateMesh)

bpy.types.Object.longgap = FloatProperty(name="Long Gap",
										description="Gap between the long edges of the planks",
										default=0.002,
										min=0,
										soft_max=0.01,
										step=0.01,
										precision=4,
										subtype='DISTANCE',
										unit='LENGTH',
										update=updateMesh)

bpy.types.Object.shortgap = FloatProperty(name="Short Gap",
										description="Gap between the short edges of the planks",
										default=0.0005,
										min=0,
										soft_max=0.01,
										step=0.01,
										precision=4,
										subtype='DISTANCE',
										unit='LENGTH',
										update=updateMesh)

bpy.types.Object.thickness = FloatProperty(name="Thickness",
										description="Thickness of the planks",
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

bpy.types.Object.nsquare = IntProperty(name="Planks per Square",
										description="Number of planks in each square tile",
										default=4,
										min=1,
										update=updateMesh)

bpy.types.Object.border = FloatProperty(name="Border",
										description="Width of border",
										default=0,
										soft_max=0.1,
										min=0,
										subtype='DISTANCE',
										unit='LENGTH',
										update=updateMesh)

bpy.types.Object.originx = FloatProperty(name="OriginX",
										description="X offset of the whole pattern",
										default=0,
										soft_max=1,
										min=0,
										subtype='DISTANCE',
										unit='LENGTH',
										update=updateMesh)

bpy.types.Object.originy = FloatProperty(name="OriginY",
										description="Y offset of the whole pattern",
										default=0,
										soft_max=1,
										min=0,
										subtype='DISTANCE',
										unit='LENGTH',
										update=updateMesh)


bpy.types.Object.randomuv = EnumProperty(name="UV randomization",
										description="Randomization mode for the uv-offset of individual planks",
										items = [('None','None','Plain mapping from top view'),
									         ('Random','Random','Add random offset to plain map of individual planks'),
											 ('Shuffle','Shuffle','Exchange uvmaps of simlilar planks'),
											 ('Packed','Packed','Overlap all uvs of individual planks while maintaining their proportions')],
										update=updateMesh)

bpy.types.Object.modify = BoolProperty(name="Add modifiers",
									description="Add bevel and solidify modifiers to the planks",
									default=True,
									update=updateMesh)

bpy.types.Object.preservemats = BoolProperty(name="Keep materials",
									description="Keep any materials assigned to the mesh",
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

bpy.types.Object.uvrotation = FloatProperty(name="UV Rotation",
										description="Rotation of the generated UV-map",
										default=0,
										step=(1.0 / 180) * PI,
										precision=2,
										subtype='ANGLE',
										unit='ROTATION',
										update=updateMesh)

bpy.types.Object.uvscalex = FloatProperty(name="UV X Scale ",
											description="Scale UV coordinates in the X direction",
											default=1.0,
											step=0.01,
											precision=4,
											update=updateMesh)

bpy.types.Object.uvscaley = FloatProperty(name="UV Y Scale ",
											description="Scale UV coordinates in the Y direction",
											default=1.0,
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

bpy.types.Object.pattern = EnumProperty(name="Pattern",
									description="Pattern of the planks",
									items = [('Regular','Regular','Parallel planks'),
									         ('Herringbone','Herringbone','Herringbone pattern'),
											 ('Square','Square','Alternating square pattern'),
											 ('Versaille','Versaille','Diagonal weave like pattern')],
									update=updateMesh)

bpy.types.Object.borderswitch = BoolProperty(name="Switch border",
									description="Order border plank in a spiral fashion",
									default=False,
									update=updateMesh)


    
class FloorBoards(bpy.types.Panel):
	bl_idname = "FloorBoards"
	bl_label = "Floorgenerator"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Floorgenerator"
	#bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		if bpy.context.mode != 'OBJECT':
			layout.label('Floorgenerator only works in OBJECT mode.')
		else:
			o = context.object
			if 'reg' in o:
				if o['reg'] == 'FloorBoards':
					box = layout.box()
					
					box.prop(o, 'pattern')
					
					box.label('Floordimensions')
					columns = box.row()
					columns.prop(o, 'length')
					columns.prop(o, 'width')
					columns = box.row()
					columns.prop(o, 'originx')
					columns.prop(o, 'originy')

					box.label('Planks')
					if o.pattern in { 'Herringbone', 'Square', 'Versaille'}:
						box.prop(o, 'planklength')
						if o.pattern == 'Square':
							box.prop(o, 'nsquare')
							box.prop(o, 'border')
						elif o.pattern != 'Versaille':
							box.prop(o, 'plankwidth')
					if o.pattern == 'Regular':
						columns = box.row()
						columns.prop(o, 'planklength')
						columns.prop(o, 'planklengthvar')
						columns = box.row()
						columns.prop(o, 'plankwidth')
						columns.prop(o, 'plankwidthvar')
					box.prop(o, 'thickness')
					
					if o.pattern == 'Regular':
						columns = box.row()
						col1 = columns.column()
						col2 = columns.column()
						col1.prop(o, 'offset')
						col2.prop(o, 'randomoffset')
						if o.randomoffset is True:
							col1.enabled = False

					columns = box.row()
					columns.prop(o, 'longgap')
					columns.prop(o, 'shortgap')
					if o.pattern == 'Versaille':
						box.prop(o, 'borderswitch')

					box.label('Randomness')
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

					box.label('Miscellaneous:')
					box.prop(o, 'usefloorplan')
					if o.usefloorplan:
						box.prop(o, 'floorplan')
					row = box.row()
					row.prop(o, 'randomuv')
					row = box.row()
					row.prop(o, 'uvrotation')
					row = box.row()
					row.prop(o, 'uvscalex')
					row.prop(o, 'uvscaley')
					row = box.row()
					row.prop(o, 'modify')
					if o.modify:
						row.prop(o, 'bevel')
					row = box.row()
					row.prop(o,'preservemats')
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
	#bl_options = {"UNDO"}

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
