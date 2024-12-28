# ##### BEGIN GPL LICENSE BLOCK #####
#
#  MicroTile, (c) 2024 Michel Anders (varkenvarken)
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
    "name": "MicroTile",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 20241228101222),
    "blender": (4, 3, 0),
    "location": "Edit mode 3d-view, Add-->MicroTile",
    "description": "Subdivide selected faces down to a configurable polysize",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

import numpy as np

import bpy
from mathutils.geometry import delaunay_2d_cdt as delauney
from mathutils import Vector


def planefit(points):
    ctr = points.mean(axis=0)
    x = points - ctr
    M = np.cov(x.T)
    eigenvalues, eigenvectors = np.linalg.eig(M)
    normal = eigenvectors[:, eigenvalues.argmin()]
    return ctr, normal


def orthopoints(normal):
    m = np.argmax(normal)
    x = np.ones(3, dtype=np.float32)
    x[m] = 0
    x /= np.linalg.norm(x)
    x = np.cross(normal, x)
    y = np.cross(normal, x)
    return x, y


class MicroTile(bpy.types.Operator):
    bl_idname = "mesh.microtile"
    bl_label = "MicroTile"
    bl_options = {"REGISTER", "UNDO"}

    size: bpy.props.FloatProperty(
        name="Size",
        description="Size of the micro tiles",
        default=0.01,
        min=0,
        soft_max=10,
        subtype="DISTANCE",
    )

    @classmethod
    def poll(self, context):
        return context.mode == "EDIT_MESH" and context.active_object.type == "MESH"

    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        ob = context.active_object
        me = ob.data

        # get polygon data
        pcount = len(me.polygons)
        pselected = np.empty(pcount, dtype=bool)
        me.polygons.foreach_get("select", pselected)
        vcount = len(me.vertices)

        # get the positions of all vertices
        shape = (vcount, 3)
        verts = np.empty(vcount * 3, dtype=np.float32)
        me.vertices.foreach_get("co", verts)
        verts.shape = shape

        for pindex in np.flatnonzero(pselected):
            pverts = verts[me.polygons[pindex].vertices]
            center, normal = planefit(pverts)
            a, b = orthopoints(normal)
            print(f"{center=} {normal=} {a=} {b=}")
            pmax = np.max(pverts, axis=0)
            pmin = np.min(pverts, axis=0)
            print(f"{pmin=} {pmax=}")

            new_vertices = list(pverts[:, :2])
            # we asume for a moment that the z dimension is flat
            z = pmin[2]

            x = pmin[0]
            mx = pmax[0] - self.size
            while x < mx:
                x += self.size
                y = pmin[1]
                my = pmax[1] - self.size
                while y < my:
                    y += self.size
                    print([x, y, z])
                    me.vertices.add(1)
                    me.vertices[vcount].co = [x, y, z]
                    vcount += 1
                    new_vertices.append(Vector([x, y]))

            vert_coords, edges, faces, orig_verts, orig_edges, orig_faces = delauney(
                new_vertices, [], [], 0, 1e-6, True
            )

            print(
                f"{vert_coords=}\n{edges=}\n{faces=}\n{orig_verts=}\n{orig_edges=}\n{orig_faces}"
            )

            for f in faces:
                me.vertices.add(3)
                for i, vi in enumerate(f):
                    co = vert_coords[vi].to_3d()
                    co.z = z
                    me.vertices[vcount + i].co = co
                lcount = len(me.loops)
                me.loops.add(3)
                me.polygons.add(1)
                me.polygons[pcount].loop_start = lcount
                me.polygons[pcount].vertices = [
                    vcount,
                    vcount + 1,
                    vcount + 2,
                ]
                vcount += 3
                pcount += 1

            me.update(calc_edges=True)

        bpy.ops.object.editmode_toggle()

        bpy.ops.mesh.remove_doubles(threshold=1e-5)
        bpy.ops.mesh.select_all(action="DESELECT")

        bpy.ops.object.editmode_toggle()
        for p in np.flatnonzero(pselected):
            print(p)
            me.polygons[p].select = True
        me.update()
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.delete(type='FACE')
        
        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(MicroTile.bl_idname, text="Tile selected faces", icon="PLUGIN")


def register():
    bpy.utils.register_class(MicroTile)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    bpy.utils.unregister_class(MicroTile)


if __name__ == "__main__":
    register()
