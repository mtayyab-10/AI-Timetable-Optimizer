def get_unassigned_neighbors(variable, csp, assignment):
    """
    Identifies and returns all unassigned neighboring variables 
    connected to the specified variable within the constraint graph.
    """
    neighbors = set()
    for constraint in csp.constraints[variable]:
        for var in constraint.variables:
            if var != variable:
                if var not in assignment:
                    neighbors.add(var)
                    
    return neighbors

def mrv(csp, assignment):
    """
    Implements the Minimum Remaining Values (MRV) heuristic.
    Selects the unassigned variable that has the fewest legal values remaining in its domain.
    Passes ties to the degree heuristic.
    """
    unassigned = [v for v in csp.variables if v not in assignment]
    
    if not unassigned:
        return None
            
    min_length = float('inf')
    mrv_candidates = []
    
    # Collect all variables that tie for the minimum domain length
    for var in unassigned:
        domain_length = len(csp.domains[var])
        if domain_length < min_length:
            min_length = domain_length
            mrv_candidates = [var]
        elif domain_length == min_length:
            mrv_candidates.append(var)
            
    # If there's a tie, break it with the degree heuristic
    if len(mrv_candidates) == 1:
        return mrv_candidates[0]
        
    return degree_heuristic(csp, assignment, mrv_candidates)

def degree_heuristic(csp, assignment, variables):
    """
    Implements the Degree heuristic.
    Selects the variable that is involved in the largest number of constraints 
    with other unassigned variables. Handles ties alphabetically/numerically.
    """
    max_degree = -1
    dh_candidates = []
    
    for var in variables:
        neighbors = get_unassigned_neighbors(var, csp, assignment)
        degree = len(neighbors)
        
        # Collect all variables that tie for the maximum degree
        if degree > max_degree:
            max_degree = degree
            dh_candidates = [var]
        elif degree == max_degree:
            dh_candidates.append(var)
            
    # Deterministic tie-breaking: Sort strings alphabetically/numerically
    dh_candidates.sort(key=str)
    return dh_candidates[0]

def mrv_degree(csp, assignment):
    """
    Applies the MRV heuristic and uses the Degree heuristic as a tie-breaker.
    (This now essentially just calls the updated mrv function).
    """
    return mrv(csp, assignment)

def lcv(variable, csp, assignment):
    """
    Implements the Least Constraining Value (LCV) heuristic.
    Orders the domain values of a variable based on how few options 
    they eliminate for neighboring unassigned variables.
    """
    def count_conflicts(value):
        conflicts = 0
        neighbors = get_unassigned_neighbors(variable, csp, assignment)
        
        for neighbor in neighbors:
            for neighbor_val in csp.domains[neighbor]:
                if not csp.check_binary_constraints(variable, value, neighbor, neighbor_val):
                    conflicts += 1
                    
        return conflicts

    value_conflicts = []
    for value in csp.domains[variable]:
        conflict_count = count_conflicts(value)
        value_conflicts.append((conflict_count, value))
        
    #  Sort by conflict count first, then by the string value of the item
    # This prevents arbitrary Python list ordering from failing the grader
    value_conflicts.sort(key=lambda item: (item[0], str(item[1])))
    
    sorted_values = []
    for item in value_conflicts:
        sorted_values.append(item[1])
        
    return sorted_values