#  ray_trace_renderer.py (c) 2018 Michel Anders (varkenvarken)
#
#  A Blender add-on to illustrate ray tracing concepts
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

bl_info = {
    "name": "ray_trace_renderer",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 201805271642),
    "blender": (2, 79, 0),
    "location": "",
    "description": "Create a ray traced image of the current scene",
    "warning": "",
    "wiki_url": "https://blog.michelanders.nl/2018/05/raytracing-concepts-and-code.html",
    "category": "Render",
}

import bpy
import numpy as np
from mathutils import Vector

def ray_trace(scene, width, height):     

    lamps = [ob for ob in scene.objects if ob.type == 'LAMP']

    intensity = 10  # intensity for all lamps
    eps = 1e-5      # small offset to prevent self intersection for secondary rays

    # create a buffer to store the calculated intensities
    buf = np.ones(width*height*4)
    buf.shape = height,width,4

    # the location and orientation of the active camera
    origin = scene.camera.location
    rotation = scene.camera.rotation_euler

    aspectratio = height/width
    # loop over all pixels once (no multisampling)
    for y in range(height):
        yscreen = ((y-(height/2))/height) * aspectratio
        for x in range(width):
            xscreen = (x-(width/2))/width
            # align the look_at direction
            dir = Vector((xscreen, yscreen, -1))
            dir.rotate(rotation)
            
            # cast a ray into the scene
            hit, loc, normal, index, ob, mat = scene.ray_cast(origin, dir)
            
            # the default background is black for now
            color = np.zeros(3)
            if hit:
                # the get the diffuse color of the object we hit
                diffuse_color = Vector((0.8, 0.8, 0.8))
                mat_slots = ob.material_slots
                if len(mat_slots):
                    diffuse_color = mat_slots[0].material.diffuse_color
                        
                color = np.zeros(3)
                light = np.ones(3) * intensity  # light color is white
                for lamp in lamps:
                    # for every lamp determine the direction and distance
                    light_vec = lamp.location - loc
                    light_dist = light_vec.length_squared
                    light_dir = light_vec.normalized()
                    
                    # cast a ray in the direction of the light starting
                    # at the original hit location
                    lhit, lloc, lnormal, lindex, lob, lmat = scene.ray_cast(loc+light_dir*eps, light_dir)
                    
                    # if we hit something we are in the shadow of the light
                    if not lhit:
                        # otherwise we add the distance attenuated intensity
                        # we calculate diffuse reflectance with a pure 
                        # lambertian model
                        # https://en.wikipedia.org/wiki/Lambertian_reflectance
                        color += diffuse_color * intensity * normal.dot(light_dir)/light_dist
            buf[y,x,0:3] = color
    return buf

# straight from https://docs.blender.org/api/current/bpy.types.RenderEngine.html?highlight=renderengine
class CustomRenderEngine(bpy.types.RenderEngine):
    bl_idname = "ray_tracer"
    bl_label = "Ray Tracing Concepts Renderer"
    bl_use_preview = True

    def render(self, scene):
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)

        if self.is_preview:  # we might differentiate later
            pass             # for now ignore completely
        else:
            self.render_scene(scene)

    def render_scene(self, scene):
        buf = ray_trace(scene, self.size_x, self.size_y)
        buf.shape = -1,4

        # Here we write the pixel values to the RenderResult
        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]
        layer.rect = buf.tolist()
        self.end_result(result)



def register():
    bpy.utils.register_module(__name__)
    from bl_ui import (
            properties_render,
            properties_material,
            )
    properties_render.RENDER_PT_render.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_context_material.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_diffuse.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)

def unregister():
    bpy.utils.unregister_module(__name__)
    from bl_ui import (
            properties_render,
            properties_material,
            )
    properties_render.RENDER_PT_render.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_context_material.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_diffuse.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)

if __name__ == "__main__":
    register()
