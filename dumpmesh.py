# ##### BEGIN GPL LICENSE BLOCK #####
#
#  DumpMesh, a Blender addon
#  (c) 2016-2019 Michel J. Anders (varkenvarken)
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

bl_info = {
	"name": "DumpMesh",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 201909011717),
	"blender": (2, 80, 0),
	"location": "View3D > Object > DumpMesh",
	"description": "Dumps geometry information of active object in a text buffer",
	"warning": "",
	"wiki_url": "https://github.com/varkenvarken/blenderaddons/blob/master/dumpmesh.py",
	"tracker_url": "",
	"category": "Object"}

# to prevent problems with all sorts of quotes and stuff, the code that will be included in the final output is here base64 encoded
# you can find the readable version on https://github.com/varkenvarken/blenderaddons/blob/master/createmesh%20.py

GPLblurb = b'IyAjIyMjIyBCRUdJTiBHUEwgTElDRU5TRSBCTE9DSyAjIyMjIwojCiMgIENyZWF0ZU1lc2gsIGEgQmxlbmRlciBhZGRvbgojICAoYykgMjAxNi0yMDE5IE1pY2hlbCBKLiBBbmRlcnMgKHZhcmtlbnZhcmtlbikKIwojICBUaGlzIHByb2dyYW0gaXMgZnJlZSBzb2Z0d2FyZTsgeW91IGNhbiByZWRpc3RyaWJ1dGUgaXQgYW5kL29yCiMgIG1vZGlmeSBpdCB1bmRlciB0aGUgdGVybXMgb2YgdGhlIEdOVSBHZW5lcmFsIFB1YmxpYyBMaWNlbnNlCiMgIGFzIHB1Ymxpc2hlZCBieSB0aGUgRnJlZSBTb2Z0d2FyZSBGb3VuZGF0aW9uOyBlaXRoZXIgdmVyc2lvbiAyCiMgIG9mIHRoZSBMaWNlbnNlLCBvciAoYXQgeW91ciBvcHRpb24pIGFueSBsYXRlciB2ZXJzaW9uLgojCiMgIFRoaXMgcHJvZ3JhbSBpcyBkaXN0cmlidXRlZCBpbiB0aGUgaG9wZSB0aGF0IGl0IHdpbGwgYmUgdXNlZnVsLAojICBidXQgV0lUSE9VVCBBTlkgV0FSUkFOVFk7IHdpdGhvdXQgZXZlbiB0aGUgaW1wbGllZCB3YXJyYW50eSBvZgojICBNRVJDSEFOVEFCSUxJVFkgb3IgRklUTkVTUyBGT1IgQSBQQVJUSUNVTEFSIFBVUlBPU0UuICBTZWUgdGhlCiMgIEdOVSBHZW5lcmFsIFB1YmxpYyBMaWNlbnNlIGZvciBtb3JlIGRldGFpbHMuCiMKIyAgWW91IHNob3VsZCBoYXZlIHJlY2VpdmVkIGEgY29weSBvZiB0aGUgR05VIEdlbmVyYWwgUHVibGljIExpY2Vuc2UKIyAgYWxvbmcgd2l0aCB0aGlzIHByb2dyYW07IGlmIG5vdCwgd3JpdGUgdG8gdGhlIEZyZWUgU29mdHdhcmUgRm91bmRhdGlvbiwKIyAgSW5jLiwgNTEgRnJhbmtsaW4gU3RyZWV0LCBGaWZ0aCBGbG9vciwgQm9zdG9uLCBNQSAwMjExMC0xMzAxLCBVU0EuCiMKIyAjIyMjIyBFTkQgR1BMIExJQ0VOU0UgQkxPQ0sgIyMjIyMK'

BaseClass = b'YmxfaW5mbyA9IHsKCSJuYW1lIjogIkNyZWF0ZU1lc2giLAoJImF1dGhvciI6ICJNaWNoZWwgQW5kZXJzICh2YXJrZW52YXJrZW4pIiwKCSJ2ZXJzaW9uIjogKDAsIDAsIDIwMTkwOTAxMTcyMCksCgkiYmxlbmRlciI6ICgyLCA4MCwgMCksCgkibG9jYXRpb24iOiAiVmlldzNEID4gT2JqZWN0ID4gQWRkIE1lc2ggPiBEdW1wZWRNZXNoIiwKCSJkZXNjcmlwdGlvbiI6ICJBZGRzIGEgbWVzaCBvYmplY3QgdG8gdGhlIHNjZW5lIHRoYXQgd2FzIGNyZWF0ZWQgd2l0aCB0aGUgRHVtcE1lc2ggYWRkb24iLAoJIndhcm5pbmciOiAiIiwKCSJ3aWtpX3VybCI6ICJodHRwczovL2dpdGh1Yi5jb20vdmFya2VudmFya2VuL2JsZW5kZXJhZGRvbnMvYmxvYi9tYXN0ZXIvY3JlYXRlbWVzaCUyMC5weSIsCgkidHJhY2tlcl91cmwiOiAiIiwKCSJjYXRlZ29yeSI6ICJBZGQgTWVzaCJ9CgppbXBvcnQgYnB5CmltcG9ydCBibWVzaAoKY2xhc3MgRHVtcE1lc2g6CgoJIyBtb3N0IGVsZW1lbnRzIGluIGFuIGF0dHJpYnV0ZSBsYXllciBjYW4gYmUgYXNzaWduZWQgdG8gZGlyZWN0bHkKCSMgaWYgdGhleSBhcmUgZmxvYXRzIGFuZCBpZiB0aGV5IGFyZSBWZWN0b3JzIChvciBDb2xvcnMpIHRoZXkgY2FuCgkjIGJlIGFzc2lnbmVkIGEgdHVwbGUgd2l0aG91dCBwcm9ibGVtcy4gSG93ZXZlciwgc29tZSBzcGVjaWZpYyB0eXBlcwoJIyBuZWVkIHRoZSB2YWx1ZSB0byBiZSBhc3NpZ25lZCB0byBhIHNwZWNpZmljIGF0dHJpYnV0ZSBhbmQgZm9yCgkjIHRob3NlIHdlIGhhdmUgYSBtYXBwaW5nIGhlcmUuIEJNVGV4UG9seSBkb2VzIG5vdCBiZWhhdmUgYW5kIGlzIG5vdAoJIyBkb2N1bWVudGVkIHdlbGwgKEJsZW5kZXIgMi43Nikgc28gd2UgaWdub3JlIGl0LiAKCWF0dHJpYnV0ZW1hcHBpbmcgPSBkaWN0KEJNTG9vcFVWPWxhbWJkYSBvYix2OiBzZXRhdHRyKG9iLCd1dicsdiksCgkJCQkJCQlCTVZlcnRTa2luPWxhbWJkYSBvYix2OiBzZXRhdHRyKG9iLCdyYWRpdXMnLHYpLAoJCQkJCQkJQk1UZXhQb2x5PWxhbWJkYSBvYix2OiBOb25lKQoKCWRlZiB2YWxtYXAoc2VsZiwgc2FtcGxlKToKCQluYW1lID0gc2FtcGxlLl9fY2xhc3NfXy5fX25hbWVfXwoJCWlmIG5hbWUgaW4gc2VsZi5hdHRyaWJ1dGVtYXBwaW5nOgoJCQlyZXR1cm4gc2VsZi5hdHRyaWJ1dGVtYXBwaW5nW25hbWVdCgkJcmV0dXJuIE5vbmUKCglkZWYgZ2VvbWV0cnkoc2VsZik6CgoJCWJtID0gYm1lc2gubmV3KCkKCgkJdmVydHMgPSBzZWxmLl9fY2xhc3NfXy52ZXJ0cwoJCWVkZ2VzID0gc2VsZi5fX2NsYXNzX18uZWRnZXMKCQlmYWNlcyA9IHNlbGYuX19jbGFzc19fLmZhY2VzCgkJCgkJZm9yIG4sdiBpbiBlbnVtZXJhdGUodmVydHMpOgoJCQlibS52ZXJ0cy5uZXcodikKCQlibS52ZXJ0cy5lbnN1cmVfbG9va3VwX3RhYmxlKCkgICMgZW5zdXJlcyBibS52ZXJ0cyBjYW4gYmUgaW5kZXhlZAoJCWJtLnZlcnRzLmluZGV4X3VwZGF0ZSgpICAgICAgICAgIyBlbnN1cmVzIGFsbCBibS52ZXJ0cyBoYXZlIGFuIGluZGV4ICg9IGRpZmZlcmVudCB0aGluZyEpCgkJaWYgaGFzYXR0cihzZWxmLl9fY2xhc3NfXywndmVydF9hdHRyaWJ1dGVzJyk6CgkJCWZvciBhdHRyLCB2YWx1ZXMgaW4gc2VsZi5fX2NsYXNzX18udmVydF9hdHRyaWJ1dGVzLml0ZW1zKCk6CgkJCQlmb3Igdix2YWwgaW4gemlwKGJtLnZlcnRzLCB2YWx1ZXMpOgoJCQkJCXNldGF0dHIodixhdHRyLHZhbCkKCgkJZm9yIG4sZSBpbiBlbnVtZXJhdGUoZWRnZXMpOgoJCQllZGdlID0gYm0uZWRnZXMubmV3KGJtLnZlcnRzW3ZdIGZvciB2IGluIGUpCgkJYm0uZWRnZXMuZW5zdXJlX2xvb2t1cF90YWJsZSgpCgkJYm0uZWRnZXMuaW5kZXhfdXBkYXRlKCkKCQlpZiBoYXNhdHRyKHNlbGYuX19jbGFzc19fLCdlZGdlX2F0dHJpYnV0ZXMnKToKCQkJZm9yIGF0dHIsIHZhbHVlcyBpbiBzZWxmLl9fY2xhc3NfXy5lZGdlX2F0dHJpYnV0ZXMuaXRlbXMoKToKCQkJCWZvciBlLHZhbCBpbiB6aXAoYm0uZWRnZXMsIHZhbHVlcyk6CgkJCQkJc2V0YXR0cihlLGF0dHIsdmFsKQoKCQlmb3IgbixmIGluIGVudW1lcmF0ZShmYWNlcyk6CgkJCWJtLmZhY2VzLm5ldyhibS52ZXJ0c1t2XSBmb3IgdiBpbiBmKQoJCWJtLmZhY2VzLmVuc3VyZV9sb29rdXBfdGFibGUoKQoJCWJtLmZhY2VzLmluZGV4X3VwZGF0ZSgpCgkJaWYgaGFzYXR0cihzZWxmLl9fY2xhc3NfXywnZmFjZV9hdHRyaWJ1dGVzJyk6CgkJCWZvciBhdHRyLCB2YWx1ZXMgaW4gc2VsZi5fX2NsYXNzX18uZmFjZV9hdHRyaWJ1dGVzLml0ZW1zKCk6CgkJCQlmb3IgZix2YWwgaW4gemlwKGJtLmZhY2VzLCB2YWx1ZXMpOgoJCQkJCXNldGF0dHIoZixhdHRyLHZhbCkKCgkJZm9yIGV0eXBlIGluICgndmVydHMnLCAnZWRnZXMnLCAnZmFjZXMnKToKCQkJc2VxID0gZ2V0YXR0cihibSwgZXR5cGUpCgkJCWJtbGF5ZXJzID0gc2VxLmxheWVycwoJCQlpZiBoYXNhdHRyKHNlbGYuX19jbGFzc19fLCBldHlwZSArICdfbGF5ZXJzJyk6CgkJCQlmb3IgbGF5ZXJ0eXBlLCBsYXllcnMgaW4gZ2V0YXR0cihzZWxmLl9fY2xhc3NfXywgZXR5cGUgKyAnX2xheWVycycpLml0ZW1zKCk6CgkJCQkJYm1sYXllcnR5cGUgPSBnZXRhdHRyKGJtbGF5ZXJzLCBsYXllcnR5cGUpCgkJCQkJZm9yIGxheWVybmFtZSwgdmFsdWVzIGluIGxheWVycy5pdGVtcygpOgoJCQkJCQlibWxheWVyID0gYm1sYXllcnR5cGUubmV3KGxheWVybmFtZSkgIyBmcmVzaCBvYmplY3Qgc28gd2UgZG9uJ3QgY2hlY2sgaWYgdGhlIGxheWVyIGFscmVhZHkgZXhpc3RzCgkJCQkJCXZhbG1hcCA9IHNlbGYudmFsbWFwKHNlcVswXVtibWxheWVyXSkKCQkJCQkJZm9yIG4sIGVsZSBpbiBlbnVtZXJhdGUoc2VxKToKCQkJCQkJCWlmIHZhbG1hcCBpcyBOb25lOgoJCQkJCQkJCWVsZVtibWxheWVyXSA9IHZhbHVlc1tuXQoJCQkJCQkJZWxzZToKCQkJCQkJCQl2YWxtYXAoZWxlW2JtbGF5ZXJdLHZhbHVlc1tuXSkKCgkJYm1sYXllcnMgPSBibS5sb29wcy5sYXllcnMKCQlpZiBoYXNhdHRyKHNlbGYuX19jbGFzc19fLCAnbG9vcHNfbGF5ZXJzJyk6CgkJCWZvciBsYXllcnR5cGUsIGxheWVycyBpbiBnZXRhdHRyKHNlbGYuX19jbGFzc19fLCAnbG9vcHNfbGF5ZXJzJykuaXRlbXMoKToKCQkJCWJtbGF5ZXJ0eXBlID0gZ2V0YXR0cihibWxheWVycywgbGF5ZXJ0eXBlKQoJCQkJYXR0cm5hbWUgPSBzZWxmLl9fY2xhc3NfXy5hdHRyaWJ1dGVtYXBwaW5nW2xheWVydHlwZV0gaWYgbGF5ZXJ0eXBlIGluIHNlbGYuX19jbGFzc19fLmF0dHJpYnV0ZW1hcHBpbmcgZWxzZSBOb25lCgkJCQlmb3IgbGF5ZXJuYW1lLCB2YWx1ZXMgaW4gbGF5ZXJzLml0ZW1zKCk6CgkJCQkJYm1sYXllciA9IGJtbGF5ZXJ0eXBlLm5ldyhsYXllcm5hbWUpICMgZnJlc2ggb2JqZWN0IHNvIHdlIGRvbid0IGNoZWNrIGlmIHRoZSBsYXllciBhbHJlYWR5IGV4aXN0cwoJCQkJCSMgd2UgYXNzdW1lIGFsbCBsb29wcyB3aWxsIGJlIG51bWJlcmVkIGluIGFzY2VuZGluZyBvcmRlcgoJCQkJCSMgYm0uZmFjZXNbaV0ubG9vcHMuaW5kZXhfdXBkYXRlKCkgaXMgb2Ygbm8gdXNlLCBzaW5jZSBpdAoJCQkJCSMgc3RhcnQgbnVtYmVyaW5nIGFnYWluIGF0IDAgZm9yIHRoaXMgc2V0IG9mIGxvb3BzLCBzbyB0aGVyZQoJCQkJCSMgaXMgbm8gd2F5IHRvIHVwZGF0ZSB0aGUgaW5kaWNlcyBvZiBhbGwgbG9vcCBpbiBpbiBnbywKCQkJCQkjIGV4Y2VwdCBieSBjb252ZXJ0aW5nIHRoZSBibSB0byBhIHJlZ3VsYXIgbWVzaCwgaW4gd2hpY2gKCQkJCQkjIGNhc2UgaXQgaGFwcGVucyBhdXRvbWFnaWNhbGx5LgoJCQkJCWxvb3BpbmRleCA9IDAKCQkJCQlmb3IgZmFjZSBpbiBibS5mYWNlczoKCQkJCQkJZm9yIGxvb3AgaW4gZmFjZS5sb29wczoKCQkJCQkJCXZhbCA9IHZhbHVlc1tmYWNlLmluZGV4XVtsb29waW5kZXhdCgkJCQkJCQl2YWxtYXAgPSBzZWxmLnZhbG1hcChsb29wW2JtbGF5ZXJdKQoJCQkJCQkJaWYgdmFsbWFwIGlzIE5vbmU6CgkJCQkJCQkJbG9vcFtibWxheWVyXSA9IHZhbAoJCQkJCQkJZWxzZToKCQkJCQkJCQl2YWxtYXAobG9vcFtibWxheWVyXSx2YWwpCgkJCQkJCQlsb29waW5kZXggKz0gMQoKCQlyZXR1cm4gYm0KCgkjIGJtZXNoLnR5cGVzLkJNZXNoIGNhbm5vdCBiZSBzdWJjbGFzc2VkLCBidXQgdGhpcyB3YXkgd2UgY2FuIGFsbW9zdAoJIyBsZXQgRHVtcE1lc2ggZGVyaXZlZCBjbGFzc2VzIGJlaGF2ZSBsaWtlIGEgY2xhc3MgZmFjdG9yeSB3aG9zZQoJIyBpbnN0YW5jZXMgcmV0dXJuIGEgQk1lc2gKCglkZWYgX19jYWxsX18oc2VsZik6CgkJcmV0dXJuIHNlbGYuZ2VvbWV0cnkoKQoKY2xhc3MgQ3ViZShEdW1wTWVzaCk6Cgl2ZXJ0cyA9IFsoLTEsLTEsLTEpLCgtMSwtMSwxKSwoLTEsMSwtMSksKC0xLDEsMSksKDEsLTEsLTEpLCgxLC0xLDEpLCgxLDEsLTEpLCgxLDEsMSksXQoKCWVkZ2VzID0gWygwLCAxKSwoMSwgMyksKDMsIDIpLCgyLCAwKSwoMywgNyksKDcsIDYpLCg2LCAyKSwoNywgNSksKDUsIDQpLCg0LCA2KSwoNSwgMSksKDAsIDQpLF0KCglmYWNlcyA9IFsoMSwgMywgMiwgMCksKDMsIDcsIDYsIDIpLCg3LCA1LCA0LCA2KSwoNSwgMSwgMCwgNCksKDAsIDIsIDYsIDQpLCg1LCA3LCAzLCAxKSxdCgoJdmVydHNfbGF5ZXJzID0geydiZXZlbF93ZWlnaHQnOiB7fSwgJ2RlZm9ybSc6IHt9LCAnZmxvYXQnOiB7fSwgJ2ludCc6IHt9LCAncGFpbnRfbWFzayc6IHt9LCAnc2hhcGUnOiB7fSwgJ3NraW4nOiB7Jyc6IHswOigwLjI1LCAwLjI1KSwxOigwLjI1LCAwLjI1KSwyOigwLjI1LCAwLjI1KSwzOigwLjI1LCAwLjI1KSw0OigwLjI1LCAwLjI1KSw1OigwLjI1LCAwLjI1KSw2OigwLjI1LCAwLjI1KSw3OigwLjI1LCAwLjI1KSx9LCB9LCAnc3RyaW5nJzoge30sIAl9CgoJZWRnZXNfbGF5ZXJzID0geydiZXZlbF93ZWlnaHQnOiB7fSwgJ2NyZWFzZSc6IHsnU3ViU3VyZkNyZWFzZSc6IHswOjAuMCwxOjAuMCwyOjAuMCwzOjAuMCw0OjAuMCw1OjEuMCw2OjAuMCw3OjEuMCw4OjEuMCw5OjEuMCwxMDowLjAsMTE6MC4wLH0sIH0sICdmbG9hdCc6IHt9LCAnZnJlZXN0eWxlJzoge30sICdpbnQnOiB7fSwgJ3N0cmluZyc6IHt9LCAJfQoKCWZhY2VzX2xheWVycyA9IHsnZmxvYXQnOiB7fSwgJ2ZyZWVzdHlsZSc6IHt9LCAnaW50Jzoge30sICdzdHJpbmcnOiB7fSwgJ3RleCc6IHsnVVZNYXAnOiB7MDpOb25lLDE6Tm9uZSwyOk5vbmUsMzpOb25lLDQ6Tm9uZSw1Ok5vbmUsfSwgfSwgCX0KCglsb29wc19sYXllcnMgPSB7J2NvbG9yJzogeydDb2wnOiB7MDogezA6KDEuMCwgMS4wLCAxLjApLDE6KDEuMCwgMS4wLCAxLjApLDI6KDEuMCwgMS4wLCAxLjApLDM6KDEuMCwgMS4wLCAxLjApLH0sMTogezQ6KDEuMCwgMS4wLCAxLjApLDU6KDEuMCwgMS4wLCAxLjApLDY6KDEuMCwgMS4wLCAxLjApLDc6KDEuMCwgMS4wLCAxLjApLH0sMjogezg6KDEuMCwgMS4wLCAxLjApLDk6KDEuMCwgMS4wLCAxLjApLDEwOigxLjAsIDEuMCwgMS4wKSwxMTooMS4wLCAxLjAsIDEuMCksfSwzOiB7MTI6KDEuMCwgMC4xNTI5NDExODIyNTU3NDQ5MywgMC4xNDkwMTk2MTM4NjIwMzc2NiksMTM6KDEuMCwgMC4wMDc4NDMxMzc3MTg3MzcxMjUsIDAuMCksMTQ6KDEuMCwgMC4wMDc4NDMxMzc3MTg3MzcxMjUsIDAuMCksMTU6KDEuMCwgMC4wMDc4NDMxMzc3MTg3MzcxMjUsIDAuMCksfSw0OiB7MTY6KDEuMCwgMS4wLCAxLjApLDE3OigxLjAsIDEuMCwgMS4wKSwxODooMS4wLCAxLjAsIDEuMCksMTk6KDEuMCwgMS4wLCAxLjApLH0sNTogezIwOigxLjAsIDEuMCwgMS4wKSwyMTooMS4wLCAxLjAsIDEuMCksMjI6KDEuMCwgMS4wLCAxLjApLDIzOigxLjAsIDEuMCwgMS4wKSx9LH0sfSwnZmxvYXQnOiB7fSwnaW50Jzoge30sJ3N0cmluZyc6IHt9LCd1dic6IHsnVVZNYXAnOiB7MDogezA6KDAuMzMzMzMzNDYyNDc2NzMwMzUsIDAuNjY2NjY2NjI2OTMwMjM2OCksMTooMC4zMzMzMzM0MDI4NzIwODU1NywgMC4zMzMzMzMzNzMwNjk3NjMyKSwyOigwLjY2NjY2NjY4NjUzNDg4MTYsIDAuMzMzMzMzMzQzMjY3NDQwOCksMzooMC42NjY2NjY3NDYxMzk1MjY0LCAwLjY2NjY2NjYyNjkzMDIzNjgpLH0sMTogezQ6KDMuOTczNjQyMDM3NjM1NzI3ZS0wOCwgMC42NjY2NjY2ODY1MzQ4ODE2KSw1OigwLjAsIDAuMzMzMzMzNDAyODcyMDg1NTcpLDY6KDAuMzMzMzMzMjgzNjYyNzk2LCAwLjMzMzMzMzM0MzI2NzQ0MDgpLDc6KDAuMzMzMzMzMzQzMjY3NDQwOCwgMC42NjY2NjY2MjY5MzAyMzY4KSx9LDI6IHs4OigxLjI5MTQzMzczMzI4NTg4NWUtMDcsIDAuMzMzMzMzMzQzMjY3NDQwOCksOTooMC4wLCA4Ljk0MDY5Mzg3NDEzNzY1MWUtMDgpLDEwOigwLjMzMzMzMzMxMzQ2NTExODQsIDAuMCksMTE6KDAuMzMzMzMzNDAyODcyMDg1NTcsIDAuMzMzMzMzMjUzODYwNDczNjMpLH0sMzogezEyOigwLjMzMzMzMzQwMjg3MjA4NTU3LCAzLjk3MzY0MTY4MjM2NDM1OTRlLTA4KSwxMzooMC42NjY2NjY2ODY1MzQ4ODE2LCAwLjApLDE0OigwLjY2NjY2Njc0NjEzOTUyNjQsIDAuMzMzMzMzMjUzODYwNDczNjMpLDE1OigwLjMzMzMzMzQ2MjQ3NjczMDM1LCAwLjMzMzMzMzMxMzQ2NTExODQpLH0sNDogezE2OigxLjAsIDAuMCksMTc6KDEuMCwgMC4zMzMzMzMyMjQwNTgxNTEyNSksMTg6KDAuNjY2NjY2NzQ2MTM5NTI2NCwgMC4zMzMzMzMyMjQwNTgxNTEyNSksMTk6KDAuNjY2NjY2NzQ2MTM5NTI2NCwgMi45ODAyMzEzNTA1OTExMTE1ZS0wOCksfSw1OiB7MjA6KDAuMCwgMC42NjY2NjY3NDYxMzk1MjY0KSwyMTooMC4zMzMzMzMyNTM4NjA0NzM2MywgMC42NjY2NjY2ODY1MzQ4ODE2KSwyMjooMC4zMzMzMzMyODM2NjI3OTYsIDAuOTk5OTk5OTQwMzk1MzU1MiksMjM6KDQuOTY3MDUyNTQ3MDQ0NjU5ZS0wOCwgMC45OTk5OTk5NDAzOTUzNTUyKSx9LH0sfSwJfQoKCXZlcnRfYXR0cmlidXRlcyA9IHsKCSdub3JtYWwnIDogWygtMC41NzczNDkxODU5NDM2MDM1LCAtMC41NzczNDkxODU5NDM2MDM1LCAtMC41NzczNDkxODU5NDM2MDM1KSwgKC0wLjU3NzM0OTE4NTk0MzYwMzUsIC0wLjU3NzM0OTE4NTk0MzYwMzUsIDAuNTc3MzQ5MTg1OTQzNjAzNSksICgtMC41NzczNDkxODU5NDM2MDM1LCAwLjU3NzM0OTE4NTk0MzYwMzUsIC0wLjU3NzM0OTE4NTk0MzYwMzUpLCAoLTAuNTc3MzQ5MTg1OTQzNjAzNSwgMC41NzczNDkxODU5NDM2MDM1LCAwLjU3NzM0OTE4NTk0MzYwMzUpLCAoMC41NzczNDkxODU5NDM2MDM1LCAtMC41NzczNDkxODU5NDM2MDM1LCAtMC41NzczNDkxODU5NDM2MDM1KSwgKDAuNTc3MzQ5MTg1OTQzNjAzNSwgLTAuNTc3MzQ5MTg1OTQzNjAzNSwgMC41NzczNDkxODU5NDM2MDM1KSwgKDAuNTc3MzQ5MTg1OTQzNjAzNSwgMC41NzczNDkxODU5NDM2MDM1LCAtMC41NzczNDkxODU5NDM2MDM1KSwgKDAuNTc3MzQ5MTg1OTQzNjAzNSwgMC41NzczNDkxODU5NDM2MDM1LCAwLjU3NzM0OTE4NTk0MzYwMzUpXSwKCSdzZWxlY3QnIDogW0ZhbHNlLCBUcnVlLCBGYWxzZSwgVHJ1ZSwgRmFsc2UsIFRydWUsIEZhbHNlLCBUcnVlXSwKCX0KCgllZGdlX2F0dHJpYnV0ZXMgPSB7Cgknc2VhbScgOiBbRmFsc2UsIEZhbHNlLCBGYWxzZSwgRmFsc2UsIEZhbHNlLCBGYWxzZSwgRmFsc2UsIEZhbHNlLCBGYWxzZSwgRmFsc2UsIEZhbHNlLCBGYWxzZV0sCgknc21vb3RoJyA6IFtUcnVlLCBUcnVlLCBUcnVlLCBUcnVlLCBUcnVlLCBUcnVlLCBUcnVlLCBUcnVlLCBUcnVlLCBUcnVlLCBUcnVlLCBUcnVlXSwKCSdzZWxlY3QnIDogW0ZhbHNlLCBUcnVlLCBGYWxzZSwgRmFsc2UsIFRydWUsIEZhbHNlLCBGYWxzZSwgVHJ1ZSwgRmFsc2UsIEZhbHNlLCBUcnVlLCBGYWxzZV0sCgl9CgoJZmFjZV9hdHRyaWJ1dGVzID0gewoJJ25vcm1hbCcgOiBbKC0xLjAsIDAuMCwgMC4wKSwgKDAuMCwgMS4wLCAtMC4wKSwgKDEuMCwgMC4wLCAtMC4wKSwgKDAuMCwgLTEuMCwgMC4wKSwgKC0wLjAsIDAuMCwgLTEuMCksICgtMC4wLCAwLjAsIDEuMCldLAoJJ3Ntb290aCcgOiBbRmFsc2UsIEZhbHNlLCBGYWxzZSwgRmFsc2UsIEZhbHNlLCBGYWxzZV0sCgknc2VsZWN0JyA6IFtGYWxzZSwgRmFsc2UsIEZhbHNlLCBGYWxzZSwgRmFsc2UsIFRydWVdLAoJfQoK'

OperatorDef = b'ZnJvbSBicHlfZXh0cmFzLm9iamVjdF91dGlscyBpbXBvcnQgb2JqZWN0X2RhdGFfYWRkCgpjbGFzcyBDcmVhdGVNZXNoKGJweS50eXBlcy5PcGVyYXRvcik6CgkiIiJBZGQgbWVzaCBvYmplY3RzIHRvIHRoZSBzY2VuZSIiIgoJYmxfaWRuYW1lID0gIm1lc2guY3JlYXRlbWVzaCIKCWJsX2xhYmVsID0gIkNyZWF0ZU1lc2giCglibF9vcHRpb25zID0geydSRUdJU1RFUicsICdVTkRPJ30KCglAY2xhc3NtZXRob2QKCWRlZiBwb2xsKGNscywgY29udGV4dCk6CgkJcmV0dXJuIGNvbnRleHQubW9kZSA9PSAnT0JKRUNUJwoKCWRlZiBleGVjdXRlKHNlbGYsIGNvbnRleHQpOgoJCWZvciBtZXNoIGluIG1lc2hlczoKCQkJbWVzaGZhY3RvcnkgPSBtZXNoKCkKCgkJCW1lID0gYnB5LmRhdGEubWVzaGVzLm5ldyhuYW1lPW1lc2hmYWN0b3J5Ll9fY2xhc3NfXy5fX25hbWVfXykKCQkJb2IgPSBvYmplY3RfZGF0YV9hZGQoY29udGV4dCwgbWUpCgkJCWJtID0gbWVzaGZhY3RvcnkoKQoKCQkJIyB3cml0ZSB0aGUgYm1lc2ggdG8gdGhlIG1lc2gKCQkJYm0udG9fbWVzaChtZSkKCQkJbWUudXBkYXRlKCkKCQkJYm0uZnJlZSgpCgoJCQkjIGFzc29jaWF0ZSB0aGUgbWVzaCB3aXRoIHRoZSBvYmplY3QKCQkJb2IuZGF0YSA9IG1lCgoJCQljb250ZXh0LnZpZXdfbGF5ZXIub2JqZWN0cy5hY3RpdmUgPSBvYgoJCQlvYi5zZWxlY3Rfc2V0KFRydWUpCgoJCXJldHVybiB7J0ZJTklTSEVEJ30KCmRlZiByZWdpc3RlcigpOgoJYnB5LnV0aWxzLnJlZ2lzdGVyX2NsYXNzKENyZWF0ZU1lc2gpCglicHkudHlwZXMuVklFVzNEX01UX2FkZC5hcHBlbmQobWVudV9mdW5jKQoKZGVmIHVucmVnaXN0ZXIoKToKCWJweS51dGlscy51bnJlZ2lzdGVyX21vZHVsZShDcmVhdGVNZXNoKQoJYnB5LnR5cGVzLlZJRVczRF9NVF9hZGQucmVtb3ZlKG1lbnVfZnVuYykKCmRlZiBtZW51X2Z1bmMoc2VsZiwgY29udGV4dCk6CglzZWxmLmxheW91dC5vcGVyYXRvcihDcmVhdGVNZXNoLmJsX2lkbmFtZSwgaWNvbj0nUExVR0lOJykKCmlmIF9fbmFtZV9fID09ICJfX21haW5fXyI6CglyZWdpc3RlcigpCg=='


import bpy
import bmesh
from bpy.props import BoolProperty, StringProperty, IntProperty
from base64 import standard_b64decode as b64decode

class DumpMesh(bpy.types.Operator):
	"""Dumps mesh geometry information to a text buffer"""
	bl_idname = "object.dumpmesh"
	bl_label = "DumpMesh"
	bl_options = {'REGISTER','UNDO'}

	include_operator : BoolProperty(name="Add operator", 
							description="Add operator definition",
							default=True)

	compact : BoolProperty(name="Compact",
							description="Omit newlines and other whitespace",
							default=True)

	geomonly : BoolProperty(name="Geometry only",
							description="Omit everything other than verts, edges and faces",
							default=False)

	digits : IntProperty(name="Digits",
							description="Number of decimal places in vertex coordinates",
							default=4,
							min=1, max=9)

	def format_vertex(self, v):
		return ("({co[0]:.%dg},{co[1]:.%dg},{co[2]:.%dg})"%(self.digits,self.digits,self.digits)).format(co=v)

	def tuple_or_orig(self, v):
		if type(v) == str :
			return v
		elif type(v) == bmesh.types.BMLoopUV:
			return tuple(v.uv)
		# elif type(v) == bmesh.types.BMTexPoly: # this types is not yet defined
		#	return None # has .image attribute but not sure what it is for
		# skin and deform values also lack an entry in bmesh.types, we ignore anything else
		elif v.__class__.__name__.startswith("BMVertSkin"):
			return tuple(v.radius)
		elif v.__class__.__name__.startswith("BM"):
			return None
		elif hasattr(v, '__iter__') or hasattr(v, '__len__'):
			return tuple(v)
		return v

	@classmethod
	def poll(cls, context):
		return (( context.active_object is not None ) 
			and (type(context.active_object.data) == bpy.types.Mesh))

	def execute(self, context):

		output = bpy.data.texts.new("mesh_data.py")

		if self.include_operator:
			output.write(b64decode(GPLblurb).decode() + '\n')
			output.write(b64decode(BaseClass).decode() + '\n')

		names = []

		for ob in context.selected_objects:
			me = ob.data
			bm = bmesh.new()
			bm.from_mesh(me)

			name = ob.name.replace(".","_").replace(" ","_")
			names.append(name)

			bm.verts.ensure_lookup_table()
			bm.edges.ensure_lookup_table()
			bm.faces.ensure_lookup_table()

			nl = "" if self.compact else "\n"
			tb = "" if self.compact else "\t"

			output.write("class " + name + "(DumpMesh):\n" + nl)

			output.write("\tverts = [" + nl)
			for v in bm.verts:
				output.write(tb + tb + self.format_vertex(v.co) + "," + nl)
			output.write(tb + "]\n\n")

			output.write("\tedges = [" + nl)
			for e in bm.edges:
				output.write(tb + tb + str(tuple(v.index for v in e.verts)) + "," + nl)
			output.write(tb + "]\n\n")

			output.write("\tfaces = [" + nl)
			for f in bm.faces:
				output.write(tb + tb + str(tuple(v.index for v in f.verts)) + "," + nl)
			output.write(tb + "]\n\n")

			if not self.geomonly:
				for etype in ('verts', 'edges', 'faces'):
					output.write("\t%s_layers = {"%etype + nl)
					seq = getattr(bm, etype)
					for attr in dir(seq.layers):
						attrval = getattr(seq.layers,attr)
						if type(attrval) == bmesh.types.BMLayerCollection:
							output.write(tb + tb + "'"+attr+"': {" + nl)
							for key, val in attrval.items():
								output.write(tb + tb + tb + "'" + key + "': {" + nl)
								for v in seq:
									output.write(tb + tb + tb + str(v.index) + ":" + str(self.tuple_or_orig(v[val])) + "," + nl)
								output.write(tb + tb + tb + "}, " + nl)
							output.write(tb + tb + "}, " + nl)
					output.write("\t}\n\n")

				output.write("\tloops_layers = {" + nl)
				for attr in dir(bm.loops.layers):
					attrval = getattr(bm.loops.layers,attr)
					if type(attrval) == bmesh.types.BMLayerCollection:
						output.write(tb + tb + "'"+attr+"': {" + nl)
						for key, val in attrval.items():
							output.write(tb + tb + tb + "'" + key + "': {" + nl)
							for f in bm.faces:
								output.write(tb + tb + tb + tb + str(f.index) + ": {" + nl)
								for l in f.loops:
									output.write(tb + tb + tb + tb + tb + str(l.index) + ":" + str(self.tuple_or_orig(l[val])) + "," + nl)
								output.write(tb + tb + tb + tb + "}," + nl)
							output.write(tb + tb + tb + "}," + nl)
						output.write(tb + tb + "}," + nl)
				output.write("\t}\n\n")

				output.write("\tvert_attributes = {\n")
				for attr in ('normal', 'select' ):
					el = [self.tuple_or_orig(getattr(v,attr)) for v in bm.verts]
					output.write("\t" + tb + "'" + attr + "' : " + str(el) + ",\n")
				output.write("\t}\n\n")

				output.write("\tedge_attributes = {\n")
				for attr in ('seam', 'smooth', 'select'):
					el = [self.tuple_or_orig(getattr(e,attr)) for e in bm.edges]
					output.write("\t" + tb + "'" + attr + "' : " + str(el) + ",\n")
				output.write("\t}\n\n")

				output.write("\tface_attributes = {\n")
				for attr in ('normal', 'smooth', 'select'):
					el = [self.tuple_or_orig(getattr(f,attr)) for f in bm.faces]
					output.write("\t" + tb + "'" + attr + "' : " + str(el) + ",\n")
				output.write("\t}\n\n")

			output.write("\n")

			bm.free()

		if self.include_operator:
			output.write('meshes = [ ' + ', '.join(names) + ' ]\n\n')
			output.write(b64decode(OperatorDef).decode())

		# force newly created text block on top if text editor is visible
		for a in context.screen.areas:
			for s in a.spaces:
				if s.type == 'TEXT_EDITOR':
					s.text = output

		return {'FINISHED'}

def register():
	bpy.utils.register_class(DumpMesh)
	bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
	bpy.utils.unregister_class(DumpMesh)
	bpy.types.VIEW3D_MT_object.remove(menu_func)

def menu_func(self, context):
	self.layout.operator(DumpMesh.bl_idname, icon='PLUGIN')
