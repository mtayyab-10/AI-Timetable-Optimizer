import time
import random
from heuristics import mrv, mrv_degree, lcv, get_unassigned_neighbors

class SearchTimeout(Exception):
    """Custom exception to instantly shatter infinite search loops."""
    pass

def check_time(metrics):
    
    if time.time() - metrics.start_time > 45.0: 
        raise SearchTimeout()
    
    pass
    
def select_unassigned_variable(csp, assignment, var_heuristic):
    
    unassigned_variables = []
    for variable in csp.variables:
        if variable not in assignment:
            unassigned_variables.append(variable)
            
    if len(unassigned_variables) == 0:
        return None
        
    if var_heuristic == 'mrv':
        return mrv(csp, assignment)
        
    if var_heuristic == 'mrv_degree':
        return mrv_degree(csp, assignment)
        
    return unassigned_variables[0]

def order_domain_values(variable, csp, assignment, val_heuristic):
    if val_heuristic == 'lcv':
        return lcv(variable, csp, assignment)
        
    return csp.domains[variable]

# ==========================================
# ALGORITHM 1 & 2: BACKTRACKING & FORWARD CHECKING
# ==========================================

def backtrack(assignment, csp, var_heuristic, val_heuristic, use_forward_checking=False, update_gui=None):
    check_time(csp.metrics)
    if len(assignment) == len(csp.variables): return assignment

    var = select_unassigned_variable(csp, assignment, var_heuristic)
    if var is None: return None
        
    ordered_values = order_domain_values(var, csp, assignment, val_heuristic)

    for value in ordered_values:
        if csp.is_consistent_with(var, value, assignment):
            assignment[var] = value
            csp.metrics.variable_assignments += 1
            
            # ---> GUI HOOK: I just assigned a variable <---
            if update_gui: update_gui(assignment, var, "assign")
            
            if use_forward_checking:
                saved_domains = {v: list(csp.domains[v]) for v in csp.variables if v not in assignment}
                if forward_check(var, assignment, csp):
                    result = backtrack(assignment, csp, var_heuristic, val_heuristic, True, update_gui)
                    if result is not None: return result
                for v, dom in saved_domains.items(): csp.domains[v] = dom
            else:
                result = backtrack(assignment, csp, var_heuristic, val_heuristic, False, update_gui)
                if result is not None: return result
                
            del assignment[var]
            csp.metrics.backtracks += 1
            
            # ---> GUI HOOK: I just failed and had to backtrack <---
            if update_gui: update_gui(assignment, var, "backtrack")
            
    return None

def forward_check(var, assignment, csp):
    neighbors = get_unassigned_neighbors(var, csp, assignment)
    
    for neighbor in neighbors:
        check_time(csp.metrics)
        valid_values = []
        for val in csp.domains[neighbor]:
            if csp.is_consistent_with(neighbor, val, assignment):
                valid_values.append(val)
                
        csp.domains[neighbor] = valid_values
        
        if len(valid_values) == 0:
            return False 
            
    return True

# ==========================================
# ALGORITHM 3: MAC (Maintaining Arc Consistency)
# ==========================================

def mac_search(csp, var_heuristic, val_heuristic):
    def ac3(assignment, assigned_var=None):
        queue = []
        
        # SMART QUEUE: Only check neighbors of the variable we just assigned
        if assigned_var is not None:
            neighbors = csp.get_neighbors(assigned_var)
            for neighbor in neighbors:
                if neighbor not in assignment:
                    queue.append((neighbor, assigned_var))
        else:
            # Fallback for initial AC3 if needed
            for var in csp.variables:
                if var not in assignment:
                    neighbors = csp.get_neighbors(var)
                    for neighbor in neighbors:
                        queue.append((var, neighbor))
        
        while len(queue) > 0:
            check_time(csp.metrics)
            xi, xj = queue.pop(0)
            if revise(xi, xj, assignment):
                if len(csp.domains[xi]) == 0:
                    return False
                neighbors = csp.get_neighbors(xi)
                for xk in neighbors:
                    if xk != xj and xk not in assignment: # Prevent bouncing back
                        queue.append((xk, xi))
        return True

    def revise(xi, xj, assignment):
        revised = False
        new_domain = []
        
        # =========================================================
        # THE FIX: If xj is already assigned, DO NOT check all its values!
        # Only compare against the single value it is locked into.
        # =========================================================
        domain_j = [assignment[xj]] if xj in assignment else csp.domains[xj]

        for x_val in csp.domains[xi]:
            found_support = False
            for y_val in domain_j:
                if csp.check_binary_constraints(xi, x_val, xj, y_val):
                    found_support = True
                    break
            if found_support:
                new_domain.append(x_val)
            else:
                revised = True
        csp.domains[xi] = new_domain
        return revised

    def mac_backtrack(assignment):
        check_time(csp.metrics)
        if len(assignment) == len(csp.variables):
            return assignment

        var = select_unassigned_variable(csp, assignment, var_heuristic)
        if var is None:
            return None
            
        ordered_values = order_domain_values(var, csp, assignment, val_heuristic)
        for val in ordered_values:
            if csp.is_consistent_with(var, val, assignment):
                assignment[var] = val
                csp.metrics.variable_assignments += 1
                
                saved_domains = {}
                for v in csp.variables:
                    if v not in assignment:
                        saved_domains[v] = list(csp.domains[v])
                
                # PASS THE VARIABLE HERE!
                if ac3(assignment, assigned_var=var): 
                    result = mac_backtrack(assignment)
                    if result is not None:
                        return result
                
                del assignment[var]
                csp.metrics.backtracks += 1
                for v, dom in saved_domains.items():
                    csp.domains[v] = dom
        return None

    return mac_backtrack({})

# ==========================================
# ALGORITHM 4: MIN-CONFLICTS
# ==========================================

def min_conflicts(csp, max_steps=1000):
    assignment = {}
    for var in csp.variables:
        if len(csp.domains[var]) == 0:
            return None     
        assignment[var] = random.choice(csp.domains[var])
        csp.metrics.variable_assignments += 1

    def get_conflicted_vars(current_assignment):
        conflicted = []
        for variable in csp.variables:
            if not csp.consistent(variable, current_assignment, csp.metrics):
                conflicted.append(variable)
        return conflicted

    for step in range(max_steps):
        check_time(csp.metrics)
        conflicted_vars = get_conflicted_vars(assignment)
        
        if len(conflicted_vars) == 0:
            return assignment 

        var = random.choice(conflicted_vars)
        best_val = assignment[var]
        min_conflicts_count = float('inf')
        
        domain_copy = list(csp.domains[var])
        random.shuffle(domain_copy)
        
        for val in domain_copy:
            old_val = assignment[var]
            assignment[var] = val
            
            conflicts = 0
            for constraint in csp.constraints[var]:
                if not constraint.satisfied(assignment, csp.metrics):
                    conflicts += 1
            
            if conflicts < min_conflicts_count:
                min_conflicts_count = conflicts
                best_val = val
                
            assignment[var] = old_val
                
        assignment[var] = best_val
        csp.metrics.variable_assignments += 1
        csp.metrics.backtracks += 1 
        
    return None