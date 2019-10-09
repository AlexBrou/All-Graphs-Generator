so, for any undirected graph with only 1 connected component (all nodes are connected directly or undirectly),
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





