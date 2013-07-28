# ##### BEGIN GPL LICENSE BLOCK #####
#
#  SCA Tree Generator, a Blender addon
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
    "name": "Floor Board Generator",
    "author": "michel anders (varkenvarken)",
    "version": (0, 0, 1),
    "blender": (2, 67, 0),
    "location": "View3D > Add > Mesh",
    "description": "Adds a mesh representing floor boards (planks)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}

from random import random as rand, seed
import bpy, bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty
from mathutils import Vector

def plank(start, end, left, right, longgap, shortgap):
    verts = (
        Vector((start, left, 0)),
        Vector((start, right - longgap, 0)),
        Vector((end - shortgap, right - longgap, 0)),
        Vector((end - shortgap, left, 0))
    )
    return verts

def planks(n, m,
    length, lengthvar,
    width, widthvar,
    longgap, shortgap,
    offset,
    nseed):

    verts = []
    faces = []
    shortedges = []
    longedges = []

    seed(nseed)
    widthoffset = 0
    s = 0
    e = offset
    ws = 0
    p = 0
    while p < n:
        p += 1
        w = width + widthvar * rand()
        we = ws + w
        #print("row",p)
        while e < m:
            #print("plank",s,e)
            ll = len(verts)
            verts.extend(plank(s, e, ws, we, longgap, shortgap))
            faces.append((ll, ll + 1, ll + 2, ll + 3))
            shortedges.extend([(ll, ll + 1), (ll + 2, ll + 3)])
            longedges.extend([(ll + 1, ll + 2 ), (ll + 3, ll)])
            s = e
            e += length + lengthvar * rand()
        #print("end plank",s,e)
        ll = len(verts)
        verts.extend(plank(s, m, ws, we, longgap, shortgap))
        faces.append((ll, ll + 1, ll + 2, ll + 3))
        shortedges.extend([(ll, ll + 1), (ll + 2, ll + 3)])
        longedges.extend([(ll + 1, ll + 2 ), (ll + 3, ll)])
        s = 0
        e = e - m
        ws = we
    return verts, faces, shortedges, longedges

class FloorBoards(bpy.types.Operator):
    bl_idname = "mesh.floor_boards"
    bl_label = "FloorBoards"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    length = FloatProperty(name="Floor Length",
                    description="Length of the floor in Blender units",
                    default=4,
                    min=0.5,
                    soft_max=40.0,
                    subtype='DISTANCE',
                    unit='LENGTH')

    nplanks = IntProperty(name="Number of planks",
                    description="Number of planks (the width)",
                    default=5,
                    min=0)

    planklength = FloatProperty(name="Plank Length",
                    description="Length of a single plank",
                    default=2,
                    min=0.5,
                    soft_max=40.0,
                    subtype='DISTANCE',
                    unit='LENGTH')

    planklengthvar = FloatProperty(name="Length Var",
                    description="Length variation of single planks",
                    default=0.2,
                    min=0,
                    soft_max=40.0,
                    subtype='DISTANCE',
                    unit='LENGTH')

    plankwidth = FloatProperty(name="Plank Width",
                    description="Width of a single plank",
                    default=0.18,
                    min=0.05,
                    soft_max=40.0,
                    subtype='DISTANCE',
                    unit='LENGTH')

    plankwidthvar = FloatProperty(name="Width Var",
                    description="Width variation of single planks",
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
                    description="Offset of the first plank",
                    default=0.4,
                    min=0,
                    soft_max=2,
                    subtype='DISTANCE',
                    unit='LENGTH')

    randomseed = IntProperty(name="Random Seed",
                    description="The seed governing random generation",
                    default=0,
                    min=0)

    @classmethod
    def poll(self, context):
        # Check if we are in object mode
        return context.mode == 'OBJECT'


    def execute(self, context):
        verts, faces, shortedges, longedges = planks(self.nplanks, self.length,
            self.planklength, self.planklengthvar,
            self.plankwidth, self.plankwidthvar,
            self.longgap, self.shortgap,
            self.offset,
            self.randomseed)

        # create mesh &link object to scene
        mesh = bpy.data.meshes.new('Planks')
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges=True)
        obj_new = bpy.data.objects.new(mesh.name, mesh)
        base = bpy.context.scene.objects.link(obj_new)
        for ob in bpy.context.scene.objects:
            ob.select = False
        base.select = True
        bpy.context.scene.objects.active = obj_new
        
        # add solidify modifier to give planks thickness
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.active_object.modifiers[0].thickness = self.thickness

        # add bevel modifier
        bpy.ops.object.modifier_add(type='BEVEL')
        bpy.context.active_object.modifiers[1].width = self.bevel
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        layout.prop(self, 'length')
        layout.prop(self, 'nplanks')
        layout.prop(self, 'planklength')
        layout.prop(self, 'planklengthvar')
        layout.prop(self, 'plankwidth')
        layout.prop(self, 'plankwidthvar')
        layout.prop(self, 'thickness')
        layout.prop(self, 'offset')
        layout.prop(self, 'longgap')
        layout.prop(self, 'shortgap')
        layout.prop(self, 'bevel')
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