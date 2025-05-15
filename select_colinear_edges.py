bl_info = {
    "name": "Select Colinear Edges",
    "author": "OpenAI ChatGPT and Michel Anders (varkenvarken)",
    "version": (0, 0, 20250515133231),
    "blender": (4, 4, 0),
    "location": "Mesh > Select > Select All by Trait > Colinear Edges",
    "description": "Selects edges that are colinear with selected ones, with options for connected chains and multiple seeds",
    "category": "Mesh",
}

import bpy
import bmesh
import numpy as np

def are_edges_colinear(a, b, tol=1e-6):
    """Check if two 3D edges are colinear."""
    a0, a1 = np.array(a[0]), np.array(a[1])
    b0, b1 = np.array(b[0]), np.array(b[1])

    va = a1 - a0
    vb = b1 - b0

    cross = np.cross(va, vb)
    if np.linalg.norm(cross) > tol:
        return False

    vab0 = b0 - a0
    cross_check = np.cross(va, vab0)
    if np.linalg.norm(cross_check) > tol:
        return False

    return True

class MESH_OT_select_colinear_edges(bpy.types.Operator):
    """Select colinear edges, with options for connected chains and multi-seed"""
    bl_idname = "mesh.select_colinear_edges"
    bl_label = "Select Colinear Edges"
    bl_options = {'REGISTER', 'UNDO'}

    connected_only: bpy.props.BoolProperty(
        name="Connected Only",
        description="Only grow selection through connected edges",
        default=False
    )

    use_multiple_seeds: bpy.props.BoolProperty(
        name="Use Multiple Selected Edges",
        description="Use all currently selected edges as starting points",
        default=False
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH'

    def execute(self, context):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)
        bm.edges.ensure_lookup_table()
        bm.verts.ensure_lookup_table()

        selected_edges = [e for e in bm.edges if e.select]
        if not selected_edges:
            self.report({'WARNING'}, "No edges selected")
            return {'CANCELLED'}

        seed_edges = selected_edges if self.use_multiple_seeds else [selected_edges[-1]]

        def edge_coords(edge):
            return [(v.co.x, v.co.y, v.co.z) for v in edge.verts]

        for e in bm.edges:
            e.select = False

        visited = set()

        def grow_connected(seed_edge, ref_coords):
            to_visit = {seed_edge}
            chain = set()

            while to_visit:
                current = to_visit.pop()
                if current in chain:
                    continue
                chain.add(current)
                for v in current.verts:
                    for linked in v.link_edges:
                        if linked not in chain and are_edges_colinear(ref_coords, edge_coords(linked)):
                            to_visit.add(linked)
            return chain

        if self.connected_only:
            for seed in seed_edges:
                ref_coords = edge_coords(seed)
                visited.update(grow_connected(seed, ref_coords))
        else:
            for e in bm.edges:
                for seed in seed_edges:
                    if are_edges_colinear(edge_coords(seed), edge_coords(e)):
                        visited.add(e)
                        break

        for e in visited:
            e.select = True

        bmesh.update_edit_mesh(obj.data, loop_triangles=False)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(MESH_OT_select_colinear_edges.bl_idname, text="Colinear Edges")

def register():
    bpy.utils.register_class(MESH_OT_select_colinear_edges)
    bpy.types.VIEW3D_MT_edit_mesh_select_by_trait.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_select_by_trait.remove(menu_func)
    bpy.utils.unregister_class(MESH_OT_select_colinear_edges)

if __name__ == "__main__":
    register()
