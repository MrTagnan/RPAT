import matplotlib.pyplot as plt
import numpy as np

import config
from scripts.ansi import *
from scripts.payload import payload_curve_generator


DEBUG_MODE = config.DEBUG_MODE
DARK_MODE = config.DARK_MODE
graph_factor = getattr(config, "graph_factor", None)
if graph_factor is None:
    graph_factor = config.graphFactor


def graph(rocket, leo_payload):
    print(YELLOW("\n=== Rocket Performance ==="))

    rocket_name = rocket.rocket_name

    cutoff = 9200  # m/s. Final graph cutoff; leave this alone as it impacts the integral.
    step = (rocket.rocket_mass / 1000) * graph_factor  # kg
    max_payload = rocket.rocket_mass * 0.1  # kg

    payloads, dvs, iterations = payload_curve_generator(
        rocket, step, max_payload, cutoff, False
    )

    # Checking if it is worth plotting the expended graph.
    total_reserve = sum(np.array(rocket.dry_mass_adj) - np.array(rocket.dry_mass))
    reserve_fraction = total_reserve / sum(rocket.dry_mass)
    plot_raw_curve = reserve_fraction > 0.02  # 2% threshold.

    if DEBUG_MODE:
        print(f"Current reserve fraction is: {reserve_fraction}")

    if plot_raw_curve:
        raw_payloads, raw_dvs, raw_iterations = payload_curve_generator(
            rocket, step, max_payload, cutoff, True
        )

    # Numerical calculus calculations for the metrics.
    # Energy cost per payload unit = f'(0) = d(Δv) / d(payload mass).
    # Finite difference differential approximation.
    dv_derivative = []

    for i in range(1, len(dvs)):
        delta_v = dvs[i] - dvs[i - 1]
        delta_payload = payloads[i] - payloads[i - 1]
        slope = (delta_v / delta_payload) if delta_payload != 0 else 0
        dv_derivative.append(slope)

    initial_slope = dv_derivative[0]  # m/s/kg
    normalised_eq = -initial_slope / dvs[0]

    if leo_payload >= 0:
        payload_fraction = leo_payload / rocket.rocket_mass
        leq = -np.log10(normalised_eq / (rocket.rocket_mass * (payload_fraction ** 3)))
    else:
        payload_fraction = 0
        leq = 0
        print("Error finding payload fraction and LEQ")

    # Trapezoidal rule numerical integration.
    area = 0
    for i in range(len(payloads) - 1):
        h = payloads[i + 1] - payloads[i]
        area += 0.5 * (dvs[i] + dvs[i + 1]) * h

    if DEBUG_MODE:
        print(f"Integral: {area:,.3f}")

    heq = area / (rocket.rocket_mass * 100)

    print(f"\n{GRAY('Initial ∆v drop per kg'):<30}: {D_GRAY(f'{initial_slope:.2f} m/s/kg')}")
    print(f"\n{GRAY('LEQ (Low-Energy Quotient)'):<30}: {D_GRAY(f'{leq:.3f}')}")
    print(f"{GRAY('HEQ (High-Energy Quotient)'):<30}: {D_GRAY(f'{heq:.3f}')}")
    print(f"\n{GRAY('Payload Fraction'):<30}: {D_GRAY(f'{payload_fraction * 100:.3f} %')}")

    # Plot for dv = f(payload).
    if DARK_MODE:
        plt.style.use("dark_background")
        fig = plt.figure(figsize=(8, 5), facecolor="black")
        ax = plt.gca()
        ax.set_facecolor("black")
        plt.grid(color="lightgrey", alpha=0.2)
    else:
        plt.figure(figsize=(8, 5))

    plt.plot(payloads, dvs, "-", lw=2, label="Achieved Δv")

    if plot_raw_curve:
        plt.plot(raw_payloads, raw_dvs, "--", lw=2, label="Achieved Δv without fuel reserves.")
        min_len = min(len(payloads), len(raw_dvs))
        plt.fill_between(
            payloads[:min_len],
            dvs[:min_len],
            raw_dvs[:min_len],
            color="orange",
            alpha=0.2,
            label="Performance loss due to reserves",
        )

    if DEBUG_MODE:
        plt.axhline(cutoff, color="red", linestyle="--", label=f"Δv cutoff ({cutoff}) m/s")
        plt.axvline(max_payload, color="red", linestyle="--", label=f"Payload cutoff: ({max_payload:.1f}) kg")
    else:
        plt.xlim(0, payloads[-1] + 10)
        plt.ylim(cutoff - 400, None)

    plt.xlabel("Payload mass (kg)")
    plt.ylabel("Total Δv (m/s)")
    plt.title(f"Rocket Performance: Payload vs. Δv, {rocket_name}")
    plt.legend(loc="best")
    plt.grid(True)
    plt.tight_layout()

    if DEBUG_MODE:
        print(f"Graphing completed with {iterations} iterations.")

    plt.show()

    # Plot for d(dv) = f'(payload).
    if DARK_MODE:
        fig = plt.figure(figsize=(8, 5), facecolor="black")
        plt.grid(color="lightgrey", alpha=0.2)
    else:
        plt.figure(figsize=(8, 5))

    plt.plot(payloads[1:], dv_derivative, "-", lw=2, color="orange", label="d(Δv)/d(payload)")
    plt.xlabel("Payload mass (kg)")
    plt.ylabel("Marginal ∆v loss (m/s per kg payload)")
    plt.title(f"Δv Sensitivity to Payload, {rocket_name}")
    plt.axhline(0, color="grey", linestyle="--")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
