import argparse
from timetable import UniversityTimetable
from algorithms import backtrack, mac_search, min_conflicts
from metrics import CSPMetrics

def print_solution(assignment, timetable, algorithm_name):
    """
    Formats and prints the timetabling solution, including the schedule grid,
    course details, and any unresolved constraint warnings.
    """
    print("========================================")
    print("UNIVERSITY TIMETABLE SOLUTION")
    print("========================================")
    print(f"Algorithm : {algorithm_name}")
    
    status_text = "UNSATISFIABLE"
    if assignment:
        status_text = "SOLUTION FOUND"
        
    print(f"Status    : {status_text}")
    print("========================================")
    
    # Initialize a safe fallback dictionary to prevent NoneType errors
    safe_assignment = {}
    if assignment is not None:
        safe_assignment = assignment

    if safe_assignment:
        print("COURSE SCHEDULE:")
        print("================")
        for course_id, (time_id, room_id) in safe_assignment.items():
            course = timetable.courses[course_id]
            time_info = timetable.timeslots[time_id]
            room_info = timetable.rooms[room_id]
            
            print(f"{course_id}: {course['CourseName']}")
            print(f"  Instructor : {course['Instructor']}")
            print(f"  Time Slot  : {time_id} ({time_info['Duration']} mins)")
            print(f"  Room       : {room_id} (Capacity: {room_info['Capacity']})")
            print(f"  Enrolled   : {course['Enrollment']}\n")

        print("================================================================================================")
        print("                                    SCHEDULE GRID VIEW")
        print("================================================================================================")
        
        rooms = list(timetable.rooms.keys())
        timeslots = list(timetable.timeslots.keys())
        
        column_widths = {}
        for slot in timeslots:
            column_widths[slot] = len(slot) + 2

        # Define how many columns to print before wrapping to a new block
        max_columns_per_row = 10
        
        # Iterate through the timeslots in chunks
        for i in range(0, len(timeslots), max_columns_per_row):
            chunk_slots = []
            for j in range(i, i + max_columns_per_row):
                if j < len(timeslots):
                    chunk_slots.append(timeslots[j])
            
            header = f"{'Room':<6} |"
            for slot in chunk_slots:
                header += f" {slot:^{column_widths[slot]}} |"
            print(header)
            
            print("-" * len(header))
            
            for room in rooms:
                row = f"{room:<6} |"
                
                for slot in chunk_slots:
                    scheduled_course = "[EMPTY]"
                    
                    for c_id, (t_id, r_id) in safe_assignment.items():
                        if t_id == slot:
                            if r_id == room:
                                scheduled_course = c_id
                                break
                                
                    row += f" {scheduled_course:^{column_widths[slot]}} |"
                
                print(row)
        
        print("================================================================================================")

    # ==========================================
    # CONSTRAINT VIOLATIONS WARNINGS
    # ==========================================
    print()
    print("WARNINGS & VIOLATIONS:")
    
    if len(safe_assignment) == len(timetable.variables):
        print("No warnings. All constraints satisfied and all courses scheduled successfully.")
    else:
        # Identify any courses that the algorithm failed to place
        unscheduled_courses = []
        for course in timetable.variables:
            if course not in safe_assignment:
                unscheduled_courses.append(course)
                
        for course in unscheduled_courses:
            course_name = timetable.courses[course]['CourseName']
            print(f"[WARNING] Could not schedule {course}: {course_name}")
            
        print("\n[NOTE] The above courses were left unassigned due to strict, unresolvable constraint conflicts.")
    print()
    #print("===============================================================================")

def main():
    """
    Main entry point. Parses command-line arguments, initializes the CSP environment,
    executes the selected algorithm, and outputs performance metrics.

    Supports the full CLI spec from the assignment:
      python main.py --input-dir instances/small/ --algorithm mac
      python main.py --generate --courses 20 --rooms 16 --density 0.5 --output-dir instances/test/
      python main.py --experiment 1
    """
    import sys
    parser = argparse.ArgumentParser(description="University Timetabling CSP Solver")

    # ---- Mode flags (mutually exclusive groups) ----
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--experiment", type=int, choices=[1, 2, 3, 4],
                            help="Run one of the 4 experimental suites")
    mode_group.add_argument("--generate", action="store_true",
                            help="Generate a synthetic CSP instance")

    # ---- Solve mode arguments ----
    parser.add_argument("--input-dir", type=str, default="instances/small",
                        help="Directory containing CSV files")
    parser.add_argument("--algorithm", type=str, choices=['backtrack', 'fc', 'mac', 'min-conflicts'],
                        default='mac')
    parser.add_argument("--var-heuristic", type=str, choices=['none', 'mrv', 'mrv_degree'], default='none')
    parser.add_argument("--val-heuristic", type=str, choices=['none', 'lcv'], default='none')

    # ---- Generator arguments ----
    parser.add_argument("--courses", type=int, default=20, help="Number of courses to generate")
    parser.add_argument("--rooms", type=int, default=16,  help="Number of rooms to generate")
    parser.add_argument("--slots", type=int, default=30,  help="Number of time slots to generate")
    parser.add_argument("--density",   type=float, default=0.5, help="Constraint density (0-1)")
    parser.add_argument("--tightness", type=float, default=0.5, help="Constraint tightness (0-1)")
    parser.add_argument("--output-dir", type=str, default="instances/test",
                        help="Output directory for generated CSV files")

    args = parser.parse_args()

    # ---- Experiment mode ----
    if args.experiment is not None:
        from experiments import run_experiment_1, run_experiment_2, run_experiment_3, run_experiment_4
        runners = {1: run_experiment_1, 2: run_experiment_2,
                   3: run_experiment_3, 4: run_experiment_4}
        print(f"[main.py] Delegating to Experiment {args.experiment}...")
        runners[args.experiment]()
        return

    # ---- Generator mode ----
    if args.generate:
        from generator import CSPDatasetGenerator
        print(f"[main.py] Generating instance: {args.courses} courses, "
              f"{args.rooms} rooms, {args.slots} slots -> {args.output_dir}")
        gen = CSPDatasetGenerator(output_dir=args.output_dir)
        instructor_count = max(int(args.courses / 3), 7)
        student_count = int(args.courses * args.density * 2)
        gen.generate_rooms(args.rooms)
        gen.generate_timeslots(args.slots)
        gen.generate_instructors(instructor_count)
        gen.generate_courses(args.courses)
        gen.generate_students(student_count)
        print(f"[main.py] Done. Files written to '{args.output_dir}/'")
        return

    # ---- Solve mode ----
    timetable = UniversityTimetable(args.input_dir)
    timetable.csp.metrics = CSPMetrics()
    timetable.csp.metrics.start_timer()

    algo_name = args.algorithm.upper()
    if args.var_heuristic != 'none':
        algo_name += f" + {args.var_heuristic.upper()}"
    if args.val_heuristic != 'none':
        algo_name += f" + {args.val_heuristic.upper()}"

    assignment = None
    if args.algorithm == 'backtrack':
        assignment = backtrack({}, timetable.csp, args.var_heuristic, args.val_heuristic, use_forward_checking=False)
    elif args.algorithm == 'fc':
        assignment = backtrack({}, timetable.csp, args.var_heuristic, args.val_heuristic, use_forward_checking=True)
    elif args.algorithm == 'mac':
        assignment = mac_search(timetable.csp, args.var_heuristic, args.val_heuristic)
    elif args.algorithm == 'min-conflicts':
        assignment = min_conflicts(timetable.csp)

    timetable.csp.metrics.stop_timer()
    print_solution(assignment, timetable, algo_name)

    scheduled_count = len(assignment) if assignment else 0
    solution_found = assignment is not None
    timetable.csp.metrics.display(len(timetable.variables), scheduled_count, solution_found)


if __name__ == "__main__":
    main()