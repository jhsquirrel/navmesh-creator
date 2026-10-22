from scipy.spatial import Delaunay
import numpy as np
import sys
from pathlib import Path
import shutil
import datetime

# is in
def ii(big, item):
    for b in big:
        if np.array_equal(item, b):
            return True
    return False

# remove from list
def rl(big, item):
    c = 0
    for b in big:
        if np.array_equal(item, b):
            big.pop(c)
            return
        c += 1


def isInObjects(point, ob):
    for i in range(ob.shape[0]):
        # we are interested in x, z only (y is the height)
        if point[0] == ob[i][0] and point[2] == ob[i][2]:
            return True
    return False

def saveObj(filename, objdata):
    myfile = Path(filename + ".obj")
    od = '\n'.join(objdata)
    #print(od)
    if myfile.is_file():
        # file exists
        now = str(datetime.datetime.now())
        now = now.replace(":", "_")
        now = now.replace(" ", "_")
        now = now.replace("-", "")
        now = now[: len(now) - 7]
        # make a bak copy
        src = filename + ".obj"
        dst = src + "." + now
        shutil.copy(src, dst)
    with open(filename + ".obj", "w") as f:
        f.write(od)   

def readCoords(filename):
    dat = []
    points = []
    objects = []
    separate_objects = []
    with open(filename, "r") as fd:
        dat = fd.readlines()
        for d in dat:
            if d.startswith("#"):
                #print("comment " + d[1:])
                pass
            elif d.startswith("@"):
                objs2 = []
                objs = d[1:].split(";")
                ds = d[1:].split(";")
                for s in ds:
                    o = [float(x) for x in s.split(",")]
                    objects.append(o)
                    objs2.append(o)
                separate_objects.append(objs2)
            elif d.startswith("@") == False and d.startswith("#") == False:
                p = [float(x) for x in d.split(",")]
                points.append(p)
    return np.array(points), np.array(objects), np.array(separate_objects)

# make x, y, z coords
if len(sys.argv) != 2:
    print(sys.argv[0] + " datafile");
    sys.exit(1)
datafile = sys.argv[1]
points, objects, separate_objects = readCoords(datafile)

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
found_non_walkable = []
# for all non walkable objects (separate_objects), see if any points are in them
for so in separate_objects:
    for i in range(tri.simplices.shape[0]):
        object_count = 0
        for j in range( len(points[ tri.simplices[i] ]) ):
            point = points[ tri.simplices[i] ][j]
            if isInObjects(point, so):
                object_count += 1
        if object_count != 3:
            # if we have a triangle that is NOT in one of the "collision objects"
            # then add it to the updated_simplices list
            t = tri.simplices[i]
            # add to updated_simplices if not already added
            if ii(updated_simplices, t) == False:
                updated_simplices.append( t )
        else:
            t = tri.simplices[i]
            # add to found_non_walkable if not already added
            if ii(found_non_walkable, t) == False:
                found_non_walkable.append( t )

for f in found_non_walkable:
    rl(updated_simplices, f)

updated_simplices = np.array(updated_simplices)

# display what the points and triangle will look like in plan view
import matplotlib.pyplot as plt
plt.triplot(points[:,0], points[:,2], updated_simplices) 
plt.plot(points[:,0], points[:, 2], 'o')

# also - print out data so we can create an obj file for the aframe navmesh
objdata = []
print("#vertices")
objdata.append("#vertices")
for j, p in enumerate(points):
    plt.text(p[0]-0.03, p[2]+0.03, j, ha='right') # label the points
    print("v", p[0], p[1], p[2])
    objdata.append("v " + str(p[0]) + " " + str(p[1]) + " " + str(p[2]))
print("#vertices textures")
print("vt 0 0")
print("vt 1 0")
print("vt 1 1")
print("vt 0 1")
objdata.append("#vertices textures")
objdata.append("vt 0 0")
objdata.append("vt 1 0")
objdata.append("vt 1 1")
objdata.append("vt 0 1")
print("#faces")
objdata.append("#faces")
for j, s in enumerate(updated_simplices):
    p = points[s].mean(axis=0)
    plt.text(p[0], p[2], '#%d' % j, ha='center') # label triangles
    print("f " + str(s[2] + 1) + "/3 " + str(s[1] + 1) + "/2 " + str(s[0] + 1) + "/1")
    objdata.append("f " + str(s[2] + 1) + "/3 " + str(s[1] + 1) + "/2 " + str(s[0] + 1) + "/1")

saveObj(datafile, objdata)

plt.xlim(-maxXZ, maxXZ); plt.ylim(-maxXZ, maxXZ)
plt.show()
