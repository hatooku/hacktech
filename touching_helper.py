import math
import numpy as np

POINT_NUM = 8 # number of points, corresponding to 2 phones
TOUCHING_DISTANCE = 3 # resolution of screen / width of phone past detection
CELL_ERROR = 1 # used to compensate for inherent rectangle imprecision


# points is a list of (x, y) tuples
# finds the distances for all points in 2 sets: those adjacent to the starting
# point and all others
def findDistances(points, start_point, index):
    distancesPts = []
    distancesTuples = []
    distancesList = []
    allDistancesPts = []
    allDistancesTuples = []    
    for i in range(0, POINT_NUM):
        if i != index:
            distancesPts.append((start_point, points[i]))
            distancesList.append(math.sqrt(math.pow(start_point[0] - points[i][0], 2) \
                                           + math.pow(start_point[1] - points[i][1], 2)))
            distancesTuples.append((abs(start_point[0] - points[i][0]), \
                                    abs(start_point[1] - points[i][1])))
    for i in range(0, POINT_NUM):
        for j in range (0, i + 1):
            pt1 = points[i]
            pt2 = points[j]
            # don't include start point
            if pt1 != start_point and pt2 != start_point and pt1 != pt2:
                allDistancesPts.append((pt1, pt2))
                allDistancesTuples.append((abs(pt1[0] - pt2[0]), \
                                           abs(pt1[1] - pt2[1])))
    distances = np.asarray(distancesList)
    return distancesPts, distancesTuples, distances, allDistancesPts, allDistancesTuples


# finds all possible parallelograms (possibly degenerate) out of lists of points
# and distances, while taking into account possible error
def findParallelograms(distancesPts, distancesTuples, allDistancesPts, \
                       allDistancesTuples, points, start_point, sortedIndices):
    pgramList = []
    for i in range(0, POINT_NUM - 1):
        for j in range(0, len(allDistancesTuples)):
            index = sortedIndices[i]
            distance = distancesTuples[index]
            t1 = allDistancesPts[j]
            if (abs(allDistancesTuples[j][0] - distance[0]) <= TOUCHING_DISTANCE and \
                abs(allDistancesTuples[j][1] - distance[1]) <= TOUCHING_DISTANCE and \
                t1[0] != points[index] and t1[1] != points[index] and \
                t1[0] != start_point and t1[1] != start_point and t1[0] != t1[1]):
                pgramList.append((t1[0], t1[1], distancesPts[index][0], \
                                  distancesPts[index][1]))
    return pgramList


# determines if 3 points are collinear, takes as argument 3 (x, y) tuples
# representing points
def isCollinear(p1, p2, p3):
    if p1[0] != p2[0] and p1[0] != p3[0]:
        slope1 = (p2[1] - p1[1]) / float(p2[0] - p1[0])
        slope2 = (p3[1] - p1[1]) / float(p3[0] - p1[0])
        if slope1 == slope2:
            return True
    else:
        if (p1[0] == p2[0] and p1[0] == p3[0]):
            return True
    return False


# determines whether an input is a rectangle, with allowance for error
# takes as argument a list of 4 points
# uses the mathematical logic that rectangle diagonals should be equal length
def isRectangle(pointsList):
    pointsList = sorted(pointsList)
    dx1 = abs(pointsList[0][0] - pointsList[3][0])
    dy1 = abs(pointsList[0][1] - pointsList[3][1])
    dx2 = abs(pointsList[1][0] - pointsList[2][0])
    dy2 = abs(pointsList[1][1] - pointsList[2][1])
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
    if lower < dis and upper > dis and pointsList not in pointsList:
        return True
    return False


# determines whether a rectangle has another point inside it
# takes as arguments a list of tuples corresponding to the corners of a
# rectangle, as well as a list of all possible points
def hasPointIn(rect, points):
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
                    return True
    return False


# determines the cells which correspond to the lines through the 4 vertices
# of a rectangle
def findBresenhamLines(rect):
    points1 = []
    x = 0.0
    y = 0.0
    error = 0.0
    deltax = 0.0
    deltay = 0.0
    for k in range(0, len(rect)):
        for j in range(0, k):
            if k != j:
                p1 = rect[k]
                p2 = rect[j]
                deltay = p2[1] - p1[1]
                deltax = p2[0] - p1[0]
                # positive slope cases
                # 1st octant of plane
                if (deltax >= 0 and deltay >= 0 and deltax >= deltay):
                    y = p1[1]
                    for i in range(p1[0], p2[0] + 1):
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
    return points1


# finds the points belonging to each set of tuples (x, y) that represent points
# on the border between them
def findTouchingLines(points1, points2):
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
    return touchpoints1, touchpoints2


# takes a list of 4 vertices representing a rectangle, and determines which
# vertex corresponds to which on a rectangular phone
def findCorners(phone1):
    tL1 = (0, 0)
    tR1 = (0, 0)
    bL1 = (0, 0)
    bR1 = (0, 0)
    if math.pow(phone1[0][0] - phone1[1][0], 2) + math.pow(phone1[0][1] - phone1[1][1], 2) > \
        math.pow(phone1[0][0] - phone1[2][0], 2) + math.pow(phone1[0][1] - phone1[2][1], 2):
        if phone1[0][0] != phone1[1][0]: # if distance to 1 > distance to 2
            if phone1[0][1] > phone1[1][1]: # assuming y increasing downwards
                tL1 = phone1[1]
                tR1 = phone1[3]
                bL1 = phone1[0]
                bR1 = phone1[2]
            else:
                tL1 = phone1[0]
                tR1 = phone1[2]
                bL1 = phone1[1]
                bR1 = phone1[3]
        else:
            tL1 = phone1[0]
            tR1 = phone1[2]
            bL1 = phone1[1]
            bR1 = phone1[3]
    else:
        if phone1[0][0] != phone1[1][0]:
            if phone1[0][1] > phone1[1][1]: # assuming y increasing downwards
                tL1 = phone1[0]
                tR1 = phone1[1]
                bL1 = phone1[2]
                bR1 = phone1[3]
            else:
                tL1 = phone1[2]
                tR1 = phone1[3]
                bL1 = phone1[0]
                bR1 = phone1[1]
        else:
            tL1 = phone1[2]
            tR1 = phone1[3]
            bL1 = phone1[0]
            bR1 = phone1[1]
    return tL1, tR1, bL1, bR1