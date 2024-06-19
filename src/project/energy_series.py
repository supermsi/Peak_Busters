from pathlib import Path
from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# energy handler
class _BaseEnergyHandling:
    def __init__(self, filepath: Path, name: str = "power"):
        self.powerTimeSeries = pd.read_csv(filepath, header=None, names=[name])[name]

    # Create a Plotly figure using plotly express
    def plot(self):
        return go.Line(
            x=self.powerTimeSeries.index,
            y=self.powerTimeSeries.values,
            name=self.powerTimeSeries.name,
        )


# Energy handler sub-classes
class Supply(_BaseEnergyHandling):
    def __init__(self, filepath: Path, name: str = "supply"):
        super().__init__(filepath, name)
        pass


class Demand(_BaseEnergyHandling):
    def __init__(self, filepath: Path, name: str = "demand"):
        super().__init__(filepath, name)
        pass


# Supply subclasses
class PhotoVoltaic(Supply):
    def __init__(self, filepath: Path, multiplier: float):
        """
        Solar panel intake in kwh per hour

        Parameters
        ----------
        filepath: Path
            file path to file
        multiplier: float
            multiplier of the normalized series
        """
        super().__init__(filepath, name="PhotoVoltaic")
        self.multiplier = multiplier

        # overwrite
        self.powerTimeSeries = self.powerTimeSeries.mul(multiplier)


class WindTurbine(Supply):
    def __init__(self, filepath: Path, multiplier: float):
        """
        Wind turbine in kwh per hour

        Parameters
        ----------
        filepath: Path
            file path to file
        multiplier: float
            multiplier of the normalized series
        """
        super().__init__(filepath, name="WindTurbine")
        self.multiplier = multiplier

        # overwrite
        self.powerTimeSeries = self.powerTimeSeries.mul(multiplier)


# Storage classes
class Battery:
    def __init__(self, energy: pd.Series, power: pd.Series, capacity: float):
        self.energy = energy
        self.power = power
        self.capacity = capacity


class Grid:
    def __init__(self, demand: Demand, supply_list: List[Supply], battery: Battery):
        self.battery = battery
        self.demand = demand

        supply_series = pd.concat(
            [item.powerTimeSeries for item in supply_list], axis=1
        ).sum(axis=1)
        self.powerTimeSeries = demand.powerTimeSeries + supply_series + battery.power

        self.energyUse = self.powerTimeSeries.sum()
        self.peakPower = self.powerTimeSeries.max()


    def plot(self):
        return go.Line(
            x=self.powerTimeSeries.index,
            y=self.powerTimeSeries.values,
            name= "demand post improvements"
        )
    
        
