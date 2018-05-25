#  trace.py (c) 2018 Michel Anders (varkenvarken)
#
#  A Blender script to illustrate ray tracing concepts
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

#  This script assumes the following
#  (a .blend file with a sample scene is provided as well: trace.blend)
#
#  - a scene with objects that are visible from a camera at (8,0,0) 
#                                           pointing in the -x direction
#  - one or more point lamps
#  - an 1024x1024 image with the name 'Test' (created with New in the 
#                               image with all defaults except the name)
  
import bpy
import numpy as np

scene = bpy.context.scene

lamps = [ob for ob in scene.objects if ob.type == 'LAMP']

intensity = 10  # intensity for all lamps
eps = 1e-5      # small offset to prevent self intersection for secondary rays

# this image must be created already and be 1024x1024 RGBA
output = bpy.data.images['Test']

# create a buffer to store the calculated intensities
buf = np.ones(1024*1024*4)
buf.shape = 1024,1024,4

# the location of our virtual camera (we do NOT use any camera that might be present)
origin = (8,0,0)

# loop over all pixels once (no multisampling)
for y in range(1024):
    for x in range(1024):
        # get the direction. camera points in -x direction, FOV = 90 degrees
        dir = (-1, (x-512)/1024, (y-512)/1024)
        
        # cast a ray into the scene
        hit, loc, normal, index, ob, mat = scene.ray_cast(origin, dir)
        
        # the default background is black for now
        color = np.zeros(3)
        if hit:
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
                    color += intensity * normal.dot(light_dir)/light_dist
        buf[y,x,0:3] = color

# pixels is a flat array RGBARGGBRGBA.... 
# assign to a single item inside pixels is prohibitively slow but
# assigning something that implements Python's buffer protocol is
# fast. So assiging a (flattened) 1024x1024x4 numpy array is fast
output.pixels = buf.flatten()
     
