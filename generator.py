import csv
import random
import os

class CSPDatasetGenerator:
    """
    Generates synthetic CSV datasets to test the scalability and performance 
    of the Constraint Satisfaction Problem timetabling solver.
    """
    def __init__(self, output_dir="instances"):
        self.output_dir = output_dir
        # SAFETY CHECK: Automatically create the folder if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.rooms = []
        self.timeslots = []
        self.instructors = []
        self.courses = []
        self.students = []

    def generate_rooms(self, count):
        possible_features = ["Projector", "Lab", "Whiteboard"]
        for i in range(count):
            room_id = f"R{i+1}"
            capacity = random.randint(30, 100)
            
            room_features = []
            for feature in possible_features:
                if random.choice([True, False]):
                    room_features.append(feature)
                    
            feature_string = ";".join(room_features) if room_features else ""
                
            self.rooms.append({
                'RoomID': room_id, 'Building': "Main Campus", 
                'Capacity': capacity, 'Features': feature_string
            })
            
        with open(f"{self.output_dir}/rooms.csv", 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['RoomID', 'Building', 'Capacity', 'Features'])
            writer.writeheader()
            writer.writerows(self.rooms)

    def generate_timeslots(self, count):
        days_options = ["Monday/Wednesday/Friday", "Tuesday/Thursday"]
        for i in range(count):
            days = random.choice(days_options)
            duration = 75 if days == "Tuesday/Thursday" else 50
            
            self.timeslots.append({
                'SlotID': f"SLOT{i+1}", 'Days': days, 
                'StartTime': f"{8 + (i % 8)}:00", 'Duration': duration
            })
            
        with open(f"{self.output_dir}/timeslots.csv", 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['SlotID', 'Days', 'StartTime', 'Duration'])
            writer.writeheader()
            writer.writerows(self.timeslots)

    def generate_instructors(self, count):
        # REQUIRED FAST-NU INSTRUCTORS
        core_instructors = [
            "Mr Aamir Gulzar", "Mr Arshad Islam", "Maam Marium Hida",
            "Mr Anas Bin Rashid", "Mr Hasnain Akhtar", "Mr Hasan Mujtaba",
            "Maam Bushra Kanwal"
        ]
        
        extra_first = ["Mr Tariq", "Mr Usman", "Mr Bilal", "Maam Fatima", "Maam Ayesha"]
        extra_last = ["Khan", "Ali", "Ahmed", "Malik", "Iqbal"]

        for i in range(count):
            if i < len(core_instructors):
                instructor_name = core_instructors[i]
            else:
                instructor_name = f"{random.choice(extra_first)} {random.choice(extra_last)}_{i}"
            
            available_slots = [s['SlotID'] for s in self.timeslots if random.randint(1, 100) <= 70]
            if not available_slots:
                available_slots.append(random.choice(self.timeslots)['SlotID'])
                
            self.instructors.append({
                'Instructor': instructor_name,
                'AvailableSlots': ";".join(available_slots),
                'PreferredSlots': available_slots[0] if available_slots else ""
            })
            
        with open(f"{self.output_dir}/instructor_availability.csv", 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Instructor', 'AvailableSlots', 'PreferredSlots'])
            writer.writeheader()
            writer.writerows(self.instructors)

    def generate_courses(self, count):
        possible_features = ["Projector", "Lab", "Whiteboard"]
        for i in range(count):
            course_features = [f for f in possible_features if random.randint(1, 100) <= 30]
            
            self.courses.append({
                'CourseID': f"CS{100 + i}",
                'CourseName': f"Course_{i}",
                'Instructor': random.choice(self.instructors)['Instructor'],
                'Enrollment': random.randint(20, 80),
                'Duration': 75 if random.choice([True, False]) else 50,
                'RoomFeatures': ";".join(course_features)
            })
            
        with open(f"{self.output_dir}/courses.csv", 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['CourseID', 'CourseName', 'Instructor', 'Enrollment', 'Duration', 'RoomFeatures'])
            writer.writeheader()
            writer.writerows(self.courses)

    def generate_students(self, count):
        # PAKISTANI NAMES REQUIRED BY RUBRIC
        first_names = ["Ali", "Ahmed", "Fatima", "Ayesha", "Usman", "Hassan", "Zainab", "Umar"]
        last_names = ["Khan", "Malik", "Siddiqui", "Tariq", "Sheikh", "Qureshi", "Raza"]
        
        for i in range(count):
            available_course_ids = [c['CourseID'] for c in self.courses]
            random.shuffle(available_course_ids)
            enrolled = available_course_ids[:random.randint(2, 5)]
            
            self.students.append({
                'StudentID': f"S{i+1:03d}",
                'StudentName': f"{random.choice(first_names)} {random.choice(last_names)}",
                'EnrolledCourses': ";".join(enrolled)
            })
            
        with open(f"{self.output_dir}/students.csv", 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['StudentID', 'StudentName', 'EnrolledCourses'])
            writer.writeheader()
            writer.writerows(self.students)

def main():
    print("Initializing CSP Dataset Generator...")
    generator = CSPDatasetGenerator(output_dir="instances")
    
    num_rooms = 15
    num_timeslots = 30
    num_instructors = 10
    num_courses = 20
    num_students = 15  
    
    generator.generate_rooms(num_rooms)
    generator.generate_timeslots(num_timeslots)
    generator.generate_instructors(num_instructors)
    generator.generate_courses(num_courses)
    generator.generate_students(num_students)
    
    print(f"Success: Generated {num_courses} courses across {num_rooms} rooms and {num_timeslots} timeslots.")

if __name__ == "__main__":
    main()