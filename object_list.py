#  ##### BEGIN GPL LICENSE BLOCK #####
#
#  ObjectList, a Blender add-on
#  (c) 2021,2025 Michel Anders (varkenvarken)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "ObjectList",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 20250924141758),
    "blender": (4, 4, 0),
    "location": "View3D > Object > Object List",
    "description": "create a comma separated list with object mesh info",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
}

from csv import DictWriter

import bpy
import bmesh


def object_list(context):
    bm = bmesh.new()

    objects = context.scene.objects[:]

    selection_status = {ob: ob.select_get() for ob in objects}
    active_object = context.active_object

    bpy.ops.object.select_all(action="DESELECT")

    for ob in objects:
        ob.select_set(True)
        bpy.ops.object.convert(target="MESH", keep_original=True)

        for ob2 in context.scene.objects:
            if ob2 not in objects:
                tris, faces, edges, verts = 0, 0, 0, 0
                bm.from_mesh(ob2.data)
                tris = len(bm.calc_loop_triangles())
                verts = len(bm.verts)
                edges = len(bm.edges)
                faces = len(bm.faces)

                info = {
                    "Name": ob.name[:],
                    "Type": ob.type[:],
                    "Tris": tris,
                    "Faces": faces,
                    "Edges": edges,
                    "Verts": verts,
                    "Datablock name": ob.data.name[:] if ob.data else None,
                    "Users": ob.data.users,
                }
                for i,c in enumerate(ob.users_collection, start=1):
                    info[f"Collection {i}"] = c.name[:]

                yield info

                bm.clear()

                data = ob2.data
                bpy.data.objects.remove(ob2)
                bpy.data.meshes.remove(data)

    for ob in objects:
        ob.select_set(selection_status[ob])
    bpy.context.view_layer.objects.active = active_object

    bm.free()


class ObjectList(bpy.types.Operator):
    bl_idname = "object.object_list"
    bl_label = "ObjectList"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        oblist = list(object_list(bpy.context))

        t = bpy.data.texts.new(name="Object list.csv")
        dictwriter = DictWriter(
            t,
            fieldnames=[
                "Name",
                "Type",
                "Tris",
                "Faces",
                "Edges",
                "Verts",
                "Datablock name",
                "Users",
                "Collection 1",
                "Collection 2",
                "Collection 3",
            ],
        )
        dictwriter.writeheader()
        dictwriter.writerows(oblist)

        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(
        ObjectList.bl_idname,
        text="Create a comma separated list with object info",
        icon="INFO",
    )


classes = (ObjectList,)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    for c in classes:
        bpy.utils.unregister_class(c)
