from pathlib import Path

import matplotlib.pyplot as plt

from project.costing import cost, optimis_cost
from project.energy_management import EMS
from project.energy_series import Demand, Grid, PhotoVoltaic, WindTurbine

PV = PhotoVoltaic(filepath=Path("Input_files/PV_data_normalized.csv"), multiplier=2000)
Wind = WindTurbine(
    filepath=Path("Input_files/Wind_data_normalized.csv"), multiplier=2000
)
Load = Demand(Path("Input_files/Load_data.csv"))

battery = EMS(PV, Wind, Load).get_battery()

grid = Grid(demand=Load, supply_list=[Wind, PV], battery=battery)

cost(PV, Wind, battery, grid)


fig, axes = plt.subplots(4, 1, sharex=True, figsize=(15, 15))

for i, series in enumerate([PV, Wind, Load]):
    series.powerTimeSeries.plot(ax=axes[i], legend=True)

battery.power.plot(ax=axes[-1], legend=True)
battery.energy.plot(ax=axes[-1], legend=True)

plt.savefig("tmp.png")


bounds = Inputs()
optimis_cost(bounds)
