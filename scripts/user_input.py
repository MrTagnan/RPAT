import json
import os
from dataclasses import dataclass
from typing import List

from config import CUSTOM_ROCKETS_PATH, DEFAULT_ROCKETS_PATH
from scripts.ansi import *


@dataclass
class Rocket:
    name: str
    stages: int
    isp: List[float]
    dry_mass: List[float]
    wet_mass: List[float]
    dry_mass_adj: List[float]
    wet_mass_adj: List[float]
    fuel_reserve: List[float]
    man_stage_addition: bool
    rocket_name: str
    rocket_mass: float


def total_mass(man_stage_addition, wet_mass):
    if man_stage_addition:
        rocket_mass = max(wet_mass)
    else:
        rocket_mass = sum(wet_mass)

    return rocket_mass


def load_rockets():
    rockets = {}

    # Default rockets.
    default_path = os.path.join(os.path.dirname(__file__), DEFAULT_ROCKETS_PATH)
    with open(default_path, "r") as file:
        rockets.update(json.load(file))

    # Custom rockets.
    custom_path = os.path.join(os.path.dirname(__file__), CUSTOM_ROCKETS_PATH)
    if os.path.exists(custom_path):
        with open(custom_path, "r") as file:
            custom_rockets = json.load(file)

        for name, data in custom_rockets.items():
            if name in rockets:
                print(f"[Warning] Custom rocket '{name}' conflicts with a default entry and will be skipped.")
                print("To fix this, please rename the rocket to something non-conflicting")
            else:
                rockets[name] = data

    return rockets


def add_reserves(stages, fuel_reserve, dry_mass, wet_mass):
    dry_mass_adj = []
    wet_mass_adj = []

    for i in range(stages):
        reserve = fuel_reserve[i]
        prop_mass = wet_mass[i] - dry_mass[i]

        if reserve > prop_mass:
            print("Fuel reserves are set up incorrectly, resetting")
            reserve = 0

        if reserve > 0:
            dry_mass_adj.append(dry_mass[i] + reserve)
            wet_mass_adj.append(wet_mass[i] - reserve)
        else:
            dry_mass_adj.append(dry_mass[i])
            wet_mass_adj.append(wet_mass[i])

    return dry_mass_adj, wet_mass_adj


def select_default():
    rockets = load_rockets()
    print(YELLOW("\nAvailable Default Rockets:"))

    for i, (key, rocket_data) in enumerate(rockets.items()):
        print(f"{GRAY(f'{i:3}')} : {D_GRAY(key):2} — {GRAY(rocket_data['desc'])}")

    selected = input(f"\n{GREEN('Enter the rocket name or number: ')}").lower().strip()

    if selected.isdigit():
        index = int(selected)

        if 0 <= index < len(rockets):
            key = list(rockets.keys())[index]
        else:
            print(RED("Invalid selection. Please try again."))
            return None
    elif selected in rockets:
        key = selected
    else:
        print(RED("Rocket not found, please try again."))
        return None

    rocket_data = rockets[key]
    fuel_reserve = rocket_data.get("fuel_reserve", [0] * rocket_data["stages"])

    dry_mass_adj, wet_mass_adj = add_reserves(
        rocket_data["stages"],
        fuel_reserve,
        rocket_data["dryMass"],
        rocket_data["wetMass"],
    )

    rocket_mass = total_mass(rocket_data["manStage"], wet_mass_adj)

    print(f"{GREEN('Selected rocket:')} {GRAY(rocket_data['desc'])}")

    return Rocket(
        name=key,
        stages=rocket_data["stages"],
        isp=rocket_data["isp"],
        dry_mass=rocket_data["dryMass"],
        wet_mass=rocket_data["wetMass"],
        dry_mass_adj=dry_mass_adj,
        wet_mass_adj=wet_mass_adj,
        fuel_reserve=fuel_reserve,
        man_stage_addition=rocket_data["manStage"],
        rocket_name=rocket_data["desc"],
        rocket_mass=rocket_mass,
    )


def manual_entry():
    name = input(GREEN("What is the name of your rocket? "))

    try:
        stages = int(input(GREEN("How many stages does your rocket have? ")))
    except ValueError:
        print("Invalid input, please try again.")
        return None

    while True:
        response = input(
            GREEN("Will you be including the mass of the upper stages in the lower stages? (y/n): ")
        ).strip().lower()

        if response in ("y", "yes", "true"):
            man_stage_addition = True
            break
        elif response in ("n", "no", "false"):
            man_stage_addition = False
            break
        else:
            print(GREEN("Please enter 'y' or 'n'."))

    dry_mass = []
    wet_mass = []
    isp = []

    for i in range(stages):
        print(YELLOW(f"\nStage {i + 1}:"))
        dry = float(input(GREEN("  Dry mass (kg) : ")))
        wet = float(input(GREEN("  Wet Mass (kg) : ")))
        isps = float(input(GREEN("  ISP (s)       : ")))

        dry_mass.append(dry)
        wet_mass.append(wet)
        isp.append(isps)

    fuel_reserve = [0] * stages
    dry_mass_adj, wet_mass_adj = add_reserves(stages, fuel_reserve, dry_mass, wet_mass)
    rocket_mass = total_mass(man_stage_addition, wet_mass_adj)

    return Rocket(
        name=name,
        stages=stages,
        isp=isp,
        dry_mass=dry_mass,
        wet_mass=wet_mass,
        dry_mass_adj=dry_mass_adj,
        wet_mass_adj=wet_mass_adj,
        fuel_reserve=fuel_reserve,
        man_stage_addition=man_stage_addition,
        rocket_name=name,
        rocket_mass=rocket_mass,
    )


def get_param():
    while True:
        response = input(GREEN("\nDo you want to use a preset rocket? (y/n): ")).strip().lower()

        if response in ("y", "yes", "true"):
            return select_default()
        elif response in ("n", "no", "false"):
            return manual_entry()
        else:
            print("Please enter 'y' or 'n'.")


rocket = get_param()
