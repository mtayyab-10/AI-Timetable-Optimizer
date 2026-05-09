class Constraint:
    def __init__(self, variables):
        self.variables = variables

    def satisfied(self, assignment, metrics):
        return True

class CSP:
    def __init__(self, variables, domains):
        self.variables = variables
        self.domains = domains
        self.constraints = {}
        self.metrics = None # Will be set by main/experiments
        
        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise ValueError("Every variable must have an assigned domain.")

    def add_constraint(self, constraint):
        for variable in constraint.variables:
            if variable not in self.variables:
                raise ValueError("Variable not found in the CSP definition.")
            self.constraints[variable].append(constraint)

    def consistent(self, variable, assignment, metrics):
        """
        High-speed consistency check. 
        Evaluates constraints even if partially assigned, allowing early pruning.
        """
        for constraint in self.constraints[variable]:
            # PERFORMANCE FIX: Removed the is_fully_assigned check.
            # We now evaluate constraints immediately. It is the constraint's 
            # responsibility to handle missing assignment keys gracefully.
            if not constraint.satisfied(assignment, metrics):
                return False
        return True

    # --- PERFORMANCE BOOSTERS ---

    def get_neighbors(self, var):
        """Returns all variables that share a constraint with the given variable."""
        neighbors = set()
        for constraint in self.constraints[var]:
            for v in constraint.variables:
                if v != var:
                    neighbors.add(v)
        return list(neighbors)

    def is_consistent_with(self, var, value, assignment):
        """
        Atomic check. Does not copy. Does not loop unnecessarily.
        """
        # Add temporarily
        assignment[var] = value
        
        # Check only constraints involving the new variable
        for constraint in self.constraints[var]:
            # PERFORMANCE FIX: Removed the relevant/fully_assigned check here too
            if not constraint.satisfied(assignment, self.metrics):
                del assignment[var] # Clean up before returning
                return False
                
        del assignment[var] # Clean up
        return True

    def check_binary_constraints(self, var1, val1, var2, val2):
        """High-speed arc consistency check between two specific variables."""
        test_map = {var1: val1, var2: val2}
        for constraint in self.constraints[var1]:
            if var2 in constraint.variables:
                # If both are in the test_map, we can check satisfaction
                if not constraint.satisfied(test_map, self.metrics):
                    return False
        return True