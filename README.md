# AI Timetable Optimizer
---

## Project Overview

This project implements a **Constraint Satisfaction Problem (CSP) solver** to generate **conflict-free university timetables**.

It assigns:

- Time slots
- Classrooms

while satisfying strict constraints such as:

- Room conflicts
- Instructor availability
- Student clashes
- Room capacity

---

## Algorithms Implemented

### Systematic Search

- Backtracking
- Forward Checking (FC)
- MAC (Maintaining Arc Consistency / AC-3)

### Local Search

- Min-Conflicts

---

## Heuristics Used

- **MRV (Minimum Remaining Values)** — Select most constrained variable
- **Degree Heuristic** — Break MRV ties
- **LCV (Least Constraining Value)** — Reduce future conflicts

---

## Key Features

- Optimized AC-3 with localized queues
- Efficient LCV without heavy memory copying
- Detailed performance metrics tracking
- 15-second timeout (kill switch safety system)
- Automated experiments + phase transition analysis

---

## Project Structure

```
24i-0613_A2/
└── Q1_CSP/
    ├── algorithms.py
    ├── csp.py
    ├── experiments.py
    ├── generator.py
    ├── heuristics.py
    ├── main.py
    ├── metrics.py
    ├── plot_phase.py
    ├── timetable.py
    ├── requirements.txt
    ├── instances/
    └── results/
```

---

## Setup Instructions

### Requirements

- Python 3.8+

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## How to Run

### 1. Generate Dataset

```bash
python csp.py
```

### 2. Run Solver

**Basic:**

```bash
python main.py --input-dir instances/ --algorithm backtrack
```

**Advanced (MAC + Heuristics):**

```bash
python main.py --input-dir instances/ --algorithm mac --var-heuristic mrv_degree --val-heuristic lcv
```

---

## CLI Options

|       Flag        |                 Values                    |
|-------------------|-------------------------------------------|
| `--algorithm     `| `backtrack`, `fc`, `mac`, `min-conflicts` |
| `--var-heuristic `| `none`, `mrv`, `mrv_degree              ` |
| `--val-heuristic `| `none`, `lcv                            ` |

---

## Experiments

Run full evaluation suite:

```bash
python experiments.py
```

Includes:

- Scaling Analysis
- Heuristic Comparison
- Phase Transition
- Local vs Systematic

---

## Phase Transition Graph

Generate graph:

```bash
python plot_phase.py
```

**Output:** `results/phase_transition_plot.png`

---

## Solver Output Example

```
Solution Found!
Assignments: 50
Backtracks: 120
Time: 2.31s
```

---

## Performance Insights

- **MAC + MRV + LCV** — Best performance
- **Min-Conflicts** — Fast but approximate
- **Backtracking** — Slow without heuristics
- Phase transition shows sharp difficulty spike

---

## Learning Outcomes

- Applied CSP theory to real-world scheduling
- Compared systematic vs local search
- Implemented constraint propagation (AC-3)
- Analyzed scalability and complexity

---

## Notes

- Large datasets may trigger timeout (15s)
- Results vary due to random dataset generation
- Designed for academic evaluation

---

## Author

**Muhammad Tayyab**
FAST NUCES, Islamabad
