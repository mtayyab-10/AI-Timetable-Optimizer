import tkinter as tk
from tkinter import messagebox
import threading
import time
import random
import traceback
from timetable import UniversityTimetable
from algorithms import backtrack
from metrics import CSPMetrics

class FastNUCESSolverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI2002 - CSP Timetable Visualizer")
        self.root.geometry("1100x700")
        
        # 1. Load Problem Data
        try:
            self.timetable = UniversityTimetable("instances/small")
            self.timetable.csp.metrics = CSPMetrics()
        except Exception as e:
            messagebox.showerror("Data Error", f"Failed to load CSVs:\n{e}")
            self.root.destroy()
            return

        self.slots = list(self.timetable.timeslots.keys())
        self.rooms = list(self.timetable.rooms.keys())
        
        # Generate colors for instructors
        instructors = set()
        for c in self.timetable.courses.values():
            instructors.add(c['Instructor'])
        
        self.colors = {}
        for inst in instructors:
            self.colors[inst] = f"#{random.randint(100, 250):02x}{random.randint(100, 250):02x}{random.randint(100, 250):02x}"

        self.build_ui()
        self.draw_grid({}) # Draw empty grid

    def build_ui(self):
        """Builds the Dashboard and Controls using standard Tkinter widgets."""
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(fill=tk.X)

        # BUTTONS
        self.btn_start = tk.Button(top_frame, text="▶ Start Search", bg="lightgreen", command=self.start_search)
        self.btn_start.pack(side=tk.LEFT, padx=10)
        
        tk.Button(top_frame, text="✏️ Edit CSV Data", bg="orange", command=self.open_csv_editor).pack(side=tk.LEFT, padx=10)

        # LIVE DASHBOARD
        self.lbl_stats = tk.Label(top_frame, text="Assignments: 0 | Backtracks: 0 | Checks: 0", font=("Arial", 12, "bold"))
        self.lbl_stats.pack(side=tk.RIGHT, padx=20)

        # VISUALIZATION CANVAS
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def draw_grid(self, assignment, current_var=None, is_backtracking=False):
        """Draws the room/timeslot matrix and plots assigned courses."""
        self.canvas.delete("all")
        cw, ch, ox, oy = 130, 60, 80, 50 # Cell Width, Height, Offsets

        # Draw Headers
        for i, slot in enumerate(self.slots):
            self.canvas.create_text(ox + (i*cw) + cw/2, oy/2, text=slot, font=("Arial", 9, "bold"))
        for j, room in enumerate(self.rooms):
            self.canvas.create_text(ox/2, oy + (j*ch) + ch/2, text=room, font=("Arial", 9, "bold"))

        # Draw Empty Background Cells first
        for i in range(len(self.slots)):
            for j in range(len(self.rooms)):
                self.canvas.create_rectangle(ox + (i*cw), oy + (j*ch), ox + ((i+1)*cw), oy + ((j+1)*ch), fill="#f0f0f0", outline="lightgray")

        # Draw Assigned Courses
        for course_id, (time_id, room_id) in assignment.items():
            if time_id in self.slots and room_id in self.rooms:
                x = ox + (self.slots.index(time_id) * cw)
                y = oy + (self.rooms.index(room_id) * ch)
                
                color = "red" if (is_backtracking and course_id == current_var) else self.colors.get(self.timetable.courses[course_id]['Instructor'], "lightblue")
                
                self.canvas.create_rectangle(x, y, x+cw, y+ch, fill=color, outline="black", width=2)
                self.canvas.create_text(x+cw/2, y+ch/2, text=course_id, font=("Arial", 10, "bold"))

    def search_callback(self, assignment, var, action):
        """This function is called by the algorithm at every step to animate the GUI."""
        metrics = self.timetable.csp.metrics
        self.lbl_stats.config(text=f"Assignments: {metrics.variable_assignments} | Backtracks: {metrics.backtracks} | Checks: {metrics.constraint_checks}")
        
        self.draw_grid(assignment, current_var=var, is_backtracking=(action=="backtrack"))
        self.root.update()
        time.sleep(0.05) # Speed of animation

    def start_search(self):
        """Runs the solver in the background so the UI doesn't freeze."""
        self.btn_start.config(state=tk.DISABLED, text="Searching...")
        
        def run():
            try:
                self.timetable.csp.metrics = CSPMetrics() # Reset stats
                self.timetable.csp.metrics.start_timer()
                
                # Run the algorithm
                assignment = backtrack({}, self.timetable.csp, 'mrv', 'lcv', use_forward_checking=False, update_gui=self.search_callback)
                
                if assignment: 
                    messagebox.showinfo("Done", "Timetable Scheduled Successfully!")
                else: 
                    messagebox.showwarning("Fail", "No valid schedule possible with current data.\n(Check if an instructor has 0 valid timeslots!)")
            
            except Exception as e:
                # to Catch any crashes and show an error box
                traceback.print_exc() 
                messagebox.showerror("Code Crashed!", f"The algorithm encountered an error:\n{e}\n\nCheck your terminal for the exact line number!")
            finally:
                self.btn_start.config(state=tk.NORMAL, text="▶ Start Search")
            
        threading.Thread(target=run, daemon=True).start()

    def open_csv_editor(self):
        """Opens a simple text editor to modify the courses.csv file live."""
        editor = tk.Toplevel(self.root)
        editor.title("CSV Editor - courses.csv")
        editor.geometry("600x400")
        
        text_box = tk.Text(editor, font=("Courier", 10))
        text_box.pack(fill=tk.BOTH, expand=True)
        
        try:
            with open("instances/small/courses.csv", "r", encoding='utf-8-sig') as f: 
                text_box.insert("1.0", f.read())
        except Exception as e:
            text_box.insert("1.0", f"Error loading file: {e}")
            
        def save():
            with open("instances/small/courses.csv", "w", encoding='utf-8-sig') as f: 
                f.write(text_box.get("1.0", tk.END).strip() + "\n")
            messagebox.showinfo("Saved", "CSV updated! Please restart the app to apply changes.")
            editor.destroy()
            
        tk.Button(editor, text=" Save Changes", bg="lightblue", command=save).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = FastNUCESSolverGUI(root)
    root.mainloop()