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
        ret += allCombsWithSize(numberOfVertices, size=i)
    return ret


def allCombsWithSize(numberOfVertices, size):
    xx = combinations(range(1, numberOfVertices), size)
    return xx


def getAllGraphsWithNumberOfVertices(numberOfVertices, allConnected=True):
    if allConnected:
        graphsByVerticeNumber = {2: [[[1, 2]]]}
    else:
        graphsByVerticeNumber = {2: [[[1, 2]], []]}

    thisNumberOfVertices = 3
    while thisNumberOfVertices <= numberOfVertices:
        # print("NUMBER OF VERTICES: ", thisNumberOfVertices, "\n")
        newOnes = []
        newCombs = allCombs(thisNumberOfVertices)
        if not allConnected:
            newCombs.append([])
        # print(thisNumberOfVertices, " -- ", newCombs)
        counter = 0
        for graph in graphsByVerticeNumber[thisNumberOfVertices - 1]:
            if counter % 10 == 0:
                print(
                    "V num ",
                    thisNumberOfVertices,
                    " : ",
                    counter / len(graphsByVerticeNumber[thisNumberOfVertices - 1]),
                )
            counter += 1
            for nn in newCombs:
                newGraph = copy.deepcopy(graph)
                for nnn in nn:
                    newGraph.append([thisNumberOfVertices, nnn])
                # print("testing for: ", newGraph)
                if not checkIfGraphAlreadyInList(
                    newGraph, newOnes, thisNumberOfVertices
                ):
                    # print("good! added")
                    newOnes.append(newGraph)
                else:
                    # print("already exists!")
                    pass
                # print()
                # input("press enter...")
        graphsByVerticeNumber[thisNumberOfVertices] = newOnes
        thisNumberOfVertices += 1
    return graphsByVerticeNumber[numberOfVertices]


if __name__ == "__main__":
    g1 = [[1, 2], [3, 1]]
    g2 = [[1, 2], [3, 2]]
    print(compareGraph(g1, g2, 3))

    zz = getAllGraphsWithNumberOfVertices(6, allConnected=True)

    for xx in zz:
        print(xx)

