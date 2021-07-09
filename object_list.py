#  ##### BEGIN GPL LICENSE BLOCK #####
#  
#  ObjectList, a Blender add-on
#  (c) 2021 Michel Anders (varkenvarken)
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
    "version": (0, 0, 202107090943),
    "blender": (2, 93, 0),
    "location": "View3D > Object > Object List",
    "description": "create a comma separated list with object info",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"}

import bpy
import bmesh

def object_list(context):
    bm = bmesh.new()
    depsgraph = context.view_layer.depsgraph
    for ob in context.scene.objects:
        tris, faces, edges, verts = 0,0,0,0
        if ob.type == 'MESH':
            bm.from_object(ob, depsgraph, face_normals=False)
            tris = len(bm.calc_loop_triangles())
            verts = len(bm.verts)
            edges = len(bm.edges)
            faces = len(bm.faces)
        yield ob.name, ob.type, tris, faces, edges, verts, ob.data.name if ob.data else None, ob.data.users if ob.data else 1, ",".join(c.name for c in ob.users_collection)
        bm.clear()
    bm.free()

class ObjectList(bpy.types.Operator):
    bl_idname = "object.object_list"
    bl_label = "ObjectList"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        t = bpy.data.texts.new(name="Object list.csv")
        t.write(",".join(("Name","Type","Tris", "Faces", "Edges", "Verts", "Datablock name","Users", "Collection 1","Collection 2","Collection 3")))
        t.write("\n")
        for ob in object_list(bpy.context):
            t.write(",".join(map(str,ob)))
            t.write("\n")
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ObjectList.bl_idname, text="Create a comma separated list with object info",
                        icon='INFO')


classes = (ObjectList, )

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    for c in classes:
        bpy.utils.unregister_class(c)
