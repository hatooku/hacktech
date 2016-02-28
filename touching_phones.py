import touching_helper as touch
import numpy as np
import time
import math

POINT_NUM = 8 # number of points, corresponding to 2 phones
TOUCHING_DISTANCE = 3 # resolution of screen / width of phone past detection
CELL_ERROR = 1 # used to compensate for inherent rectangle imprecision


def main(points):
    start_time = time.time()
    points = sorted(points)
    index = 0
    start_point = points[index]
    
    # generate all point distances needed for further computation
    distancesPts, distancesTuples, distances, allDistancesPts, \
        allDistancesTuples = touch.findDistances(points, start_point, index)
    
    sortedIndices = np.argsort(distances)
    
    # list of all sets of points with a pair of equal side lengths
    pgramList = touch.findParallelograms(distancesPts, distancesTuples, \
                                         allDistancesPts, allDistancesTuples, \
                                         points, start_point, sortedIndices)
    
    # now perform a series of tests to narrow down rectangles and thus phones
    # first test collinearity
    pgramListNew = []
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
                    if (touch.isCollinear(p1, p2, p3) == True):
                        collinear = True
                        break
        if collinear == False:
            pgramListNew.append(temp)
    
    # test if 4 noncollinear points are a rectangle (equal diagonal length)
    rectlist = []
    for i in range(0, len(pgramListNew)):
        if (touch.isRectangle(pgramListNew[i]) == True):
            rectlist.append(pgramListNew[i])
    
    # test if 4 points of rectangle have another point inside them, and accept
    # the first rectangle that does not
    phone1 = []
    for i in range(0, len(rectlist)):
        if (touch.hasPointIn(rectlist[i], points) == False):
            phone1.append(rectlist[i][0])
            phone1.append(rectlist[i][1])
            phone1.append(rectlist[i][2])
            phone1.append(rectlist[i][3])
            break
    
    # fill phone2 with remaining 4 out of 8 points
    phone2 = []
    for i in range(0, POINT_NUM):
        if points[i] not in phone1:
            phone2.append(points[i])
    
    # find cells that trace outline of phones
    points1 = touch.findBresenhamLines(phone1)
    points2 = touch.findBresenhamLines(phone2)
    
    # find points where the 2 outlines are touching
    touchpoints1, touchpoints2 = touch.findTouchingLines(points1, points2)
    
    # find corners of each phone
    tL1, tR1, bL1, bR1 = touch.findCorners(phone1)
    tL2, tR2, bL2, bR2 = touch.findCorners(phone2)
    
    print phone1
    print phone2
    print("--- %.10f sec ---" % ((time.time() - start_time)))
    return phone1, phone2, touchpoints1, touchpoints2, \
           (tL1, tR1, bL1, bR1), (tL2, tR2, bL2, bR2)