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
    "version": (0, 0, 20241230122518),
    "blender": (4, 3, 0),
    "location": "Edit mode 3d-view, Add-->MicroTile",
    "description": "Subdivide selected faces down to a configurable polysize",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

from time import time

import numpy as np

import bpy
from mathutils.geometry import (
    delaunay_2d_cdt as delauney,
    tessellate_polygon as tesselate,
    intersect_point_tri_2d,
)
from mathutils import Vector

profile = lambda x: x

# uncomment this if you want the code to be profiled but make sure to disable it in production code: it easily adds 15% to the runtime
# needs the line_profile package to be installed in Blender.
# See: https://blog.michelanders.nl/2021/06/installing-python-packages-with-pip-in-your-blender-environment.html
# on disabling the addon in the preferences a profile will be written to disk, that can be inspected with for example
# ./Downloads/blender-4.3.1-linux-x64/4.3/python/bin/python3.11 -m line_profiler /tmp/test.prof

# try:
#     from line_profiler import LineProfiler

#     profile = LineProfiler()
# except ImportError:
#     pass

# example: On my machine, selecting 122 faces with an average area of around 5.7 cm2 and a tile size of 1 mm, about 135k tris are added in 6.7 seconds

class MicroTile(bpy.types.Operator):
    bl_idname = "mesh.microtile"
    bl_label = "MicroTile"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Subdivide selected faces down to a configurable polysize"

    size: bpy.props.FloatProperty(
        name="Size",
        description="Size of the micro tiles",
        default=0.01,
        min=0.0001,
        soft_max=10,
        precision=4,
        subtype="DISTANCE",
    )

    @classmethod
    def poll(self, context):
        return context.mode == "EDIT_MESH" and context.active_object.type == "MESH"

    def execute(self, context):
        return self.do_execute(
            context
        )  # Blender doesn´t like it if we apply the @profile decorator to the execute() function directly

    @profile
    def do_execute(self, context):
        start = time()
        # make sure we are in face selection mode
        bpy.ops.mesh.select_mode(type="FACE")

        Z = Vector((0, 0, 1))

        bpy.ops.object.editmode_toggle()  # to object mode
        ob = context.active_object
        me = ob.data

        # we always create a new vertex group and assign any new vertices to it
        vg = ob.vertex_groups.new(name="MicroTiles")

        # get selection status for polygons
        pcount = len(me.polygons)
        pselected = np.empty(pcount, dtype=bool)
        me.polygons.foreach_get("select", pselected)

        # get the positions of all vertices currently in the mesh
        vcount = len(me.vertices)
        shape = (vcount, 3)
        verts = np.empty(vcount * 3, dtype=np.float32)
        me.vertices.foreach_get("co", verts)
        verts.shape = shape

        original_pcount = pcount

        # iterate through all selected polygon indices
        context.window_manager.progress_begin(0, np.count_nonzero(pselected))
        for i, pindex in enumerate(np.flatnonzero(pselected)):
            context.window_manager.progress_update(i)

            pverts = verts[me.polygons[pindex].vertices]
            normal = me.polygons[pindex].normal

            rot2Z = np.array(
                Z.rotation_difference(Vector(normal)).to_matrix()
            )  # rotation towards Z
            rot2Zi = np.array(
                Vector(normal).rotation_difference(Z).to_matrix()
            )  # inverse

            # rotate all vertices of the polygon so it is alligned with the Z-axis
            rotated_pverts = pverts @ rot2Z

            # calculate the bounding box
            pmax = np.max(rotated_pverts, axis=0)
            pmin = np.min(rotated_pverts, axis=0)

            # we start out with the verts that define the polygon but we drop the z dimension
            new_vertices = list(rotated_pverts[:, :2])

            # tesselate the polygon
            tris = tesselate(
                [rotated_pverts]
            )  # input is a list of polylines, even if it is just a single one. Without the list you get a TypeError: tessellate_polygon: parse coord

            grid = []
            # we asume that the z dimension is completely flat, i.e. minimum and maximum in that dimension are the same so we pick one
            # TODO use the average z-position
            z = pmin[2]

            # create a grid of new vertices in the plane of the bounding box
            # and reject any that are not inside the actual (rotated) polygon
            x = pmin[0]
            mx = pmax[0] - self.size
            while x < mx:
                x += self.size
                y = pmin[1]
                my = pmax[1] - self.size
                while y < my:
                    y += self.size
                    pt = Vector([x, y])
                    intersect = False
                    for tri in tris:
                        points = [rotated_pverts[i] for i in tri]
                        if intersect_point_tri_2d(pt, *points):
                            intersect = True  # TODO can we add a break here?
                    if intersect:
                        grid.append((x, y, z))

            # add all new vertices in one go
            if len(grid):
                me.vertices.add(len(grid))
                # rotate vertex position back into the original plane
                rgrid = np.array(grid) @ rot2Zi
                # get the positions of all vertices currently in the mesh, incl. the newly added ones
                vcount2 = len(me.vertices)
                shape = (vcount2, 3)
                verts = np.empty(vcount2 * 3, dtype=np.float32)
                me.vertices.foreach_get("co", verts)
                verts.shape = shape
                # update with the new coords
                # print(f"{vcount=} {vcount2} {grid.shape=}")
                verts[vcount:] = rgrid
                me.vertices.foreach_set("co", verts.flatten())  # TODO 10% of the time is spent here
                new_vertices.extend(Vector(v[:2]) for v in grid)
                vcount = vcount2

            # the Delauney triangulation will create tris between the collection of
            # new vertices and the ones that made up the original polygon
            # (even if none of the grid verts was added, if which case we effectively triangulate the original face)
            vert_coords, edges, faces, orig_verts, orig_edges, orig_faces = (
                delauney(  # triangulation is done with the 2d (i.e. rotated) verts
                    new_vertices, [], [], 0, 1e-6, True
                )
            )

            # we create new polygons for all the tris in a very naive way:
            # we simply create the face along with the vertices. That will
            # result in a lot of duplicate vertices, but we remove all of them
            # in one go with the help of the remove doubles operator.
            nfaces = len(faces)
            me.vertices.add(nfaces * 3)
            for nf, f in enumerate(faces):
                for ni, vi in enumerate(f):
                    co = vert_coords[vi].to_3d()
                    co.z = z
                    me.vertices[vcount + nf * 3 + ni].co = (
                        np.array(co) @ rot2Zi
                    )

            # we add the same number of loops as we did add verts, so their indices should match up
            lcount = len(me.loops)
            me.loops.add(3 * nfaces)
            newlcount = len(me.loops)
            ldata = np.empty(newlcount, dtype=np.int32)
            me.loops.foreach_get("vertex_index", ldata)  # TODO 13% of the time is spent here
            ldata[lcount:] = np.arange(vcount, vcount + 3 * nfaces, dtype=np.int32)
            me.loops.foreach_set("vertex_index", ldata)  # TODO 16% of the time is spent here

            me.polygons.add(nfaces)
            newpcount = len(me.polygons)
            # print(f"{lcount=} {newlcount=} {pcount=} {newpcount=}")
            pdata = np.empty(newpcount, dtype=np.int32)
            me.polygons.foreach_get("loop_start", pdata)
            pdata[pcount:] = np.arange(lcount, newlcount, 3, dtype=np.int32)
            me.polygons.foreach_set("loop_start", pdata)
            me.polygons.foreach_get("loop_total", pdata)
            pdata[pcount:] = 3
            me.polygons.foreach_set("loop_total", pdata)

            while pcount < newpcount:
                me.polygons[pcount].vertices = [
                    vcount,
                    vcount + 1,
                    vcount + 2,
                ]
                vcount += 3
                pcount += 1

        me.update(calc_edges=True)
        me.validate()

        context.window_manager.progress_end()

        bpy.ops.object.editmode_toggle()  # to edit mode

        # remove any overlapping verts we created
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(
            threshold=1e-4
        )  # TODO make this dependent on the grid size? Because with a size of 1e-3, 1e-5 will miss vertices

        # unselect everything
        bpy.ops.mesh.select_all(action="DESELECT")

        bpy.ops.object.editmode_toggle()  # to object mode

        # add the new vertices we created to the new vertex group
        for p in range(original_pcount, len(me.polygons)):
            vg.add(me.polygons[p].vertices, 1.0, "REPLACE")

        # select the orginally selected polygons and remove their vertices from the vertex group
        # TODO this isn´t perfect yet; because of the remove doubles, sometimes one of the new vertices will be at the exact same position (so the wrong one was deduplicated)
        for p in np.flatnonzero(pselected):
            me.polygons[p].select = True
            vg.remove(me.polygons[p].vertices)

        # update the mesh (creating edge data for example)
        me.update()

        bpy.ops.object.editmode_toggle()  # to edit mode

        # remove the original polygons (that are still selected at this point) from the mesh
        bpy.ops.mesh.delete(type="FACE")

        self.report({"INFO"}, f"time: {time()-start:.3f}")  # 6.7 seconds 0.001m

        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(
        MicroTile.bl_idname, text="Tile selected faces", icon="MESH_GRID"
    )


def register():
    bpy.utils.register_class(MicroTile)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    bpy.utils.unregister_class(MicroTile)
    try:
        profile.dump_stats("/tmp/test.prof")
    except AttributeError:
        pass  # ignore if we did not actually create a LineProfiler instance


if __name__ == "__main__":
    register()
