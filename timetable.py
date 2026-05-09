import csv
from csp import CSP, Constraint

# ==========================================
# CONSTRAINTS DEFINITION
# ==========================================

class RoomOccupancyConstraint(Constraint):
    """Ensures no two courses are scheduled in the same room simultaneously."""
    def __init__(self, course1, course2):
        super().__init__([course1, course2])

    def satisfied(self, assignment, metrics):
        metrics.constraint_checks += 1
        if self.variables[0] not in assignment or self.variables[1] not in assignment:
            return True
        
        time1, room1 = assignment[self.variables[0]]
        time2, room2 = assignment[self.variables[1]]
        
        if time1 == time2 and room1 == room2:
            return False
        return True

class InstructorConflictConstraint(Constraint):
    """Ensures an instructor is not scheduled for multiple courses at the same time."""
    def __init__(self, course1, course2, instructor1, instructor2):
        super().__init__([course1, course2])
        self.instructor1 = instructor1
        self.instructor2 = instructor2

    def satisfied(self, assignment, metrics):
        metrics.constraint_checks += 1
        if self.variables[0] not in assignment or self.variables[1] not in assignment:
            return True
            
        time1, _ = assignment[self.variables[0]]
        time2, _ = assignment[self.variables[1]]
        
        if self.instructor1 == self.instructor2 and time1 == time2:
            return False
        return True

class StudentConflictConstraint(Constraint):
    """Ensures courses sharing enrolled students are not scheduled simultaneously."""
    def __init__(self, course1, course2, shared_students):
        super().__init__([course1, course2])
        self.shared_students = shared_students

    def satisfied(self, assignment, metrics):
        metrics.constraint_checks += 1
        if not self.shared_students:
            return True
            
        if self.variables[0] not in assignment or self.variables[1] not in assignment:
            return True
            
        time1, _ = assignment[self.variables[0]]
        time2, _ = assignment[self.variables[1]]
        
        if time1 == time2:
            return False
        return True

# ==========================================
# TIMETABLE PROBLEM FORMULATION
# ==========================================

class UniversityTimetable:
    def __init__(self, data_folder):
        self.courses = {}
        self.rooms = {}
        self.timeslots = {}
        self.student_enrollments = {}
        self.course_students = {} 
        self.instructor_availability = {}
        
        self.load_data(data_folder)
        self.variables = list(self.courses.keys())
        self.domains = self.setup_domains()
        
        self.csp = CSP(self.variables, self.domains)
        self.add_rules()

    def load_data(self, data_folder):        
        # Parse courses.csv
        with open(f"{data_folder}/courses.csv", 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, skipinitialspace=True)
            # CLEAN THE HEADERS: Strip accidental spaces from the TA's CSV files
            reader.fieldnames = [field.strip() for field in reader.fieldnames if field]
            
            for row in reader:
                features_list = []
                if row['RoomFeatures']:
                    split_features = row['RoomFeatures'].split(';')
                    for feature in split_features:
                        features_list.append(feature.strip())
                        
                self.courses[row['CourseID'].strip()] = {
                    'CourseName': row['CourseName'].strip(),
                    'Instructor': row['Instructor'].strip(),
                    'Enrollment': int(row['Enrollment'].strip()),
                    'Duration': int(row['Duration'].strip()),
                    'RoomFeatures': features_list
                }

        # Parse rooms.csv
        with open(f"{data_folder}/rooms.csv", 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, skipinitialspace=True)
            reader.fieldnames = [field.strip() for field in reader.fieldnames if field]
            
            for row in reader:
                room_features_list = []
                if row['Features']:
                    split_features = row['Features'].split(';')
                    for feature in split_features:
                        room_features_list.append(feature.strip())
                        
                self.rooms[row['RoomID'].strip()] = {
                    'Capacity': int(row['Capacity'].strip()),
                    'Features': room_features_list
                }

        # Parse timeslots.csv
        with open(f"{data_folder}/timeslots.csv", 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, skipinitialspace=True)
            reader.fieldnames = [field.strip() for field in reader.fieldnames if field]
            
            for row in reader:
                self.timeslots[row['SlotID'].strip()] = {
                    'Duration': int(row['Duration'].strip())
                }

        # Parse students.csv
        with open(f"{data_folder}/students.csv", 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, skipinitialspace=True)
            reader.fieldnames = [field.strip() for field in reader.fieldnames if field]
            
            for row in reader:
                student_id = row['StudentID'].strip()
                
                enrolled_list = []
                if row['EnrolledCourses']:
                    split_courses = row['EnrolledCourses'].split(';')
                    for course in split_courses:
                        enrolled_list.append(course.strip())
                
                self.student_enrollments[student_id] = enrolled_list
                
                for course in enrolled_list:
                    if course not in self.course_students:
                        self.course_students[course] = []
                    self.course_students[course].append(student_id)

        # Parse instructor_availability.csv safely
        try:
            with open(f"{data_folder}/instructor_availability.csv", 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file, skipinitialspace=True)
                reader.fieldnames = [field.strip() for field in reader.fieldnames if field]
                
                for row in reader:
                    instructor = row['Instructor'].strip()
                    
                    available_slots_list = []
                    if row['AvailableSlots']:
                        split_slots = row['AvailableSlots'].split(';')
                        for slot in split_slots:
                            available_slots_list.append(slot.strip())
                            
                    self.instructor_availability[instructor] = available_slots_list
        except FileNotFoundError:
            pass

    def setup_domains(self):
        """Enforces unary constraints (domain pruning) before search begins."""
        domains = {}
        for course_id, course_info in self.courses.items():
            valid_options = []
            
            for time_id, time_info in self.timeslots.items():
                for room_id, room_info in self.rooms.items():
                    
                    if room_info['Capacity'] < course_info['Enrollment']:
                        continue 
                        
                    has_features = True
                    for feature in course_info['RoomFeatures']:
                        if feature not in room_info['Features']:
                            has_features = False
                            break
                    if not has_features:
                        continue 
                        
                    if time_info['Duration'] != course_info['Duration']:
                        continue 
                        
                    instructor = course_info['Instructor']
                    if instructor in self.instructor_availability:
                        if time_id not in self.instructor_availability[instructor]:
                            continue 
                        
                    valid_options.append((time_id, room_id))
                    
            domains[course_id] = valid_options
        return domains

    def add_rules(self):
        """Constructs the constraint graph with binary constraints."""
        for i in range(len(self.variables)):
            for j in range(i + 1, len(self.variables)):
                course1 = self.variables[i]
                course2 = self.variables[j]
                
                self.csp.add_constraint(RoomOccupancyConstraint(course1, course2))
                
                inst1 = self.courses[course1]['Instructor']
                inst2 = self.courses[course2]['Instructor']
                self.csp.add_constraint(InstructorConflictConstraint(course1, course2, inst1, inst2))
                
                students1 = set(self.course_students.get(course1, []))
                students2 = set(self.course_students.get(course2, []))
                shares_students = len(students1.intersection(students2)) > 0
                
                if shares_students:
                    self.csp.add_constraint(StudentConflictConstraint(course1, course2, True))