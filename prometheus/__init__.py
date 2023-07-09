# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Prometheus, a Blender addon
#  (c) 2023 Michel J. Anders (varkenvarken)
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

# Note: the prometheus_client subdirectory is part of
# https://github.com/prometheus/client_python/tree/master and covered by its own license.

bl_info = {
    "name": "Prometheus",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 20230709165251),
    "blender": (3, 6, 0),
    "location": "",
    "description": "Expose metrics with the help of prometheus",
    "warning": "",
    "wiki_url": "https://github.com/varkenvarken/blenderaddons/blob/master/prometheus",
    "tracker_url": "",
    "category": "System",
}

import bpy  # type: ignore

from .prometheus_client import Gauge, start_http_server, stop_http_server, REGISTRY

def every_10_seconds():
    global g
    r = bpy.app.is_job_running("RENDER")
    if r:
        g.set(1.0)
    else:
        g.set(0.0)
    print(f"rendering: {r}")
    return 10.0


classes = []


def register():
    print("register")
    global g
    g = Gauge("Blender_Render", "Rendering processes")
    start_http_server(8000)
    bpy.app.timers.register(every_10_seconds, persistent=True)
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    print("unregister")
    global g
    bpy.app.timers.unregister(every_10_seconds)
    REGISTRY.unregister(g)
    stop_http_server()
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
