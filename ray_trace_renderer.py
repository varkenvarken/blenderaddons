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
    "version": (0, 0, 201806161245),
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
from math import acos, atan2, pi
from random import random, seed

def cosine_transform(scene):
    tex = scene.world.active_texture
    if tex:
        # scale image to a managable size
        img = tex.image.copy()
        img.scale(256,128)
        # get the pixels in an ordered array (works for any depth)
        p = np.array(img.pixels, dtype=np.float32)
        y,x = img.size[1],img.size[0]
        p.shape = y,x,-1
        
        # calculate the range of angles (inclination and azimuth)
        theta = (np.arange(y, dtype=np.float32)/(y-1) - 0.5)*np.pi
        phi = (np.arange(x, dtype=np.float32)/(x-1) - 0.5)*2*np.pi
        
        # allocate space for the convoluted colors
        c = np.zeros(p.shape, dtype=np.float32)
        
        # calculate the cartesian direction vectors (r = 1)
        d = np.empty((y,x,3), dtype=np.float32)
        costheta = np.cos(theta)
        sintheta = np.sin(theta)
        cosphi = np.cos(phi)
        sinphi = np.sin(phi)
        d[:,:,0] = np.outer(costheta, cosphi)
        d[:,:,1] = np.outer(costheta, sinphi)
        d[:,:,2] = np.outer(sintheta, np.ones(x, dtype=np.float32))

        # convert d to a single list of 3-vectors
        d.shape = -1,3
        # convert p to a single list of n-vectors
        p.shape = x*y,-1
        # for each direction, calculate the sum of dot products with all
        # other direction vectors.
        # This might be done in a more clever way
        w = np.einsum('ij,...j',d,d)
        # truncate negative dot product (i.e. backward pointing normals)
        w[w<0] = 0.0
        # for each direction calculate the weighted environment contribution
        print(d.shape, w.shape, p.shape)
        wc = np.dot(w,p) * (scene.world.light_settings.environment_energy / w.shape[0])
        # reshape the environment map
        wc.shape = y,x,-1
        return wc
    return None
        
X = Vector((1,0,0))
Y = Vector((0,1,0))
Z = Vector((0,0,1))

def vdc(n, base=2):
    vdc, denom = 0,1
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        vdc += remainder / denom
    return vdc

def single_ray(scene, origin, dir, lamps, depth, gi):
    eps = 1e-5      # small offset to prevent self intersection for secondary rays

    # cast a ray into the scene
    hit, loc, normal, index, ob, mat = scene.ray_cast(origin, dir)
    
    # the default background is black for now
    color = np.zeros(3)
    if hit:
        # get the diffuse and specular color and intensity of the object we hit
        diffuse_color = Vector((0.8, 0.8, 0.8))
        specular_color = Vector((0.2, 0.2, 0.2))
        mat_slots = ob.material_slots
        hardness = 0
        mirror_reflectivity = 0
        if len(mat_slots):
            mat = mat_slots[0].material
            diffuse_color = mat.diffuse_color * mat.diffuse_intensity
            specular_color = mat.specular_color * mat.specular_intensity
            hardness = mat.specular_hardness
            if mat.raytrace_mirror.use:
                mirror_reflectivity = mat.raytrace_mirror.reflect_factor

        color = np.zeros(3)
        for lamp in lamps:
            light = np.array(lamp.data.color * lamp.data.energy)
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
                illumination = light * normal.dot(light_dir)/light_dist
                color += np.array(diffuse_color) * illumination  # need cast: Color cannot be multiplies with an np.array
                if hardness > 0:  # phong reflection model
                    half = (light_dir - dir).normalized()
                    reflection = light * half.dot(normal) ** hardness
                    color += np.array(specular_color) * reflection

        # calculate reflections from the environment
        # for now we do not look at mat.raytrace_mirror.depth
        if depth > 0 and mirror_reflectivity > 0:
            # Rr = Ri - 2 N (Ri . N) see: http://paulbourke.net/geometry/reflected/
            reflection_dir = (dir - 2 * normal  * dir.dot(normal)).normalized()
            color += mirror_reflectivity * single_ray(scene, loc + normal*eps, reflection_dir, lamps, depth-1, gi)

        # calculate global illumination (ambient light)
        if gi is not None:
            theta = 1-acos(normal.z)/pi  # [-1,1] -> [pi,0] -> [1,0] 
            phi = ((-atan2(normal.y, normal.x)/pi) + 1)/2  # [pi,-pi] -> [-1,1] -> [0,2] ->[0,1]
            y = int(gi.shape[0] * theta)
            x = int(gi.shape[1] * phi)
            color += gi[y,x,:3]
                
    elif scene.world.active_texture:
        # intersect with an environment image
        # dir is normalized so the hypothenuse == length == 1
        # which means the z component == cos(angle)
        theta = 1-acos(dir.z)/pi  # [-1,1] -> [0,1] 
        phi = atan2(dir.y, dir.x)/pi
        color = np.array(scene.world.active_texture.evaluate((-phi,2*theta-1,0)).xyz)
    return color

def ray_trace(scene, width, height, depth, buf, samples, gi):     

    lamps = [ob for ob in scene.objects if ob.type == 'LAMP']

    lamp_intensity = 10  # intensity for all lamps

    # the location and orientation of the active camera
    origin = scene.camera.location
    rotation = scene.camera.rotation_euler

    sbuf = np.zeros(width*height*4)
    sbuf.shape = height,width,4

    aspectratio = height/width
    # loop over all pixels
    dy = aspectratio/height
    dx = 1/width
    seed(42)

    N = samples*width*height
    for s in range(samples):
        for y in range(height):
            yscreen = ((y-(height/2))/height) * aspectratio
            for x in range(width):
                xscreen = (x-(width/2))/width
                sumcolor = np.zeros(3, dtype=np.float32)
                # align the look_at direction after perturbing it a bit
                #dir = Vector((xscreen + dx*(random()-0.5), yscreen + dy*(random()-0.5), -1))
                dir = Vector((xscreen + dx*(vdc(s,2)-0.5), yscreen + dy*(vdc(s,3)-0.5), -1))
                dir.rotate(rotation)
                dir = dir.normalized()
                sbuf[y,x,0:3] += single_ray(scene, origin, dir, lamps, depth, gi)
            buf[y,:,0:3] = sbuf[y,:,0:3] / (s+1)
            if y < height-1:
                buf[y+1,:,0:3] = 1 - buf[y+1,:,0:3]
            yield (s*width*height+width*y)/N

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
        gi = None
        if scene.world.light_settings.use_environment_light:
            gi = cosine_transform(scene)
        # create a buffer to store the calculated intensities
        height, width = self.size_y, self.size_x
        buf = np.ones(width*height*4)
        buf.shape = height,width,4
        
        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]
        
        # note that anti_aliasing_samples is a string for no obvious reason
        samples = int(scene.render.antialiasing_samples) if scene.render.use_antialiasing else 1
        for p in ray_trace(scene, width, height, 1, buf, samples, gi):
            buf.shape = -1,4
            # Here we write the pixel values to the RenderResult
            layer.rect = buf.tolist()
            self.update_result(result)
            buf.shape = height,width,4
            self.update_progress(p)
            if self.test_break():
                break
        
        self.end_result(result)

from bpy.types import Panel
from bl_ui.properties_render import RenderButtonsPanel

class CUSTOM_RENDER_PT_antialiasing(RenderButtonsPanel, Panel):
    bl_label = "Anti-Aliasing"
    COMPAT_ENGINES = {CustomRenderEngine.bl_idname}

    def draw_header(self, context):
        rd = context.scene.render

        self.layout.prop(rd, "use_antialiasing", text="")

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render
        layout.active = rd.use_antialiasing

        split = layout.split()

        col = split.column()
        col.row().prop(rd, "antialiasing_samples", expand=True)
        
def register():
    bpy.utils.register_module(__name__)
    from bl_ui import (
            properties_render,
            properties_material,
            properties_data_lamp,
            properties_world,
            properties_texture,
            )
    properties_render.RENDER_PT_render.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_context_material.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_diffuse.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_specular.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_mirror.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_data_lamp.DATA_PT_lamp.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_world.WORLD_PT_context_world.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_world.WORLD_PT_environment_lighting.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_texture.TEXTURE_PT_context_texture.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_texture.TEXTURE_PT_preview.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_texture.TEXTURE_PT_image.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)
    properties_texture.TEXTURE_PT_mapping.COMPAT_ENGINES.add(CustomRenderEngine.bl_idname)

def unregister():
    bpy.utils.unregister_module(__name__)
    from bl_ui import (
            properties_render,
            properties_material,
            properties_data_lamp,
            properties_world,
            properties_texture,
            )
    properties_render.RENDER_PT_render.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_context_material.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_diffuse.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_specular.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_material.MATERIAL_PT_mirror.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_data_lamp.DATA_PT_lamp.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_world.WORLD_PT_context_world.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_world.WORLD_PT_environment_lighting.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_texture.TEXTURE_PT_context_texture.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_texture.TEXTURE_PT_preview.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_texture.TEXTURE_PT_image.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)
    properties_texture.TEXTURE_PT_mapping.COMPAT_ENGINES.remove(CustomRenderEngine.bl_idname)

if __name__ == "__main__":
    register()
