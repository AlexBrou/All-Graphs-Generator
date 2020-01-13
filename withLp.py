"""so, for any undirected graph with only 1 connected component (all nodes are connected directly or undirectly),
they must follow this rule:

sum( degrees of all vertices ) ==  2 X (sum of existing edges)

we already know that if a graph has n vertices, the minimum number of edges is n-1 and the
maximum is  (n X (n-1 ))/2,
so we can use constraint programming to figure out how many different graphs exist with N vertices
by constraining the degrees of the vertices

in case of N_vertices == 4:

for numberOfEdges in range( N_vertices-1   ,   (N_vertices X (N_vertices-1 ))/2        )

    v1,v2,v3,v4 <= Integers from 1 to N_vertices-1

    v1 <= v2
    v2 <= v3
    v3 <= v4


    sum(v1,v2,v3,v4) == numberOfEdges X 2

    CALCULATE ALL POSSIBLE SOLUTIONS USING GOOGLE OR TOOLS, CP_SOLVER


now, given all the possible solutions for all the CP problems presented above,
we create a LP model to figure out the graph

in case N_vertices == 4 , N_edges == 4  and degrees == [ 3,  2,  1,  2 ]:

create Integer value for each vertex
create Boolean variables for each edge

Vertex_i = sum( all the edges that come or go to i)

there is no use for a maximize function or minimize, just like the n-queens problem


AND THEEERE YOU GO :D :D :D :D



results are different from the non lp or cp method, but the sequence matches this:
http://oeis.org/A007721
"""


#####
from pulp import (
    lpSum,
    LpVariable,
    LpProblem,
    LpMinimize,
    LpInteger,
    LpBinary,
    LpStatus,
    value,
)

from ortools.sat.python import cp_model


def getOverlapEdgePairs(nVerts):
    allEdges = []
    for i in range(nVerts):
        for j in range(i+1, nVerts):
            allEdges.append([i, j])

    # print(allEdges)
    overlaps = []
    for i in range(len(allEdges)):
        for j in range(i+1, len(allEdges)):
            fst = allEdges[i]
            lst = allEdges[j]
            if lst[0] > fst[0] and lst[0] < fst[1]:
                if lst[1] > fst[1]:
                    overlaps.append([fst, lst])
    return overlaps


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.__solutions_array = []

    def on_solution_callback(self):
        self.__solution_count += 1
        sol = []
        for v in self.__variables:
            # print("%s=%i" % (v, self.Value(v)), end=" ")
            sol.append(self.Value(v))
        self.__solutions_array.append(sol)
        # print()

    def solution_count(self):
        return self.__solution_count, self.__solutions_array


def SearchForAllSolutionsSampleSat(n_vertices, n_edges):
    """Showcases calling the solver to search for all solutions."""
    # Creates the model.
    model = cp_model.CpModel()

    # Creates the variables.
    # n_vertices = 4
    # n_edges =
    variables = []
    for i in range(n_vertices):
        v = model.NewIntVar(1, n_vertices - 1, "Vertex" +
                            str(i + 1) + "_degree")
        variables.append(v)
    # Creates the constraints.
    for i in range(n_vertices - 1):
        v1 = variables[i]
        v2 = variables[i + 1]
        model.Add(v1 <= v2)

    model.Add(sum(variables) == 2 * n_edges)

    # Create a solver and solve.
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter(variables)
    status = solver.SearchForAllSolutions(model, solution_printer)

    # print("Status = %s" % solver.StatusName(status))
    n_sols, sols = solution_printer.solution_count()
    # print("Number of solutions found: %i" % n_sols)
    # print(sols)
    return sols


def getGraphFromDegrees(degrees):
    #numberOfEdges = sum(degrees) / 2
    numberOfVertices = len(degrees)

    prob = LpProblem("THE_GRAPH_CREATING_PROBLEM", LpMinimize)

    # vertices variables
    verticesVariables = []
    for vv in range(1, numberOfVertices + 1):
        vertVar = LpVariable("VERTEX_" + str(vv), 1,
                             numberOfVertices - 1, LpInteger)
        prob += vertVar == degrees[vv - 1]
        verticesVariables.append(vertVar)

    # edge variables
    edgeVariables = {}

    edgeVariablesForOverlap = {}

    for i in range(1, numberOfVertices + 1):
        for j in range(i + 1, numberOfVertices + 1):
            # print(i, " -- ", j)
            edgeVar = LpVariable("EDGE_" + str(i) + "-" +
                                 str(j), 0, 1, LpInteger)
            if i not in edgeVariables.keys():
                edgeVariables[i] = [edgeVar]
            else:
                edgeVariables[i].append(edgeVar)
            if j not in edgeVariables.keys():
                edgeVariables[j] = [edgeVar]
            else:
                edgeVariables[j].append(edgeVar)

            if i not in edgeVariablesForOverlap.keys():
                edgeVariablesForOverlap[i] = {}
            if j not in edgeVariablesForOverlap[i].keys():
                edgeVariablesForOverlap[i][j] = edgeVar
            if j not in edgeVariablesForOverlap.keys():
                edgeVariablesForOverlap[j] = {}
            if i not in edgeVariablesForOverlap[j].keys():
                edgeVariablesForOverlap[j][i] = edgeVar

    for i in edgeVariables:
        prob += lpSum(edgeVariables[i]) == verticesVariables[i - 1]

    # overlaps
    overlapVars = []
    for fst, lst in getOverlapEdgePairs(numberOfVertices):
        #print(fst, lst)
        # now we get the edgeVars respectively

        fstEdgeVar = edgeVariablesForOverlap[fst[0]+1][fst[1]+1]
        lstEdgeVar = edgeVariablesForOverlap[lst[0]+1][lst[1]+1]
        # print(fstEdgeVar)
        # print(lstEdgeVar)

        overlapVar = LpVariable(
            "OVERLAP_" + str(fst) + "-" + str(lst), 0, 1, LpInteger)

        prob += overlapVar >= fstEdgeVar + lstEdgeVar - 1
        overlapVars.append(overlapVar)
        # print()

    # objective function: minimize the overlaps

    prob += sum(overlapVars)

    # print("Solving...")
    prob.solve()
    statusText = LpStatus[prob.status]
    # print("Status:", statusText)
    if statusText == "Optimal":
        returner = []
        for v in prob.variables():
            if v.varValue != 0:
                # print(v.name, "=", v.varValue)
                varNameSplit = v.name.split("_")
                if varNameSplit[0] == "EDGE":
                    returner.append(
                        [int(varNameSplit[1]), int(varNameSplit[2])])
        return returner
    return None


n_vertices = 8
counter = 0
for n_edges in range(n_vertices - 1, int((n_vertices * (n_vertices - 1)) / 2) + 1):

    sols = [
        x
        for x in [
            getGraphFromDegrees(x)
            for x in SearchForAllSolutionsSampleSat(n_vertices, n_edges)
        ]
        if x != None
    ]

    print("EDGES: ", n_edges, "  ||  Number of solutions: ", len(sols))
    counter += len(sols)

print("NUMBER OF SOLS WITH #VERTICES ", n_vertices, " ==>> ", counter)
