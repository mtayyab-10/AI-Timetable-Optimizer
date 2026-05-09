import time

class CSPMetrics:
    """
    Tracks and records performance metrics for Constraint Satisfaction Problem algorithms,
    including execution time, variable assignments, backtracks, and constraint evaluations.
    """
    def __init__(self):
        self.variable_assignments = 0
        self.backtracks = 0
        self.constraint_checks = 0
        self.start_time = 0
        self.execution_time = 0

    def start_timer(self):
        """
        Records the initialization time of the search algorithm.
        """
        self.start_time = time.time()

    def stop_timer(self):
        """
        Calculates the total execution duration by comparing the current time 
        against the start time.
        """
        self.execution_time = time.time() - self.start_time

    def display(self, total_courses, scheduled_courses, solution_found):
        """
        Outputs the final performance metrics and solution quality to the standard output
        in a strictly structured format.
        """
        print("==============================================================")
        print("                   PERFORMANCE METRICS")
        print("==============================================================")
        print(f"Total Courses Scheduled : {scheduled_courses}/{total_courses}")
        print(f"Variable Assignments    : {self.variable_assignments}")
        print(f"Backtracks              : {self.backtracks}")
        print(f"Constraint Checks       : {self.constraint_checks}")
        print(f"Execution Time          : {self.execution_time:.3f} seconds")
        print("==============================================================")
        
        if solution_found:
            print("Solution Quality        : All hard constraints satisfied")
        else:
            print("Solution Quality        : Failed to find solution")
            
        print("==============================================================")