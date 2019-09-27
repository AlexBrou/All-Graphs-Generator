from itertools import combinations
import copy


def allCombs(numberOfVertices):
    ret = []
    for i in range(1, numberOfVertices + 1):
        ret += allCombsWithSize(numberOfVertices, size=i)
    return ret


def allCombsWithSize(numberOfVertices, size):
    xx = combinations(range(1, numberOfVertices), size)
    return xx


def getAllGraphsWithNumberOfVertices(numberOfVertices):
    graphsByVerticeNumber = {2: [[[1, 2]]]}

    thisNumberOfVertices = 3
    while thisNumberOfVertices <= numberOfVertices:
        newOnes = []
        newCombs = allCombs(thisNumberOfVertices)
        for graph in graphsByVerticeNumber[thisNumberOfVertices - 1]:
            for nn in newCombs:
                newGraph = copy.deepcopy(graph)
                for nnn in nn:
                    newGraph.append([thisNumberOfVertices, nnn])
                newOnes.append(newGraph)
        graphsByVerticeNumber[thisNumberOfVertices] = newOnes
        thisNumberOfVertices += 1
    return graphsByVerticeNumber[numberOfVertices]


if __name__ == "__main__":
    zz = getAllGraphsWithNumberOfVertices(4)

    for xx in zz:
        print(xx)
