from pathlib import Path

import numpy as np
from scipy.optimize import OptimizeResult, minimize

from project.energy_management import EMS, Battery, PhotoVoltaic, WindTurbine
from project.energy_series import Demand, Grid
from project.temp_input import Inputs

# dictionaries of cost for costing
costPerUnitDict = {"PV": 1, "Turbine": 2, "Battery": 3, "Grid": 4}
costUpfrontDict = {"PV": 1, "Turbine": 2, "Battery": 3, "Grid": 4}


# cost the scheme
def cost(solar: PhotoVoltaic, wind: WindTurbine, battery: Battery, grid: Grid):
    """
    calculate total cost

    Parameters
    ----------
    solar : PhotoVoltaic
    wind : WindTurbine
    battery : Battery
    grid : Grid

    Returns
    -------
    total cost
    """
    _cost_PV = solar.multiplier * costPerUnitDict["PV"]
    _cost_Turbine = wind.multiplier * costPerUnitDict["Turbine"]
    _cost_Battery = battery.capacity * costPerUnitDict["Battery"]
    _cost_Grid = (
        grid.energyUse * costPerUnitDict["Grid"]
        + grid.peakPower * costUpfrontDict["Grid"]
    )

    total_cost = sum([_cost_PV, _cost_Turbine, _cost_Battery, _cost_Grid])  #

    return total_cost


# optimise the cost through options
def optimis_cost(bounds: Inputs) -> OptimizeResult:
    """
    Optimize cost by updating multiplier

    Parameters
    ----------
    bounds: Inputs

    Returns
    -------
    OptimizeResult
    """

    # Define the function to minimize
    def optimize_function(x):
        # define local power inputs
        # pv = PhotoVoltaic(filepath=Path("Input_files/PV_data_normalized.csv"), multiplier=x[0])
        # turbine = WindTurbine(filepath=Path("Input_files/Wind_data_normalized.csv"), multiplier=x[1])
        project_path = Path(__file__).parent.parent.parent
        print(project_path)
        pv = PhotoVoltaic(
            filepath=project_path / "Input_files" / "PV_data_normalized.csv",
            multiplier=x[0],
        )
        turbine = WindTurbine(
            filepath=project_path / "Input_files" / "Wind_data_normalized.csv",
            multiplier=x[1],
        )

        # run EMS to define battery and grid

        load = Demand(Path("Input_files/Load_data.csv"))
        battery = EMS(pv, turbine, load).get_battery()
        supply_list = [pv, turbine]
        grid = Grid(load, supply_list, battery)
        # calculate and return cost
        total_cost = cost(pv, turbine, battery, grid)
        return total_cost

    # Initial guess for the minimum
    x0 = np.array([bounds.PV_output_max, bounds.wind_output_max])

    # Define the bounds for the variables (range)
    _bounds = (
        (bounds.PV_output_min, bounds.PV_output_min),
        (bounds.wind_output_min, bounds.wind_output_max),
    )  # Bounds for x and y variables

    # Minimize the function using the 'L-BFGS-B' method
    result = minimize(optimize_function, x0, method="L-BFGS-B", bounds=_bounds)

    return result
