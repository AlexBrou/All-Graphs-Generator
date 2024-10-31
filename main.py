from ortools.sat.python import cp_model
import networkx as nx
from tqdm import tqdm
import json

OUTPUT_FILE = "output_graphs_of_{vertices_number}.json"

ASCII_ART = """
   _____   .__   .__      ________                        .__        ________                                         __                 
  /  _  \  |  |  |  |    /  _____/_______ _____   ______  |  |__    /  _____/   ____    ____    ____ _______ _____  _/  |_  ____ _______ 
 /  /_\  \ |  |  |  |   /   \  ___\_  __ \\__  \  \____ \ |  |  \  /   \  ___ _/ __ \  /    \ _/ __ \\_  __ \\__  \ \   __\/  _ \\_  __ \
/    |    \|  |__|  |__ \    \_\  \|  | \/ / __ \_|  |_> >|   Y  \ \    \_\  \\  ___/ |   |  \\  ___/ |  | \/ / __ \_|  | (  <_> )|  | \/
\____|__  /|____/|____/  \______  /|__|   (____  /|   __/ |___|  /  \______  / \___  >|___|  / \___  >|__|   (____  /|__|  \____/ |__|   
        \/                      \/             \/ |__|         \/          \/      \/      \/      \/             \/                                                                                                                                                       

"""


def get_interval_of_potential_edges(num_vertices: int) -> tuple[int, int]:
    assert num_vertices > 0
    min_number_of_edges = num_vertices - 1
    max_number_of_edges = int((num_vertices * (num_vertices - 1)) / 2)

    return min_number_of_edges, max_number_of_edges


def get_all_degree_combinations(num_vertices: int, degree_sum: int) -> list[list[int]]:
    def helper(degree_sum, num_vertices, max_val) -> list[list] | list:
        if num_vertices == 0 and degree_sum == 0:
            return [[]]
        if num_vertices == 0 or degree_sum == 0:
            return []
        combinations = []
        for i in range(min(degree_sum, max_val), 0, -1):
            for combo in helper(degree_sum - i, num_vertices - 1, i):
                combinations.append([i] + combo)
        return combinations

    return helper(degree_sum, num_vertices, num_vertices - 1)


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.__solutionsArray = []

    def on_solution_callback(self):
        self.__solution_count += 1
        current_solution = []
        for v in self.__variables:
            if self.Value(v) == 1:
                var_str = v.Name().split("_")[1:]
                assert len(var_str) == 2
                current_solution.append([int(var_str_val) for var_str_val in var_str])
        self.__solutionsArray.append(current_solution)

    def solution_count(self):
        return self.__solution_count

    def solutionArray(self):
        return self.__solutionsArray


def filter_out_isomorphic(all_graphs: list[list[tuple[int, int]]]) -> tuple[list, int]:
    isomorphic_graphs: list[nx.Graph] = []

    # this kinda depends on luck, but it might be a good indicator
    # of useless computation after all isomorphic are found
    how_many_useless_candidates_after_all_are_found: int = 0

    for cur_candidate in all_graphs:
        cur_candidate_graph: nx.Graph = nx.from_edgelist(cur_candidate)
        found_match: bool = False
        for isomorphic_graph in isomorphic_graphs:
            if nx.is_isomorphic(cur_candidate_graph, isomorphic_graph):
                found_match = True
                break
        if not found_match:
            isomorphic_graphs.append(cur_candidate_graph)
            how_many_useless_candidates_after_all_are_found = 0
        else:
            how_many_useless_candidates_after_all_are_found += 1

    return isomorphic_graphs, how_many_useless_candidates_after_all_are_found


def get_all_graphs_from_degree_array(
    degree_array: list[int], number_of_vertices: int
) -> list:
    """Showcases calling the solver to search for all solutions."""
    # Creates the model.
    model = cp_model.CpModel()

    # Creates the variables.
    nodes_variables = []
    biggest_degree = max(degree_array)
    smallest_degree = min(degree_array)

    edges_dict = {}
    all_edges = []
    for i in range(1, number_of_vertices + 1):
        v = model.NewIntVar(smallest_degree, biggest_degree, "VertDeg_" + str(i))
        nodes_variables.append(v)
        for j in range(i + 1, number_of_vertices + 1):
            e = model.NewIntVar(0, 1, "Edge_" + str(i) + "_" + str(j))
            if i in edges_dict.keys():
                edges_dict[i].append(e)
            else:
                edges_dict[i] = [e]
            if j in edges_dict.keys():
                edges_dict[j].append(e)
            else:
                edges_dict[j] = [e]
            all_edges.append(e)

    for i in range(len(degree_array)):
        model.Add(nodes_variables[i] == degree_array[i])
        model.Add(sum(edges_dict[i + 1]) == nodes_variables[i])

    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter(all_edges)
    _ = solver.SearchForAllSolutions(model, solution_printer)

    return solution_printer.solutionArray()


def is_valid_degree_sequence(degree_sequence) -> bool:
    degree_sequence = sorted(degree_sequence, reverse=True)
    while degree_sequence:
        if degree_sequence[0] < 0 or degree_sequence[0] >= len(degree_sequence):
            return False
        current_degree = degree_sequence[0]
        degree_sequence = degree_sequence[1:]
        for i in range(current_degree):
            degree_sequence[i] -= 1
        degree_sequence = sorted(degree_sequence, reverse=True)
        if any(x < 0 for x in degree_sequence):
            return False
    return True


if __name__ == "__main__":

    print(ASCII_ART)

    n_vertices: int = int(
        input("Please insert the number of vertices of your Graph: ").strip()
    )

    current_output_file = OUTPUT_FILE.format(vertices_number=n_vertices)

    total_isomorphic_graphs: int = 0

    all_isomorphic_graphs: dict[str, list[tuple[int, int]]] = {}

    min_number_of_edges, max_number_of_edges = get_interval_of_potential_edges(
        n_vertices
    )

    for cur_number_of_edges in tqdm(
        range(min_number_of_edges, max_number_of_edges + 1)
    ):
        print(f"Current number of EDGES: {cur_number_of_edges}")

        all_degree_combinations = get_all_degree_combinations(
            num_vertices=n_vertices,
            degree_sum=cur_number_of_edges * 2,
        )

        valid_degree_combinations = [
            degree_combination
            for degree_combination in all_degree_combinations
            if is_valid_degree_sequence(degree_combination)
        ]

        for degree_combination in tqdm(valid_degree_combinations):
            print(f"Current Degree combination: {degree_combination}")

            all_graphs_found = get_all_graphs_from_degree_array(
                degree_combination, n_vertices
            )
            print(f"Number of ALL Graphs found: {len(all_graphs_found)}")

            all_unique_graphs_found, useless_counter = filter_out_isomorphic(
                all_graphs_found
            )
            total_isomorphic_graphs += len(all_unique_graphs_found)
            assert len(all_unique_graphs_found) > 0

            all_isomorphic_graphs[str(degree_combination)] = [
                list(x.edges) for x in all_unique_graphs_found
            ]

            print(f"Number of ALL UNIQUE Graphs found: {len(all_unique_graphs_found)}")
            print(f"Useless counter: {useless_counter}")

            print("-----")
        print("\n")

    print(f"TOTAL GRAPHS OF {n_vertices} VERTICES: {total_isomorphic_graphs}")

    with open(current_output_file, "w") as f:
        f.write(json.dumps(all_isomorphic_graphs))

    print(f"Result exported to {current_output_file}")
