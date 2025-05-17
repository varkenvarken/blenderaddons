bl_info = {
    "name": "Select Colinear Edges",
    "author": "michel.anders, GitHub Copilot",
    "version": (1, 1, 20250517142157),
    "blender": (4, 4, 0),
    "location": "View3D > Select > Select Similar > Colinear Edges",
    "description": "Select all edges colinear with any currently selected edge, optionally only along colinear paths",
    "category": "Mesh",
}

import bpy
import bmesh
from mathutils import Vector


class MESH_OT_select_colinear_edges(bpy.types.Operator):
    """Select all edges colinear with any currently selected edge, optionally only along colinear paths"""

    bl_idname = "mesh.select_colinear_edges"
    bl_label = "Colinear Edges"
    bl_options = {"REGISTER", "UNDO"}

    angle_threshold: bpy.props.FloatProperty(
        name="Angle Threshold",
        description="Maximum angle (degrees) to consider edges colinear",
        default=1.0,
        min=0.0,
        max=10.0,
    )

    only_colinear_paths: bpy.props.BoolProperty(
        name="Only Colinear Paths",
        description="Only select edges connected via colinear paths from the originally selected edges",
        default=True,
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and context.mode == "EDIT_MESH"

    def execute(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        bm.edges.ensure_lookup_table()

        # Find all originally selected edges
        original_selected_edges = [e for e in bm.edges if e.select]
        if not original_selected_edges:
            self.report({"WARNING"}, "No edges selected")
            return {"CANCELLED"}

        # Deselect all edges first
        for e in bm.edges:
            e.select = False

        threshold_rad = self.angle_threshold * 3.14159265 / 180.0

        def edge_dir(edge):
            v1, v2 = edge.verts
            return (v2.co - v1.co).normalized()

        def are_colinear(e1, e2):
            # Check if direction vectors are parallel
            dir1 = edge_dir(e1)
            # guard against zero length edges
            if dir1.length < 1e-6:
                return False
            dir2 = edge_dir(e2)
            if dir2.length < 1e-6:
                return False
            angle = dir1.angle(dir2)
            if not (angle < threshold_rad or abs(angle - 3.14159265) < threshold_rad):
                return False
            # Check if the vector between their start points is also parallel to the direction
            v1 = e1.verts[0].co
            w1 = e2.verts[0].co
            between = w1 - v1
            # If between is zero vector, they share a vertex, so colinear
            if between.length < 1e-6:
                return True
            between_dir = between.normalized()
            angle2 = dir1.angle(between_dir)
            return angle2 < threshold_rad or abs(angle2 - 3.14159265) < threshold_rad

        if self.only_colinear_paths:
            visited = set()
            queue = []
            for e in original_selected_edges:
                queue.append(e)
                visited.add(e)

            while queue:
                current_edge = queue.pop(0)
                current_edge.select = True
                for v in current_edge.verts:
                    for neighbor in v.link_edges:
                        if neighbor is current_edge or neighbor in visited:
                            continue
                        if are_colinear(current_edge, neighbor):
                            queue.append(neighbor)
                            visited.add(neighbor)
        else:
            for e in bm.edges:
                for sel_edge in original_selected_edges:
                    if are_colinear(sel_edge, e):
                        e.select = True
                        break

        bmesh.update_edit_mesh(obj.data)
        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(MESH_OT_select_colinear_edges.bl_idname, text="Colinear Edges")


def register():
    bpy.utils.register_class(MESH_OT_select_colinear_edges)
    bpy.types.VIEW3D_MT_edit_mesh_select_similar.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_select_similar.remove(menu_func)
    bpy.utils.unregister_class(MESH_OT_select_colinear_edges)


if __name__ == "__main__":
    register()
