from scipy.spatial import Delaunay
import numpy as np

def isInObjects(point, ob):
    for i in range(ob.shape[0]):
        # we are interested in x, z only (y is the height)
        if point[0] == ob[i][0] and point[2] == ob[i][2]:
            return True
    return False

# make x, y, z coords
points = np.array([[0, 10, -50], [-50, 15, -50], [-50, 10, 0], [50, 15, 0], [40, 10, 50], [-70, 15, 50], [50, 10, 50]])

# maxXZ is for the matplotlib display
maxXZ = 0
for i in range(points.shape[0]):
    x = abs(points[i][0])
    z = abs(points[i][2])
    if x > maxXZ:
        maxXZ = x
    if z > maxXZ:
        maxXZ = z

# define a single object which is a square - this will be our "non walkable area" later
objects = np.array([[0, 0, 10], [-10, 0, 10], [-10, 0, 20], [0, 0, 20]])
points = np.append(points, objects, axis=0)
dpoints = []

# make an array of only x and z (ignore y)
for i in range(points.shape[0]):
    dpoints.append( [ points[i][0], points[i][2] ] )
dpoints = np.array(dpoints)

# use the dpoints array for the delaunday calculation
tri = Delaunay(dpoints)
updated_simplices = []

# remove any triangles that have 3 points within an object
# this is so the areas that are covered by "objects" i.e. "non walkable areas"
# will not have any triangles in them
for i in range(tri.simplices.shape[0]):
    object_count = 0
    for j in range( len(points[ tri.simplices[i] ]) ):
        point = points[ tri.simplices[i] ][j]
        if isInObjects(point, objects):
            object_count += 1
    if object_count != 3:
        # if we have a triangle that is NOT in one of the "collision objects"
        # then add it to the updated_simplices list
        t = tri.simplices[i]
        updated_simplices.append( t )

updated_simplices = np.array(updated_simplices)

# display what the points and triangle will look like in plan view
import matplotlib.pyplot as plt
plt.triplot(points[:,0], points[:,2], updated_simplices) 
plt.plot(points[:,0], points[:, 2], 'o')

# also - print out data so we can create an obj file for the aframe navmesh
print("#vertices")
for j, p in enumerate(points):
    plt.text(p[0]-0.03, p[2]+0.03, j, ha='right') # label the points
    print("v", p[0], p[1], p[2])
print("#vertices textures")
print("vt 0 0")
print("vt 1 0")
print("vt 1 1")
print("vt 0 1")
print("#faces")
for j, s in enumerate(updated_simplices):
    p = points[s].mean(axis=0)
    plt.text(p[0], p[2], '#%d' % j, ha='center') # label triangles
    print("f " + str(s[2] + 1) + "/3 " + str(s[1] + 1) + "/2 " + str(s[0] + 1) + "/1")
plt.xlim(-maxXZ, maxXZ); plt.ylim(-maxXZ, maxXZ)
plt.show()
