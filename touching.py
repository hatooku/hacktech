import math
import numpy as np
import time
start_time = time.time()

POINT_NUM = 8 # number of points, corresponding to 2 phones
TOUCHING_DISTANCE = 3 # resolution of screen / width of phone past detection
CELL_ERROR = 1 # used to compensate for inherent rectangle imprecision

# test cases
#points = sorted([(2, 0), (1, 1), (2, 3), (3, 2), (4, 0), (4, 4), (6, 0), (6, 4)])
#points = sorted([(5, 1), (5, 2), (5, 3), (5, 0), (6, 0), (6, 1), (4, 2), (4, 3)])
#points = sorted([(1, 0), (4, 0), (4, 2), (1, 2), (1, 3), (4, 3), (4, 5), (1, 5)])
#points = sorted([(1, 0), (0, 1), (3, 2), (2, 3), (5, 1), (7, 2), (3, 4), (6, 5)])
#points = sorted([(1, 0), (0, 1), (1, 3), (2, 2), (3, 1), (4, 0), (5, 2), (4, 3)])
#points = sorted([(-3, 6), (-6, 2), (6, -7), (9, -3), (2, 4), (6, 4), (2, 10), (6, 10)])
#points = sorted([(-4, 3), (0, 0), (6, 8), (3, 11), (-6, 1), (-4, 2), (-3, 0), (-5, -1)])
#points = sorted([(1, 3), (2, 2), (3, 1), (4, 0), (5, 1), (4, 2), (3, 3), (2, 4)])
#points = sorted([(0, 1), (10, 11), (0, 0), (10, 10), (11, 10), (1, 0), (11, 11), (1, 1)])
#points = sorted([(25, 29), (58, 9), (11, 9), (44, 29), (24, 9), (12, 30), (59, 30), (47, 9)])
points = sorted([(16, 5), (41, 31), (37, 7), (18, 29), (54, 29), (6, 23), (26, 11), (47, 4)])

# start from leftmost, uppermost point (from sorted point list)
index = 0
point1 = points[index]

# create empty lists to use
distancesPts = []
distancesTuples = []
distancesList = []
allDistancesPts = []
allDistancesTuples = []

# find all distances from starting point
for i in range(0, POINT_NUM):
    if i != index:
        distancesPts.append((point1, points[i]))
        distancesList.append(math.sqrt(math.pow(point1[0] - points[i][0], 2) \
                                       + math.pow(point1[1] - points[i][1], 2)))
        distancesTuples.append((abs(point1[0] - points[i][0]), \
                                abs(point1[1] - points[i][1])))

# print distancesTuples

# find all distances between all pairs of the 8 points, except start point
for i in range(0, POINT_NUM):
    for j in range (0, i + 1):
        pt1 = points[i]
        pt2 = points[j]
        if pt1 != point1 and pt2 != point1 and pt1 != pt2: # don't include start point
            allDistancesPts.append((pt1, pt2))
            allDistancesTuples.append((abs(pt1[0] - pt2[0]), \
                                       abs(pt1[1] - pt2[1])))

# print allDistancesTuples

distances = np.asarray(distancesList)
sortedIndices = np.argsort(distances)
pgramList = []

'''print distances
print distancesPts
print allDistancesTuples
print allDistancesPts
print sortedIndices'''

# no error (exact) rectangle coordinate version
'''# equate distances from starting point with distances all distances, excluding
# those that include the starting point
# create list of possible parallelograms (possibly degenerate / collinear)
for i in range(0, POINT_NUM - 1):
    for j in range(0, len(allDistancesTuples)):
        index = sortedIndices[i]
        distance = distancesTuples[index]
        t1 = allDistancesPts[j]
        if (allDistancesTuples[j] == distance and t1[0] != points[index] and 
        t1[1] != points[index]): # don't repeat points
            pgramList.append((t1[0], t1[1], distancesPts[index][0],
                              distancesPts[index][1]))'''

# version that takes into account rectangle coordinate error
for i in range(0, POINT_NUM - 1):
    for j in range(0, len(allDistancesTuples)):
        index = sortedIndices[i]
        distance = distancesTuples[index]
        t1 = allDistancesPts[j]
        if (abs(allDistancesTuples[j][0] - distance[0]) <= TOUCHING_DISTANCE and \
            abs(allDistancesTuples[j][1] - distance[1]) <= TOUCHING_DISTANCE and \
            t1[0] != points[index] and t1[1] != points[index] and \
            t1[0] != point1 and t1[1] != point1 and t1[0] != t1[1]):
            pgramList.append((t1[0], t1[1], distancesPts[index][0], \
                              distancesPts[index][1]))

print pgramList

# test if points are collinear, and filter out parallelograms with them
pgramListNew = []
collinear = False
for i in range(0, len(pgramList)):
    temp = sorted(pgramList[i])
    collinear = False
    # test all combinations of 3 points
    for j in range(2, len(temp)):
        for k in range(1, j):
            for m in range(0, k):
                p1 = temp[j]
                p2 = temp[k]
                p3 = temp[m]
                if p1[0] != p2[0] and p1[0] != p3[0]:
                    slope1 = (p2[1] - p1[1]) / float(p2[0] - p1[0])
                    slope2 = (p3[1] - p1[1]) / float(p3[0] - p1[0])
                    if slope1 == slope2:
                        collinear = True
                        break
                else:
                    if (p1[0] == p2[0] and p1[0] == p3[0]):
                        collinear = True
                        break
    if collinear == False:
        pgramListNew.append(temp)

# print pgramListNew        

# test if remaining, nondegenerate parallelograms are rectangles
rectlist = []
for i in range(0, len(pgramListNew)):
    # sorted list guarantees 1st and 4th vertices are diagonal from each other
    temp = sorted(pgramListNew[i])
    # correspond to differences between diagonal lengths
    dx1 = abs(temp[0][0] - temp[3][0])
    dy1 = abs(temp[0][1] - temp[3][1])
    dx2 = abs(temp[1][0] - temp[2][0])
    dy2 = abs(temp[1][1] - temp[2][1])
    dis = math.sqrt(dx1 * dx1 + dy1 * dy1)
    
    errdx = 0 # compensation for inherent imprecision
    errdy = 0 # compensation for inherent imprecision
    if dx2 < CELL_ERROR:
        errdx = 0
    else:
        errdx = dx2 - CELL_ERROR
    if dy2 < CELL_ERROR:
        errdy = 0
    else:
        errdy = dy2 - CELL_ERROR
    # upper and lower bounds because of inherent imprecision
    lower = math.sqrt((errdx) * (errdx) + (errdy) * (errdy)) 
    upper = math.sqrt((dx2 + CELL_ERROR) * (dx2 + CELL_ERROR) + \
                      (dy2 + CELL_ERROR) * (dy2 + CELL_ERROR))
    if lower < dis and upper > dis and temp not in rectlist:
        rectlist.append(temp)

# print rectlist

# test if rectangles contain a point inside them
phone1 = []
pointIn = False
for i in range(0, len(rectlist)):
    rect = rectlist[i]
    pointIn = False
    for j in range(0, POINT_NUM):
        if points[j] not in rect:
            # calculations for dot product
            ABx = abs(-rect[0][0] + rect[1][0])
            ABy = abs(-rect[0][1] + rect[1][1])
            ADx = abs(-rect[0][0] + rect[2][0])
            ADy = abs(-rect[0][1] + rect[2][1])
            AB = ABx * ABx + ABy * ABy
            AD = ADx * ADx + ADy * ADy
            AMx = abs(-rect[0][0] + points[j][0])
            AMy = abs(-rect[0][1] + points[j][1])
            # M inside rectangle if 0 < AM * AB < AB * AB and 
            # 0 < AM * AD < AD * AD
            # http://math.stackexchange.com/questions/190111/how-to-check-if-a-point-is-inside-a-rectangle
            if AMx * ABx + AMy * ABy >= 0 and AMx * ABx + AMy * ABy < AB:
                if AMx * ADx + AMy * ADy >= 0 and AMx * ADx + AMy * ADy < AD:
                    pointIn = True
    if pointIn == False:
        phone1.append(rect[0])
        phone1.append(rect[1])
        phone1.append(rect[2])
        phone1.append(rect[3])
        break

print "Phone 1:"
print phone1

phone2 = []
for i in range(0, POINT_NUM):
    if points[i] not in phone1:
        phone2.append(points[i])
        
print "Phone 2:"
print phone2

# implementation of Bresenham Line Drawing Algorithm
points1 = []
x = 0.0
y = 0.0
error = 0.0
deltax = 0.0
deltay = 0.0
for k in range(0, 4):
    for j in range(0, k):
        if k != j:
            p1 = phone1[k]
            p2 = phone1[j]
            deltay = p2[1] - p1[1]
            deltax = p2[0] - p1[0]
            # positive slope cases
            # 1st octant of plane
            if (deltax >= 0 and deltay >= 0 and deltax >= deltay):
                y = p1[1]
                for i in range(p1, p2 + 1):
                    points1.append((i, y))
                    error += deltay
                    if 2 * error >= deltax:
                        error -= deltax
                        y += 1
            # 2nd octant of plane
            elif (deltax >= 0 and deltay >= 0 and deltax < deltay):
                x = p1[0];
                for i in range(p1[1], p2[1] + 1):
                    points1.append((x, i))
                    error += deltax; # increase error
                    if (2 * error >= deltay):
                        error -= deltay
                        x += 1
            # 5th octant of plane
            elif (deltax <= 0 and deltay <= 0 and deltax <= deltay):
                y = p2[1];
                for i in range(p2[0], p2[0] + 1):
                    points1.append((i, y))
                    error -= deltay
                    if (2 * error >= -deltax):
                        error += deltax # decrease error appropriately
                        y += 1
            # 6th octant of plane, increment by y
            elif (deltax <= 0 and deltay <= 0 and deltax > deltay):
                x = p2[0];
                for i in range(p2[1], p1[1] + 1):
                    points1.append((x, i))
                    error -= deltax; # increase error
                    if (2 * error >= -deltay): # if change in x is >= 0.5
                        error += deltay # decrease error appropriately
                        x += 1 # increase next x-coordinate
            
            # negative slope cases
            # 3rd octant of plane, increment by y
            elif (deltax <= 0 and deltay >= 0 and -deltax <= deltay):
                x = p1[0];
                for i in range(p1[1], p2[1] + 1):
                    points1.append((x, i)) # add point to list to be drawn
                    error += deltax; # decrease error
                    if (2 * error <= -deltay): # if change in x is <= -0.5
                        error += deltay; # increase error appropriately
                        x -= 1; # decrease next x-coordinate
            # 4th octant of plane, increment by x
            elif (deltax <= 0 and deltay >= 0 and -deltax > deltay):
                y = p2[1];
                for i in range(p2[0], p1[0] + 1):
                    points1.append((i, y)) # add point to list to be drawn
                    error -= deltay; # decrease error
                    if (2 * error <= deltax): # if change in y is <= -0.5
                        error -= deltax # increase error appropriately
                        y -= 1 # decrease next y-coordinate
            # 7th octant of plane, increment by y
            elif (deltax >= 0 and deltay <= 0 and deltax < -deltay):
                x = p2[0];
                for i in range(p2[1], p1[1] + 1):
                    points1.append((x, i)) # add point to list to be drawn
                    error -= deltax; # decrease error
                    if (2 * error <= deltay): # if change in x is <= -0.5
                        error -= deltay # increase error appropriately
                        x -= 1 # decrease next y-coordinate
            # 8th octant of plane, increment by x
            elif (deltax >= 0 and deltay <= 0 and deltax >= -deltay):
                y = p1[1];
                for i in range(p1[0], p2[0] + 1):
                    points1.append((i, y)) # add point to list to be drawn
                    error += deltay; # decrease error
                    if (2 * error <= -deltax): # if change in y is <= -0.5
                        error += deltax; # increase error appropriately
                        y -= 1; # decrease next x-coordinate       

# print points1

# repeated implementation of Bresenham Line Drawing Algorithm
points2 = []
x = 0.0
y = 0.0
error = 0.0
deltax = 0.0
deltay = 0.0
for k in range(0, 4):
    for j in range(0, k):
        if k != j:
            p1 = phone2[k]
            p2 = phone2[j]
            deltay = p2[1] - p1[1]
            deltax = p2[0] - p1[0]
            if (deltax >= 0 and deltay >= 0 and deltax >= deltay):
                y = p1[1]
                for i in range(p1, p2 + 1):
                    points2.append((i, y))
                    error += deltay
                    if 2 * error >= deltax:
                        error -= deltax
                        y += 1
            elif (deltax >= 0 and deltay >= 0 and deltax < deltay):
                x = p1[0];
                for i in range(p1[1], p2[1] + 1):
                    points2.append((x, i))
                    error += deltax; # increase error
                    if (2 * error >= deltay):
                        error -= deltay
                        x += 1
            elif (deltax <= 0 and deltay <= 0 and deltax <= deltay):
                y = p2[1];
                for i in range(p2[0], p2[0] + 1):
                    points2.append((i, y))
                    error -= deltay
                    if (2 * error >= -deltax):
                        error += deltax # decrease error appropriately
                        y += 1
            # 6th octant of plane, increment by y
            elif (deltax <= 0 and deltay <= 0 and deltax > deltay):
                x = p2[0];
                for i in range(p2[1], p1[1] + 1):
                    points2.append((x, i))
                    error -= deltax; # increase error
                    if (2 * error >= -deltay): # if change in x is >= 0.5
                        error += deltay # decrease error appropriately
                        x += 1 # increase next x-coordinate
            
            # negative slope cases
            # 3rd octant of plane, increment by y
            elif (deltax <= 0 and deltay >= 0 and -deltax <= deltay):
                x = p1[0];
                for i in range(p1[1], p2[1] + 1):
                    points2.append((x, i)) # add point to list to be drawn
                    error += deltax; # decrease error
                    if (2 * error <= -deltay): # if change in x is <= -0.5
                        error += deltay; # increase error appropriately
                        x -= 1; # decrease next x-coordinate
            # 4th octant of plane, increment by x
            elif (deltax <= 0 and deltay >= 0 and -deltax > deltay):
                y = p2[1];
                for i in range(p2[0], p1[0] + 1):
                    points2.append((i, y)) # add point to list to be drawn
                    error -= deltay; # decrease error
                    if (2 * error <= deltax): # if change in y is <= -0.5
                        error -= deltax # increase error appropriately
                        y -= 1 # decrease next y-coordinate
            # 7th octant of plane, increment by y
            elif (deltax >= 0 and deltay <= 0 and deltax < -deltay):
                x = p2[0];
                for i in range(p2[1], p1[1] + 1):
                    points2.append((x, i)) # add point to list to be drawn
                    error -= deltax; # decrease error
                    if (2 * error <= deltay): # if change in x is <= -0.5
                        error -= deltay # increase error appropriately
                        x -= 1 # decrease next y-coordinate
            # 8th octant of plane, increment by x
            elif (deltax >= 0 and deltay <= 0 and deltax >= -deltay):
                y = p1[1];
                for i in range(p1[0], p2[0] + 1):
                    points2.append((i, y)) # add point to list to be drawn
                    error += deltay; # decrease error
                    if (2 * error <= -deltax): # if change in y is <= -0.5
                        error += deltax; # increase error appropriately
                        y -= 1; # decrease next x-coordinate

# print points2

touchpoints1 = []
touchpoints2 = []
found = False
for i in range(0, len(points1)):
    found = False
    point1 = points1[i]
    minx = point1[0] - TOUCHING_DISTANCE
    maxx = point1[0] + TOUCHING_DISTANCE
    miny = point1[1] - TOUCHING_DISTANCE
    maxy = point1[1] + TOUCHING_DISTANCE
    for j in range(0, len(points2)):
        point2 = points2[j]
        if (point2[0] >= minx and point2[0] <= maxx and \
           point2[1] >= miny and point2[1] <= maxy):
            found = True
            touchpoints2.append(point2)
    if found == True:
        touchpoints1.append(point1)

touchpoints1 = sorted(list(set(touchpoints1)))
touchpoints2 = sorted(list(set(touchpoints2)))

print "Touching Boundary for Phone 1:"
print touchpoints1
print "Touching Boundary for Phone 2:"
print touchpoints2

print("--- %.10f sec ---" % ((time.time() - start_time)))