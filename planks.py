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
    "author": "Michel Anders (varkenvarken) with contributions from Alain (Alain)",
    "version": (0, 0, 7),
    "blender": (2, 67, 0),
    "location": "View3D > Add > Mesh",
    "description": "Adds a mesh representing floor boards (planks)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}

from random import random as rand, seed, uniform as randuni
from math import pi as PI
import bpy, bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty
from mathutils import Vector, Euler

# Vector.rotate() does NOT return anything, contrary to what the docs say
def rotate(v, r):
    v2 = v.copy()
    v2.rotate(r)
    return v2
    
def plank(start, end, left, right, longgap, shortgap, rot=None):
    ll = Vector((start, left, 0))
    lr = Vector((start, right - longgap, 0))
    ul = Vector((end - shortgap, right - longgap, 0))
    ur = Vector((end - shortgap, left, 0))
    if rot :
        midpoint = Vector((start + end / 2, left + right / 2, 0))
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
    c = offset #Offset per row
    ws = 0
    p = 0

    while p < n:
        p += 1
        w = width + randuni(0, widthvar)
        we = ws + w
        if randomoffset:
            e = randuni(0,length) # I think we should change length into offset. That way we have indepent control of of the offset variation
        #print ("Offset:",e)
        #print("row",p)
        while e < m:
            #print("plank",s,e)
            ll = len(verts)
            rot = Euler((randrotx * randuni(-1,1),randroty * randuni(-1,1), randrotz * randuni(-1,1)), 'XYZ')
            verts.extend(plank(s, e, ws, we, longgap, shortgap, rot))
            faces.append((ll, ll + 1, ll + 2, ll + 3))
            shortedges.extend([(ll, ll + 1), (ll + 2, ll + 3)])
            longedges.extend([(ll + 1, ll + 2 ), (ll + 3, ll)])
            s = e
            e += length + randuni(0,lengthvar)
        #print("end plank",s,e)
        ll = len(verts)
        rot = Euler((randrotx * randuni(-1,1), randroty * randuni(-1,1), randrotz * randuni(-1,1)), 'XYZ')
        verts.extend(plank(s, m, ws, we, longgap, shortgap, rot))
        faces.append((ll, ll + 1, ll + 2, ll + 3))
        shortedges.extend([(ll, ll + 1), (ll + 2, ll + 3)])
        longedges.extend([(ll + 1, ll + 2 ), (ll + 3, ll)])
        s = 0
        #e = e - m
        if c <= (length):
            c = c + offset
        if c > (length):
            c = c - length
        e = c
        #print ("e, c: ", e, c)
        ws = we
    return verts, faces, shortedges, longedges

class FloorBoards(bpy.types.Operator):
    bl_idname = "mesh.floor_boards"
    bl_label = "FloorBoards"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    length = FloatProperty(name="Floor Area Length",
                    description="Length of the floor in Blender units",
                    default=4,
                    soft_min=0.5,
                    soft_max=40.0,
                    subtype='DISTANCE',
                    unit='LENGTH')

    nplanks = IntProperty(name="Number of planks",
                    description="Number of planks (the width)",
                    default=5,
                    soft_min=1)

    planklength = FloatProperty(name="Plank Length",
                    description="Length of a single plank",
                    default=2,
                    soft_min=0.5,
                    soft_max=40.0,
                    subtype='DISTANCE',
                    unit='LENGTH')

    planklengthvar = FloatProperty(name="Max Length Var",
                    description="Max Length variation of single planks",
                    default=0.2,
                    min=0,
                    soft_max=40.0,
                    subtype='DISTANCE',
                    unit='LENGTH')

    plankwidth = FloatProperty(name="Plank Width",
                    description="Width of a single plank",
                    default=0.18,
                    soft_min=0.05,
                    soft_max=40.0,
                    subtype='DISTANCE',
                    unit='LENGTH')

    plankwidthvar = FloatProperty(name="Max Width Var",
                    description="Max Width variation of single planks",
                    default=0,
                    min=0,
                    soft_max=4.0,
                    subtype='DISTANCE',
                    unit='LENGTH')

    longgap = FloatProperty(name="Long Gap",
                    description="Gap between long edges of planks",
                    default=0.002,
                    min=0,
                    soft_max=0.01,
                    step=0.01,
                    precision=4,
                    subtype='DISTANCE',
                    unit='LENGTH')

    shortgap = FloatProperty(name="Short Gap",
                    description="Gap between short edges of planks",
                    default=0.0005,
                    min=0,
                    soft_max=0.01,
                    step=0.01,
                    precision=4,
                    subtype='DISTANCE',
                    unit='LENGTH')

    thickness = FloatProperty(name="Thickness",
                    description="Thickness of planks",
                    default=0.018,
                    soft_max=0.1,
                    step=0.1,
                    precision=3,
                    subtype='DISTANCE',
                    unit='LENGTH')

    bevel = FloatProperty(name="Bevel",
                    description="Bevel width planks",
                    default=0.001,
                    min=0,
                    soft_max=0.01,
                    step=0.01,
                    precision=4,
                    subtype='DISTANCE',
                    unit='LENGTH')

    offset = FloatProperty(name="Offset",
                    description="Offset per row in Blender Units",
                    default=0.4,
                    min=0,
                    soft_max=2,
                    subtype='DISTANCE',
                    unit='LENGTH')
                 
    randomoffset = BoolProperty(name="Offset random",
                    description="Uses random values for offset",
                    default=False)           

    randomseed = IntProperty(name="Random Seed",
                    description="The seed governing random generation",
                    default=0,
                    min=0)

    randomuv = BoolProperty(name="Randomize UVs",
                    description="Randomize the uv-offset of individual planks",
                    default=True)

    modifiers = BoolProperty(name="Add modifiers",
                    description="Add bevel and solidify modifiers to the planks",
                    default=True)

    randrotx = FloatProperty(name="X Rotataion",
                    description="Randam rotation of individual planks around x-axis",
                    default=0,
                    min=0,
                    soft_max=0.01,
                    step=(0.02/180)*PI,
                    precision=4,
                    subtype='ANGLE',
                    unit='ROTATION')

    randroty = FloatProperty(name="Y Rotataion",
                    description="Randam rotation of individual planks around y-axis",
                    default=0,
                    min=0,
                    soft_max=0.01,
                    step=(0.02/180)*PI,
                    precision=4,
                    subtype='ANGLE',
                    unit='ROTATION')

    randrotz = FloatProperty(name="Z Rotataion",
                    description="Randam rotation of individual planks around z-axis",
                    default=0,
                    min=0,
                    soft_max=0.01,
                    step=(0.02/180)*PI,
                    precision=4,
                    subtype='ANGLE',
                    unit='ROTATION')

    @classmethod
    def poll(self, context):
        # Check if we are in object mode
        return context.mode == 'OBJECT'


    def execute(self, context):
        verts, faces, shortedges, longedges = planks(self.nplanks, self.length,
            self.planklength, self.planklengthvar,
            self.plankwidth, self.plankwidthvar,
            self.longgap, self.shortgap,
            self.offset, self.randomoffset,
            self.randomseed,
            self.randrotx, self.randroty, self.randrotz)

        # create mesh &link object to scene
        mesh = bpy.data.meshes.new('Planks')
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges=True)

        # add uv-coords and per face random vertex colors
        mesh.uv_textures.new()
        uv_layer = mesh.uv_layers.active.data
        vertex_colors = mesh.vertex_colors.new().data
        for poly in mesh.polygons:
            offset = Vector((rand(),rand(),0)) if self.randomuv else Vector((0,0,0)) 
            color = [rand(), rand(), rand()]
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                coords = mesh.vertices[mesh.loops[loop_index].vertex_index].co
                uv_layer[loop_index].uv = (coords + offset).xy
                vertex_colors[loop_index].color = color

        obj_new = bpy.data.objects.new(mesh.name, mesh)
        base = bpy.context.scene.objects.link(obj_new)
        for ob in bpy.context.scene.objects:
            ob.select = False
        base.select = True
        bpy.context.scene.objects.active = obj_new
        
        if self.modifiers:
            # add solidify modifier to give planks thickness
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            bpy.context.active_object.modifiers[0].thickness = self.thickness

            # add bevel modifier
            bpy.ops.object.modifier_add(type='BEVEL')
            bpy.context.active_object.modifiers[1].width = self.bevel
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, 'length')
        box.prop(self, 'nplanks')
        
        box = layout.box()
        box.prop(self, 'planklength')
        box.prop(self, 'planklengthvar')
        box.prop(self, 'plankwidth')
        box.prop(self, 'plankwidthvar')
        box.prop(self, 'thickness')
        box.prop(self, 'offset')
        box.prop(self, 'randomoffset')
        box.prop(self, 'longgap')
        box.prop(self, 'shortgap')
        box.prop(self, 'bevel')
        
        box = layout.box()
        box.prop(self, 'randrotx')
        box.prop(self, 'randroty')
        box.prop(self, 'randrotz')
        
        box = layout.box()
        box.prop(self, 'randomuv')
        box.prop(self, 'modifiers')
        layout.prop(self, 'randomseed')

def menu_func(self, context):
    self.layout.operator(FloorBoards.bl_idname, text="Add floor board mesh",
                                                icon='PLUGIN')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()