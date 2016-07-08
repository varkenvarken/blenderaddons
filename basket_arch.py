# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Basket Arch, a Blender addon
#  (c) 2014,2015 Michel J. Anders (varkenvarken)
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
	"name": "Basket Arch",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 20150206),
	"blender": (2, 73, 0),
	"location": "View3D > Add > Mesh",
	"description": "Adds a basket arch mesh",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Add Mesh"}
									
from math import atan2, asin, sin, cos, pi, degrees, sqrt
import bpy, bmesh
from bpy.props import FloatProperty, BoolProperty, FloatVectorProperty, IntProperty, BoolVectorProperty
from bpy_extras import object_utils

def circle(x,y,r,s,e,w):
	co = []
	# in Blender z is considered up
	if s <= e :
		while s <= e :
			co.append((x+r*cos(s),0,y+r*sin(s)))
			s += w
	else:
		while s >= e :
			co.append((x+r*cos(s),0,y+r*sin(s)))
			s -= w
	return co

def calc_radii(W,H):
	r = 2*H/3.0
	h = H/3.0
	w = W/2.0
	alpha = atan2(h, w)
	b = sqrt(w*w + h*h)
	s = b/sin(alpha)
	c = s - h
	R = c + H
	
	return r,R,c

def R(w,h):
	"""
	calculate the y poistion of the center circle of a basket arch given half the width and the height.
	"""
	a = h/3.0
	beta = atan2(a,w)
	c = sqrt(a**2 + w**2)
	d = c/2.0
	e = d/sin(beta)
	return e-a
	
def c(xA,yA,rA, xB,yB,rB):
	"""
	return the interection point(s) of two circles.
	"""
	d2 = (xB-xA)**2 + (yB-yA)**2 
	K = (1/4.0) * sqrt(((rA+rB)**2-d2) * (d2-(rA-rB)**2))
	
	xb = (1/2.0)*(xB+xA) + (1/2.0)*(xB-xA)*(rA**2-rB**2)/d2
	dx = 2*(yB-yA)*K/d2 
	yb = (1/2.0)*(yB+yA) + (1/2.0)*(yB-yA)*(rA**2-rB**2)/d2
	dy = -2*(xB-xA)*K/d2

	return ((xb+dx,yb+dy), (xb-dx,yb-dy))

	
def basket_arch(W,D,H=0,resolution=1):
	if (H > 0) and (W/H >= 2.0) and (W/H <= 4.0):
		w=2*H/3.0
		s=W/2.0-w
		rc = R(s,H)
		r = rc + H
		c1x = -s
		c1y = 0
		cmx = 0
		cmy = -rc
		c2x = s
		c2y = 0
		CX,CY = c(c1x,c2x,w, cmx,cmy,r)[0]
		dx = -CX
		dy = CY + rc
		beta = atan2(dx,dy)
		dx = -CX-s
		dy = CY
		alpha = atan2(dx,dy)
		
	else:
		w = W / 4.0
		h = sqrt(3.0) * w
		r = 3.0 * w
		c1x = -w
		c1y = 0
		cmx = 0
		cmy = -h
		c2x = w
		c2y = 0
		#alpha = atan2(h, 2.0 * w)
		beta = atan2(w , h)
		alpha = beta
		
	co =   circle(c1x, c1y, w, pi             , pi / 2.0 + alpha, resolution * 3*pi/360)
	co +=  circle(cmx, cmy, r, pi / 2.0 + beta, pi / 2.0 - beta, resolution *   pi/360)
	# reversing the generation of the points in this segment will ensure these segments are symmetrical
	# reversing the resulting list is necessary to maintain the order of the generated polygons
	co +=  reversed(circle(c2x, c2y, w, 0.0	  , pi / 2.0 - alpha, resolution * 3*pi/360))
	
	n = len(co)
	return co + [(x,y+D,z) for x,y,z in co], [(i,i+1,n+i+1,n+i) for i in range(n-1)]

class BasketArch(bpy.types.Operator):
	bl_idname = 'mesh.basketarch'
	bl_label = 'Create a basket arch'
	bl_options = {'REGISTER','UNDO'}

	view_align = BoolProperty(
			name="Align to View",
			default=False,
			)
	location = FloatVectorProperty(
			name="Location",
			subtype='TRANSLATION',
			)
	rotation = FloatVectorProperty(
			name="Rotation",
			subtype='EULER',
			)
	width = FloatProperty(
			name="Width",description="Width of the basket arch (span)",
			default=4,
			subtype='DISTANCE',
			unit='LENGTH')
	height = FloatProperty(
			name="Height",description="Height of the basket arch (0 if classical)",
			default=0,
			subtype='DISTANCE',
			unit='LENGTH')
	depth = FloatProperty(
			name="Depth",description="Depth of the basket arch",
			default=1,
			subtype='DISTANCE',
			unit='LENGTH')
	resolution = IntProperty(
			name="Resolution", description="Higher values = less polygons",
			default=1,
			min = 1)
	layers = BoolVectorProperty( # see: https://developer.blender.org/rB0f63ce61c52fce82f18df687369d513c3b6c19b1
			name="Layers",
			subtype='LAYER',
			description="Object Layers",
			size=20,
			)

	def execute(self, context):

		verts_loc, faces = basket_arch(self.width, self.depth, self.height, self.resolution)

		mesh = bpy.data.meshes.new("BasketArch")

		bm = bmesh.new()

		for v_co in verts_loc:
			bm.verts.new(v_co)

		# see http://blenderartists.org/forum/archive/index.php/t-354412.html for next bit
		if hasattr(bm.verts, "ensure_lookup_table"):
			bm.verts.ensure_lookup_table()
		
		for f_idx in faces:
			bm.faces.new([bm.verts[i] for i in f_idx])

		bm.to_mesh(mesh)
		mesh.update()

		object_utils.object_data_add(context, mesh, operator=self)

		return {"FINISHED"}

def menu_func(self, context):
	self.layout.operator(BasketArch.bl_idname, text="Create a basket arch mesh",
						icon='PLUGIN')

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
	bpy.types.INFO_MT_mesh_add.remove(menu_func)
	bpy.utils.unregister_module(__name__)
