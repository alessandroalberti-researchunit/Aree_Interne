# -*- coding: utf-8 -*-
"""Genera asset grafici (radar chart 4 tipi di dato) per la presentazione."""
import numpy as np
import matplotlib.pyplot as plt

TEAL = "#2FE3C4"
TEAL_FILL = "#2FE3C4"
BG = "#0A0E17"
GRID = "#3C4658"
TEXT = "#E7ECF2"
MUTED = "#8B96A8"

labels = ["Thick Data", "Big Data", "Forward-Looking\nData", "Participatory\nData"]
values = [0.62, 0.78, 0.85, 0.55]  # mix illustrativo, non dati reali (grafico concettuale)

N = len(labels)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
values_closed = values + values[:1]
angles_closed = angles + angles[:1]

fig = plt.figure(figsize=(7.2, 7.2), dpi=300)
fig.patch.set_facecolor(BG)
ax = fig.add_subplot(111, polar=True)
ax.set_facecolor(BG)

ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

# grid rings
ax.set_ylim(0, 1)
rings = [0.25, 0.5, 0.75, 1.0]
ax.set_yticks(rings)
ax.set_yticklabels([f"{int(r*100)}%" for r in rings], color=MUTED, fontsize=9, fontfamily="sans-serif")
ax.set_xticks(angles)
ax.set_xticklabels(labels, color=TEXT, fontsize=13, fontfamily="sans-serif", fontweight="bold")

ax.spines["polar"].set_color(GRID)
ax.grid(color=GRID, linewidth=1.0, alpha=0.9)
ax.tick_params(axis="x", pad=18)

# plot shape
ax.plot(angles_closed, values_closed, color=TEAL, linewidth=2.6, solid_capstyle="round")
ax.fill(angles_closed, values_closed, color=TEAL_FILL, alpha=0.22)
ax.scatter(angles, values, s=60, color=TEAL, zorder=5, edgecolors=BG, linewidths=1.5)

ax.set_xlim(0, 2 * np.pi)
fig.subplots_adjust(left=0.14, right=0.86, top=0.88, bottom=0.12)
plt.savefig("assets/radar_4dati.png", facecolor=BG, bbox_inches="tight", pad_inches=0.35)
print("radar saved")
