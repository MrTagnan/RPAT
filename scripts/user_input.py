import json
import os
from dataclasses import dataclass
from typing import List

from config import CUSTOM_ROCKETS_PATH, DEFAULT_ROCKETS_PATH, DEBUG_MODE
from scripts.ansi import *


@dataclass
class Rocket:
    name: str
    stages: int
    isp: List[float]
    dry_mass: List[float]
    wet_mass: List[float]
    dry_mass_adj: List[float]
    fuel_reserve: List[float]
    rocket_name: str
    rocket_mass: float




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
                print(RED(f"[Warning] Custom rocket '{name}' conflicts with a default entry and will be skipped."))
                print(GREEN("To fix this, please rename the rocket to something non-conflicting"))
            else:
                rockets[name] = data

    return rockets

def isolate_stage_masses(dry_mass, wet_mass):
    isolated_dry = []
    isolated_wet = []

    for i in range(len(wet_mass) - 1):
        isolated_wet.append(wet_mass[i] - wet_mass[i + 1])
        isolated_dry.append(dry_mass[i] - wet_mass[i + 1])

    isolated_wet.append(wet_mass[-1])
    isolated_dry.append(dry_mass[-1])

    return isolated_dry, isolated_wet


def add_reserves(stages, fuel_reserve, dry_mass, wet_mass):
    dry_mass_adj = []

    for i in range(stages):
        reserve = fuel_reserve[i]
        prop_mass = wet_mass[i] - dry_mass[i]

        if reserve > prop_mass:
            print(RED("Fuel reserves are set up incorrectly, resetting"))
            reserve = 0

        if reserve > 0:
            dry_mass_adj.append(dry_mass[i] + reserve)
        else:
            dry_mass_adj.append(dry_mass[i])

    return dry_mass_adj

def booster_stage_calc(booster_dry_mass, booster_wet_mass, booster_count, booster_thrust, 
                       booster_isp, main_stage_thrust, main_stage_isp, wet_mass, dry_mass, booster_burn_time):
    
    booster_dry_sum = booster_dry_mass * booster_count
    booster_wet_sum = booster_wet_mass * booster_count
    booster_thrust_sum = booster_thrust * booster_count

    #average the ISP weighted by the thrust of each component to get the effective ISP of the combined system
    effective_isp = (booster_thrust_sum + main_stage_thrust) / ((main_stage_thrust / main_stage_isp) + (booster_thrust_sum / booster_isp))
    
    g0 = 9.80665 #m/s^2
    core_mass_flow = (main_stage_thrust * 1000) / (main_stage_isp * g0) #json data is in kN, so multiply by 1000 to get N
    core_mass_used = core_mass_flow * booster_burn_time  

    booster_stage_wet = booster_wet_sum + core_mass_used
    booster_stage_dry = booster_dry_sum
    
    core_stage_wet = wet_mass[0] - core_mass_used
    core_stage_dry = dry_mass[0]

    core_prop_available = wet_mass[0] - dry_mass[0]

    if core_mass_used >= core_prop_available:
        raise ValueError("Booster burn consumes all first-stage core propellant.")

    if DEBUG_MODE:
        print(YELLOW("Booster Stage Calculation:\n"))
        print(f"Effective ISP: {effective_isp:.2f}s\n")
        print(f"Booster Dry Mass: {booster_dry_mass:.2f} kg")
        print(f"Booster Wet Mass: {booster_wet_mass:.2f} kg\n")
        print(f"Booster Count: {booster_count}")
        print(f"Booster Dry Mass Sum: {booster_dry_sum:.2f} kg")
        print(f"Booster Wet Mass Sum: {booster_wet_sum:.2f} kg\n")
        print(f"Core Mass Flow: {core_mass_flow:.2f} kg/s")
        print(f"Core Mass Used: {core_mass_used:.2f} kg\n")
        print(f"Booster Stage Wet Mass: {booster_stage_wet:.2f} kg")
        print(f"Booster Stage Dry Mass: {booster_stage_dry:.2f} kg\n")
        print(f"Core Stage Wet Mass: {core_stage_wet:.2f} kg")
        print(f"Core Stage Dry Mass: {core_stage_dry:.2f} kg\n")

    return effective_isp, booster_stage_wet, booster_stage_dry, core_stage_wet, core_stage_dry

def apply_booster_stage(
    stages, isp, dry_mass_adj, dry_mass, wet_mass, fuel_reserve,
    booster_dry_mass, booster_wet_mass, booster_count, booster_thrust,
    booster_isp, booster_burn_time, main_stage_thrust,
):
    if DEBUG_MODE:
        print(YELLOW("Booster application results:\n"))
        print(f"Previous wet masses: {[round(elem, 2) for elem in wet_mass]} kg")
        print(f"Previous dry masses: {[round(elem, 2) for elem in dry_mass_adj]} kg")
        print(f"Previous ISPs: {[round(elem, 2) for elem in isp]}s\n")
    
    effective_isp, booster_stage_wet, booster_stage_dry, core_stage_wet, core_stage_dry = booster_stage_calc(
        booster_dry_mass, booster_wet_mass, booster_count,
        booster_thrust, booster_isp, main_stage_thrust,
        isp[0], wet_mass, dry_mass, booster_burn_time,
    )


    return {
        "stages": stages + 1,
        "isp": [effective_isp, *isp],
        "dry_mass": [booster_stage_dry, core_stage_dry, *dry_mass[1:]],
        "dry_mass_adj": [booster_stage_dry, dry_mass_adj[0], *dry_mass_adj[1:]],    
        "wet_mass": [booster_stage_wet, core_stage_wet, *wet_mass[1:]],
        "fuel_reserve": [0, *fuel_reserve],
        
    }


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
    
    stages = rocket_data["stages"]
    isp = rocket_data["isp"]
    fuel_reserve = rocket_data.get("fuel_reserve", [0] * stages)

    manual_stage_addition = rocket_data.get("manStage", rocket_data.get("man_stage_add", False))
    
    dry_mass = rocket_data["dryMass"]
    wet_mass = rocket_data["wetMass"]

    if manual_stage_addition:
        dry_mass, wet_mass = isolate_stage_masses(dry_mass, wet_mass)
        if DEBUG_MODE:
            print("Manual stage addition is enabled, adjusting dry and wet masses accordingly.\n")
            print(f"Previous dry masses: {rocket_data['dryMass']} kg")
            print(f"Previous wet masses: {rocket_data['wetMass']} kg\n")
            print(f"Adjusted dry masses: {dry_mass} kg")
            print(f"Adjusted wet masses: {wet_mass} kg\n")

    dry_mass_adj = add_reserves( rocket_data["stages"], fuel_reserve, dry_mass, wet_mass, )
    
    rocket_mass = sum(wet_mass)  # Total wet mass of the rocket.
    
    booster_count = rocket_data.get("booster_count", 0)
    if booster_count > 0:
        required_booster_fields = [
            "booster_dry_mass",
            "booster_wet_mass",
            "booster_isp",
            "booster_burn_time",
            "main_stage_thrust",
            "booster_thrust",
        ]

        missing_fields = [
            field for field in required_booster_fields
            if field not in rocket_data
        ]

        if missing_fields:
            print(RED(f"Invalid booster data. Missing: {', '.join(missing_fields)}"))
            return None

        booster_result = apply_booster_stage(
            stages, isp, dry_mass_adj, dry_mass, 
            wet_mass, fuel_reserve,
            rocket_data["booster_dry_mass"],
            rocket_data["booster_wet_mass"],
            booster_count,
            rocket_data["booster_thrust"],
            rocket_data["booster_isp"],
            rocket_data["booster_burn_time"],
            rocket_data["main_stage_thrust"],
        )

        stages = booster_result["stages"]
        isp = booster_result["isp"]
        dry_mass = booster_result["dry_mass"]
        dry_mass_adj = booster_result["dry_mass_adj"]
        wet_mass = booster_result["wet_mass"]
        fuel_reserve = booster_result["fuel_reserve"]
        rocket_mass = rocket_mass + rocket_data["booster_wet_mass"] * booster_count

        if DEBUG_MODE:
            print(f"Updated ISPs: {[round(elem, 2) for elem in isp]}s")
            print(f"Updated wet masses: {[round(elem, 2) for elem in wet_mass]} kg")
            print(f"Updated dry masses: {[round(elem, 2) for elem in dry_mass_adj]} kg\n")



    print(f"{GREEN('Selected rocket:')} {GRAY(rocket_data['desc'])}")

    return Rocket(
        name=key,
        stages=stages,
        isp=isp,
        dry_mass=dry_mass,
        wet_mass=wet_mass,
        dry_mass_adj=dry_mass_adj,
        fuel_reserve=fuel_reserve,
        rocket_name=rocket_data["desc"],
        rocket_mass=rocket_mass,
    )

#very broken and very out of date, but leaving it here for now in case I want to fix it later
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
    dry_mass_adj, wet_mass = add_reserves(stages, fuel_reserve, dry_mass, wet_mass)
    rocket_mass = total_mass(man_stage_addition, wet_mass)

    return Rocket(
        name=name,
        stages=stages,
        isp=isp,
        dry_mass=dry_mass,
        wet_mass=wet_mass,
        dry_mass_adj=dry_mass_adj,
        fuel_reserve=fuel_reserve,
        rocket_name=name,
        rocket_mass=rocket_mass,
    )


def get_param():
    while True:
        response = input(GREEN("\nDo you want to use a preset rocket? (y/n): ")).strip().lower()

        if response in ("y", "yes", "true"):
            return select_default()
        elif response in ("n", "no", "false"):
            print(RED("Manual rocket entry is currently disabled. Please use a preset rocket."))
            continue
        else:
            print("Please enter 'y' or 'n'.")


rocket = get_param()
