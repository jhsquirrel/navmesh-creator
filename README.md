# navmesh-creator
A basic navmesh creator using delaunday triangles (scipy)
The scipy_delaunay.py will create a set of delaunlay triangles and then remove any triangles that are "within an object".

In this way, we can create a navmesh out of contrained delaunday triangles.

An example can be found (delaunay.html) which uses the navmesh created by scipy_delaunay.py
Another (better?) example can be found (t1.html) which uses the updated scipy_delaunay2.py (which accepts a dat file
(e.g. t1.dat) which will create an obj file that can be used by aframe navmesh (example t1.html)
