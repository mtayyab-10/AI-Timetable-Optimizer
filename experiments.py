from timetable import UniversityTimetable
from algorithms import backtrack, mac_search, min_conflicts, SearchTimeout
from metrics import CSPMetrics
from generator import CSPDatasetGenerator

def run_solver(algorithm_name, var_heuristic, val_heuristic):
    """
    Initializes the CSP environment, executes a single solver configuration,
    and returns an isolated dictionary of performance metrics.
    """
    timetable = UniversityTimetable("instances")
    timetable.csp.metrics = CSPMetrics()
    timetable.csp.metrics.start_timer()

    assignment = None
    success = False

    try:
        if algorithm_name == 'backtrack':
            assignment = backtrack({}, timetable.csp, var_heuristic, val_heuristic, use_forward_checking=False)
        if algorithm_name == 'fc':
            assignment = backtrack({}, timetable.csp, var_heuristic, val_heuristic, use_forward_checking=True)
        if algorithm_name == 'mac':
            assignment = mac_search(timetable.csp, var_heuristic, val_heuristic)
        if algorithm_name == 'min-conflicts':
            assignment = min_conflicts(timetable.csp)
            
        if assignment is not None:
            if len(assignment) == len(timetable.variables):
                success = True
    except SearchTimeout:
        # The kill-switch was triggered to prevent infinite hanging
        success = False

    timetable.csp.metrics.stop_timer()

    metrics_dict = {}
    metrics_dict['time'] = timetable.csp.metrics.execution_time
    metrics_dict['backtracks'] = timetable.csp.metrics.backtracks
    metrics_dict['checks'] = timetable.csp.metrics.constraint_checks
    metrics_dict['success'] = success

    return metrics_dict

def run_multiple_instances(generator, courses, rooms, slots, density, tightness, algo, var_h, val_h, runs=1):
    """
    Executes multiple independent runs of a specific configuration.
    """
    total_time = 0.0
    total_backtracks = 0
    total_checks = 0
    success_count = 0

    for i in range(runs):
        print(f"      Instance {i+1}/{runs} in progress...", end='\r')
        
        student_count = int(courses * density * 2)
        instructor_count = max(int(courses / 3), 1)
        
        generator.generate_rooms(rooms)
        generator.generate_timeslots(slots)
        generator.generate_instructors(instructor_count)
        generator.generate_courses(courses)
        generator.generate_students(student_count)

        metrics = run_solver(algo, var_h, val_h)
        
        total_time += metrics['time']
        total_backtracks += metrics['backtracks']
        total_checks += metrics['checks']
        
        if metrics['success']:
            success_count += 1

    print(" " * 50, end='\r')

    avg_metrics = {}
    avg_metrics['avg_time'] = total_time / runs
    avg_metrics['avg_backtracks'] = total_backtracks / runs
    avg_metrics['avg_checks'] = total_checks / runs
    avg_metrics['success_rate'] = (success_count / runs) * 100

    return avg_metrics

def print_rubric_table(title, results):
    """Formats the aggregated experimental data into a professional terminal grid."""
    print(f"\n=========================================================================================")
    print(title)
    print(f"=========================================================================================")
    
    header = f"{'Configuration':<25} | {'Success %':<10} | {'Avg Time(s)':<12} | {'Avg Backtracks':<15} | {'Avg Checks':<15}"
    print(header)
    print("-" * len(header))

    for row in results:
        config_name = row[0]
        metrics = row[1]
        
        succ_str = f"{metrics['success_rate']:.1f}%"
        time_str = f"{metrics['avg_time']:.4f}"
        bt_str = f"{metrics['avg_backtracks']:.1f}"
        chk_str = f"{metrics['avg_checks']:.1f}"

        print(f"{config_name:<25} | {succ_str:<10} | {time_str:<12} | {bt_str:<15} | {chk_str:<15}")
        
    print(f"=========================================================================================\n")

def run_experiment_1():
    print("Running Experiment 1: Algorithm Comparison (1 instance per config for speed)...")
    generator = CSPDatasetGenerator("instances")
    
    configs = []
    configs.append({'c': 10, 'r': 8, 's': 20, 'd': 0.3, 't': 0.3})
    configs.append({'c': 20, 'r': 16, 's': 30, 'd': 0.5, 't': 0.5})
    configs.append({'c': 30, 'r': 24, 's': 40, 'd': 0.5, 't': 0.5})
    configs.append({'c': 50, 'r': 40, 's': 50, 'd': 0.7, 't': 0.7})

    for config in configs:
        results = []
        c = config['c']
        r = config['r']
        s = config['s']
        d = config['d']
        t = config['t']
        
        print(f"  -> Testing scale: {c} Courses, {r} Rooms, {s} Slots...")

        res_bt = run_multiple_instances(generator, c, r, s, d, t, 'backtrack', 'none', 'none', runs=5)
        results.append(("Backtracking", res_bt))

        res_fc = run_multiple_instances(generator, c, r, s, d, t, 'fc', 'none', 'none', runs=5)
        results.append(("Forward Checking", res_fc))

        res_mac = run_multiple_instances(generator, c, r, s, d, t, 'mac', 'none', 'none', runs=5)
        results.append(("MAC", res_mac))

        print_rubric_table(f"Exp 1: Scale = {c} Courses", results)

def run_experiment_2():
    print("Running Experiment 2: Heuristic Impact (20 Courses, Medium Tightness)...")
    generator = CSPDatasetGenerator("instances")
    results = []

    res_none = run_multiple_instances(generator, 20, 16, 30, 0.5, 0.5, 'mac', 'none', 'none', runs=5)
    results.append(("1. No Heuristics", res_none))

    res_mrv = run_multiple_instances(generator, 20, 16, 30, 0.5, 0.5, 'mac', 'mrv', 'none', runs=5)
    results.append(("2. MRV Only", res_mrv))

    res_mrv_deg = run_multiple_instances(generator, 20, 16, 30, 0.5, 0.5, 'mac', 'mrv_degree', 'none', runs=5)
    results.append(("3. MRV + Degree", res_mrv_deg))

    res_all = run_multiple_instances(generator, 20, 16, 30, 0.5, 0.5, 'mac', 'mrv_degree', 'lcv', runs=5)
    results.append(("4. MRV + Degree + LCV", res_all))

    print_rubric_table("Experiment 2: Heuristic Impact Analysis", results)

def run_experiment_3():
    print("Running Experiment 3: Phase Transition (Varying Tightness from 0.1 to 0.9)...")
    generator = CSPDatasetGenerator("instances")
    
    tightness_levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    results = []

    for t in tightness_levels:
        print(f"  -> Testing Tightness {t}...")
        res_mac = run_multiple_instances(generator, 20, 16, 30, 0.5, t, 'mac', 'mrv_degree', 'none', runs=5)
        
        config_name = f"Tightness: {t}"
        results.append((config_name, res_mac))

    print_rubric_table("Experiment 3: Phase Transition Data (Use for Plotting)", results)

def run_experiment_4():
    print("Running Experiment 4: Systematic vs Local Search...")
    generator = CSPDatasetGenerator("instances")
    results = []

    res_mac = run_multiple_instances(generator, 30, 24, 40, 0.5, 0.5, 'mac', 'mrv_degree', 'none', runs=5)
    results.append(("MAC (Systematic)", res_mac))

    res_min = run_multiple_instances(generator, 30, 24, 40, 0.5, 0.5, 'min-conflicts', 'none', 'none', runs=5)
    results.append(("Min-Conflicts (Local)", res_min))

    print_rubric_table("Experiment 4: MAC vs Min-Conflicts", results)

def main():
    run_experiment_1()
    run_experiment_2()
    run_experiment_3()
    run_experiment_4()
    
if __name__ == "__main__":
    main()