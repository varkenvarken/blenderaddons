bl_info = {
    "name": "Prometheus",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 20230709105314),
    "blender": (3, 6, 0),
    "location": "",
    "description": "Expose metrics with the help of prometheus",
    "warning": "",
    "wiki_url": "https://github.com/varkenvarken/blenderaddons/blob/master/prometheus",
    "tracker_url": "",
    "category": "System",
}

import bpy  # type: ignore

from .prometheus_client import Gauge, start_http_server


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
    g = Gauge("Render2", "Rendering processes")
    start_http_server(8000)
    bpy.app.timers.register(every_10_seconds, persistent=True)
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    print("unregister")
    global g
    bpy.app.timers.unregister(every_10_seconds)
    prometheus_client.REGISTRY.unregister(g)
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
