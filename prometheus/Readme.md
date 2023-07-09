# A Prometheus add-on for Blender

Exposes [Prometheus](https://prometheus.io/) metrics on port 8000 when enabled.

In particular, it exposes a [Gauge](https://prometheus.io/docs/concepts/metric_types/#gauge), *Blender_Render*, that is 1 when the Blender instance is rendering, and 0 when it is not. The standard metrics, like cpu usage are also exposed.

## Building the add-on

Currently we use an embedded and slightly modified version of the [prometheus_client](https://github.com/prometheus/client_python/tree/master) for Python, which is in the [](prometheus_client/) subdirectory. That is not ideal and might change once I have figured out how to monkey path the server instead of hacking the source, but i don´t like to depend on external Python packages because that makes it difficult to distribute and add-on.
Copying is also very far from ideal, so a git sub-repository is probably the way to go.

```bash

git clone https://github.com/varkenvarken/blenderaddons.git
cd blenderaddons
zip -urv prometheus.zip prometheus
```

Then install `prometheus.zip` in the usual way and enable the add-on.

You can inspect the published metrics on http://localhost:8000.

Scraping this with a [Prometheus container](https://hub.docker.com/r/prom/prometheus) and creating a [Grafana](https://hub.docker.com/r/grafana/grafana) dashboard is something you'll have to figure out yourself.

## Source code

The code is extremely simple: when the add-on is enabled we create a Gauge metric and start the prometheus http server. We then register a [Blender timer](https://docs.blender.org/api/latest/bpy.app.timers.html#bpy.app.timers.register) that checks every 10 seconds if we are rendering or not with the [is_app_running()](https://docs.blender.org/api/latest/bpy.app.html#bpy.app.is_job_running) function and sets the Gauge accordingly.

The timer is made persistent, so it will keep running even if we load another .blend file.
The Prometheus server is running in a separate (daemon) thread and will only end if we exit Blender or if we invoke our custom `stop_http_server()` function, and that's where the ugly hack comes in: the `start_http-server()` function does not return the server it creates, so w e have no way to call its `shutdown()` function (which is present, because it is a subclass of [http.server](https://docs.python.org/3.11/library/http.server.html)) or call `close()` on the socket it is listening on, and this would prevent us from disabling and then enabling the add-on again, because we would get an address in use exception.

Same goes for the Gauge: If we want o be able to reenable the add-on we  have to make sure to remove it from the registry in the `unregister()` function.
```python
import bpy 
from .prometheus_client import Gauge, start_http_server, stop_http_server, REGISTRY

def every_10_seconds():
    global g
    r = bpy.app.is_job_running("RENDER")
    if r:
        g.set(1.0)
    else:
        g.set(0.0)
    return 10.0


def register():
    global g
    g = Gauge("Blender_Render", "Rendering processes")
    start_http_server(8000)
    bpy.app.timers.register(every_10_seconds, persistent=True)

def unregister():
    global g
    bpy.app.timers.unregister(every_10_seconds)
    REGISTRY.unregister(g)
    stop_http_server()
```