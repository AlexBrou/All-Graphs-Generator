"""
This gets all the degrees arrays combinations with a linear algorithm, not using CP
"""

from ortools.sat.python import cp_model


def main(edges, nodes):

    maxEdgesByNodes = nodes*(nodes-1) / 2
    minEdgesByNodes = nodes-1

    assert minEdgesByNodes <= edges
    assert maxEdgesByNodes >= edges

    degreeSum = edges*2
    maxDegreeOnNode = nodes-1
    return mainAux(degreeSum, maxDegreeOnNode, nodes)


counter = 0


def mainAux(degreeSum, maxDegreeOnNode, nodes, ind=0):
    global counter
    sols = []
    for thisDegree in range(maxDegreeOnNode,   0, -1):
        # if nodes > 1 and degreeSum-thisDegree > 0:
        if nodes > 1 and degreeSum-thisDegree > nodes-2 and degreeSum-thisDegree > 0:
            #print(ind*" ",thisDegree)
            counter += 1
            ret = mainAux(degreeSum-thisDegree, thisDegree, nodes-1, ind+1)
            if ret != []:
                sols.append([thisDegree, ret])
        elif degreeSum-thisDegree == 0 and nodes == 1:
            #print(ind*" ",thisDegree)
            sols.append(thisDegree)
    return sols


def solParser(ss, nodesNumber, back=[]):
    foundSols = []
    for s in ss:
        if nodesNumber > 1:
            foundSols += solParser(s[1], nodesNumber-1, back+[s[0]])
        elif nodesNumber == 1:
            #print("FOUND ", back+[s  ])
            foundSols.append(back+[s])
    return foundSols


def getAllDegreesByNodes(nodes):
    sols = []
    maxEdgesByNodes = int(nodes*(nodes-1) / 2)
    minEdgesByNodes = nodes-1
    for edges in range(minEdgesByNodes, maxEdgesByNodes+1):
        ss = main(edges, nodes)
        ss = solParser(ss, nodes)
        for i in ss:
            print([i, edges])
            sols.append([i, edges])
    return sols


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self):
        self.__solution_count += 1
        for v in self.__variables:
            print('%s=%i' % (v, self.Value(v)), end=' ')
        print()

    def solution_count(self):
        return self.__solution_count


def getAllGraphsFromDegreeArray(degArr, nodesNumber):
    """Showcases calling the solver to search for all solutions."""
    # Creates the model.
    model = cp_model.CpModel()

    # Creates the variables.
    nodesVars = []
    biggestDegree = max(degArr)
    smallestDegree = min(degArr)

    edgesDict = {}
    allEdges = []
    for i in range(1, nodesNumber+1):
        v = model.NewIntVar(smallestDegree, biggestDegree, 'VertDeg_'+str(i))
        nodesVars.append(v)
        for j in range(i+1, nodesNumber+1):
            e = model.NewIntVar(0, 1, 'Edge_'+str(i)+'-'+str(j))
            if i in edgesDict.keys():
                edgesDict[i].append(e)
            else:
                edgesDict[i] = [e]
            if j in edgesDict.keys():
                edgesDict[j].append(e)
            else:
                edgesDict[j] = [e]
            allEdges.append(e)

    for i in range(len(degArr)):
        model.Add(nodesVars[i] == degArr[i])

        model.Add(sum(edgesDict[i+1]) == nodesVars[i])

    # Create a solver and solve.
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter(allEdges)
    status = solver.SearchForAllSolutions(model, solution_printer)

    print('Status = %s' % solver.StatusName(status))
    print('Number of solutions found: %i' % solution_printer.solution_count())


nodeNumber = 4
sols = getAllDegreesByNodes(nodeNumber)
print()
for ss in sols:
    print(ss)
    print("FOR THE DISPLAY OF ", ss[0], " , of edges ", ss[1])
    getAllGraphsFromDegreeArray(ss[0], nodeNumber)
    print()

#3 ,3 ,1 ,1
#3 ,2 ,2 ,1
#2 ,2 ,2 ,2
