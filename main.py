from itertools import combinations, permutations
import copy


def checkIfGraphAlreadyInList(graph, graphList, numberOfVertices):
    for oldGraph in graphList:
        if compareGraph(graph, oldGraph, numberOfVertices):
            return True
    return False


def compareGraph(originalGraph, newGraph, numberOfVertices):
    if len(originalGraph) != len(newGraph):
        return False

    for perm in permutations(range(1, numberOfVertices + 1)):
        # print("PERMUTATION: ", perm)
        isTheSame = True
        for edge in newGraph:
            shiftedEdge = [perm[edge[0] - 1], perm[edge[1] - 1]]
            # print("original: ", edge, " || shifted: ", shiftedEdge)
            if shiftedEdge not in originalGraph:
                if shiftedEdge[::-1] not in originalGraph:
                    # print("not the same")
                    isTheSame = False
                    break
        if isTheSame:
            return True
        # print()
        # input("...")
    return False


def allCombs(numberOfVertices):
    ret = []
    for i in range(1, numberOfVertices + 1):
        ret.append(list(allCombsWithSize(numberOfVertices, size=i)))
    return ret


def allCombsWithSize(numberOfVertices, size):
    xx = combinations(range(1, numberOfVertices), size)
    return xx


def initLengthCounter(numberOfVertices):
    returner = {}
    maxNumberOfEdges = (numberOfVertices * (numberOfVertices - 1)) / 2
    for i in range(numberOfVertices - 1, int(maxNumberOfEdges + 1)):
        returner[i] = 0
    return returner


def checkLengthRules(lengthCounter, newGraphLength, numberOfVertices):
    # return True if the newGraph is not allowed
    if newGraphLength == numberOfVertices - 1:
        return lengthCounter[newGraphLength] >= numberOfVertices - 2
    elif newGraphLength == ((numberOfVertices * (numberOfVertices - 1)) / 2) - 2:
        return lengthCounter[newGraphLength] >= 2
    elif newGraphLength == ((numberOfVertices * (numberOfVertices - 1)) / 2) - 1:
        return lengthCounter[newGraphLength] >= 1
    elif newGraphLength == (numberOfVertices * (numberOfVertices - 1)) / 2:
        return lengthCounter[newGraphLength] >= 1


def getAllGraphsWithNumberOfVertices(numberOfVertices, allConnected=True):
    if allConnected:
        graphsByVerticeNumber = {2: [[[[1, 2]]]]}
    else:
        graphsByVerticeNumber = {2: [[[1, 2]], []]}
    assert isListOfLevels(graphsByVerticeNumber[2])
    thisNumberOfVertices = 3
    while thisNumberOfVertices <= numberOfVertices:
        # print()
        lengthCounter = initLengthCounter(thisNumberOfVertices)
        print("NUMBER OF VERTICES: ", thisNumberOfVertices, "\n")
        newOnes = []
        newCombs = allCombs(thisNumberOfVertices)
        if not allConnected:
            newCombs.append([])
        # print(thisNumberOfVertices, " -- ", newCombs)
        counter = 0
        for graphLevel in graphsByVerticeNumber[thisNumberOfVertices - 1]:
            # print("Graph Level : ", graphLevel, "// length: ", len(graphLevel[0]))
            # print("Graph length: ", len(graphLevel[0]))
            assert isLevel(graphLevel)
            for newCombsLevel in newCombs:
                # print(
                #     " ----  NewCombsLevel : ",
                #     newCombsLevel,
                #     "length: ",
                #     len(newCombsLevel),
                # )
                if newCombsLevel == []:
                    nCl = 0
                else:
                    nCl = len(newCombsLevel[0])
                sumLength = nCl + len(graphLevel[0])
                # print("SUM LENGTH: ", sumLength)
                if not (sumLength in lengthCounter.keys()) or checkLengthRules(
                    lengthCounter, sumLength, thisNumberOfVertices
                ):
                    print("early continue")
                    continue
                for graph in graphLevel:
                    assert isGraph(graph)
                    # if counter % 10 == 0:
                    #     print(
                    #         "V num ",
                    #         thisNumberOfVertices,
                    #         " : ",
                    #         counter
                    #         / len(graphsByVerticeNumber[thisNumberOfVertices - 1]),
                    #     )
                    # print("USING GRAPH: ", graph)
                    counter += 1
                    # print("LEVEL ", newCombsLevel)
                    for nn in newCombsLevel:
                        newGraph = copy.deepcopy(graph)
                        for nnn in nn:
                            newGraph.append([thisNumberOfVertices, nnn])
                        # print("testing for: ", newGraph)
                        if checkLengthRules(
                            lengthCounter, len(newGraph), thisNumberOfVertices
                        ):
                            # print("NOT, BREAKED")
                            # print(len(newCombsLevel) + len(graphLevel[0]))
                            break

                        if not checkIfGraphAlreadyInList(
                            newGraph, newOnes, thisNumberOfVertices
                        ):
                            # print("good! added")
                            newOnes.append(newGraph)
                            # print("                      ", newGraph)
                            lengthCounter[len(newGraph)] += 1
                        else:
                            # print("already exists!")
                            # print("NOT")
                            pass
                        # print()
                        # input("press enter...")
        # print("NEW ONES : ", newOnes)
        assert isLevel(newOnes)
        # print(newOnes)
        # print(newOnes)
        newGroupByLength = groupByLength(newOnes)
        assert isListOfLevels(newGroupByLength)
        # assert isListOfLevels(newGroupByLength)
        graphsByVerticeNumber[thisNumberOfVertices] = newGroupByLength
        thisNumberOfVertices += 1
        # print(
        #     "Length counter for #vertices ", thisNumberOfVertices, " -> ", lengthCounter
        # )
        # print("Number of total graphs: ", len(newOnes))
    # print("BAMBAM ", graphsByVerticeNumber[3])
    return graphsByVerticeNumber[numberOfVertices]


def groupByLength(xs):
    returner = {}
    for x in xs:
        assert isGraph(x)
        l = len(x)
        if l in returner.keys():
            returner[l].append(x)
        else:
            returner[l] = [x]

    # print("KEEEEYS  ", list(returner.keys()))
    returnerList = []
    for i in returner:
        # print("appending ", i, "...")
        # print(returner[i])
        assert isLevel(returner[i])
        returnerList.append(returner[i])
    # print("RETLIST ", returnerList)
    return returnerList


def getNumberOfDegrees(xs):
    vertices = {}
    for xy in xs:
        for i in xy:
            if i in vertices.keys():
                vertices[i] += 1
            else:
                vertices[i] = 1
    return vertices


def allGraphsStatistics(xs, degrees=False):
    sumOfAll = 0
    for li in xs:
        print("LENGHT ", len(li[0]), " == ", len(li))
        sumOfAll += len(li)
    print("\nSum of ALL: ", sumOfAll)

    print("\n\n\n")
    if degrees:
        for li in xs:
            for xs in li:
                gn = getNumberOfDegrees(xs)
                gnSum = sum(gn.values()) / len(xs)
                print(
                    "LENGTH: ",
                    len(xs),
                    " || Degrees: ",
                    gn,
                    " |||| EDGES: ",
                    xs,
                    " // ratio of sum(degrees)/nEdges: ",
                    gnSum,
                )


def isLevel(xs):
    for xx in xs:
        if not isGraph(xx):
            return False
    return True


def isGraph(xs):
    for xx in xs:
        if type(xx[0]) != int or type(xx[0]) != int:
            return False
    return True


def isListOfLevels(xs):
    for xx in xs:
        if not isLevel(xx):
            return False
    return True


if __name__ == "__main__":
    g1 = [[1, 2], [3, 1]]
    g2 = [[1, 2], [3, 2]]
    assert isGraph(g1)
    print(compareGraph(g1, g2, 3))

    # print(allCombs(5))
    g = [[[1, 2], [3, 1]], [[1, 2], [3, 1], [3, 2]]]
    g = [
        [[1, 2], [3, 1], [4, 1]],
        [[1, 2], [3, 1], [4, 2]],
        [[1, 2], [3, 1], [4, 1], [4, 2]],
        [[1, 2], [3, 1], [4, 2], [4, 3]],
        [[1, 2], [3, 1], [4, 1], [4, 2], [4, 3]],
        [[1, 2], [3, 1], [3, 2], [4, 1], [4, 2], [4, 3]],
    ]
    assert isLevel(g)
    gg = groupByLength(g)
    assert isListOfLevels(gg)
    # print("GG ", gg)
    # print(len(gg))
    # allGraphsStatistics(gg, 3)
    # 6 / 0
    numberOfVertices = 6
    zz = getAllGraphsWithNumberOfVertices(numberOfVertices, allConnected=True)
    # print(zz)
    allGraphsStatistics(zz, degrees=True)
    # for xx in zz:
    #    print(xx)

