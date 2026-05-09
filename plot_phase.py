import matplotlib.pyplot as plt




tightness = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

success_rate = [100.0, 100.0, 80.0, 60.0, 40.0, 20.0, 20.0, 0.0, 0.0]  # Example numbers
avg_checks = [100000, 250000, 800000, 1500000, 800000, 400000, 200000, 50000, 10000] # Example numbers

# Create the figure and the first axis (for Success %)
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot Success % on the left Y-axis
color1 = 'tab:blue'
ax1.set_xlabel('Constraint Tightness')
ax1.set_ylabel('Success Rate (%)', color=color1, fontweight='bold')
line1 = ax1.plot(tightness, success_rate, marker='o', color=color1, linewidth=2, label='Success Rate')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.set_ylim(0, 110) # 0 to 100% scale

# Create a second axis that shares the same X-axis (for Avg Checks)
ax2 = ax1.twinx()  

# Plot Avg Checks on the right Y-axis
color2 = 'tab:red'
ax2.set_ylabel('Search Cost (Avg Constraint Checks)', color=color2, fontweight='bold')
line2 = ax2.plot(tightness, avg_checks, marker='s', color=color2, linewidth=2, linestyle='--', label='Constraint Checks')
ax2.tick_params(axis='y', labelcolor=color2)

# Add title, grid, and legend
plt.title('Experiment 3: Phase Transition Analysis (20 Courses)')
ax1.grid(True, linestyle=':', alpha=0.7)

# Combine legends from both axes
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left')

# Save the plot as an image to put in your report
plt.savefig('phase_transition_plot.png', dpi=300, bbox_inches='tight')
print("Graph saved successfully as 'phase_transition_plot.png'!")

# Display the plot on screen
plt.show()