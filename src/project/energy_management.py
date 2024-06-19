from typing import Tuple

import numpy as np
import pandas as pd

from src.project.energy_series import Battery, Demand, PhotoVoltaic, WindTurbine


class EMS:
    def __init__(
        self,
        solar: PhotoVoltaic,
        wind: WindTurbine,
        load: Demand,
        capacity: float = 5000,
    ):
        """
        EMS??

        Parameters
        ----------
        solar: PhotoVoltaic
        wind: WindTurbine
        load: Demand
        capacity: float
            default is 5000 kwh
        """
        self.batterySize = capacity  # kwh

        self.PhotoVoltaic = solar
        self.Wind = wind
        self.Load = load

        # init empy series
        self.batteryPower = pd.Series(
            [0] * len(solar.powerTimeSeries), name="batteryPower"
        )
        self.batteryEnergy = pd.Series(
            [0] * len(solar.powerTimeSeries), name="batteryEnergy"
        )

        self.calculate_battery_energy()

        # self.CalcBatteryPower(PV, Wind, Load)
        # print(self.batteryPower, self.batteryEnergy)
        # self.batteryPower.to_csv('batterypower',index=False)

    def _calculate_battery_energy(
        self, power: float, SOC: float
    ) -> Tuple[float, float]:
        energy = power  # energy is power as it is power in one hour
        currentSOC = SOC

        battery_power = np.nan
        newSOC = np.nan

        # situation normal, enough SOC to either drain or fill battery
        if self.batterySize >= currentSOC + energy >= 0:
            newSOC = currentSOC + energy
            battery_power = power

        # Situation battery capacity not able to fully obtain surplus but only partially
        elif currentSOC < self.batterySize < currentSOC + energy:
            newSOC = self.batterySize

            leftover_energy = currentSOC + energy - self.batterySize
            battery_energy = energy - leftover_energy
            battery_power = battery_energy

        # situation battery not able to generate all energy requested but only partially
        elif currentSOC > 0 > currentSOC + energy:
            newSOC = 0

            leftover_energy = currentSOC + energy
            battery_energy = energy - leftover_energy
            battery_power = battery_energy

        # Situation battery full and energy surplus available
        elif currentSOC >= self.batterySize and energy >= 0:
            newSOC = self.batterySize
            battery_power = 0

        # situation battery empty and energy demand
        elif currentSOC <= 0 and energy < 0:
            newSOC = 0
            battery_power = 0

        return battery_power, newSOC

    def calculate_battery_energy(self) -> None:
        desired_battery_power = (
            self.PhotoVoltaic.powerTimeSeries
            + self.Wind.powerTimeSeries
            + self.Load.powerTimeSeries
        )
        # desired_battery_power.to_csv('Desired_batterypower',index=False)
        # print(PV.powerTimeSeries)
        # print(Wind.powerTimeSeries)
        # print(Load.powerTimeSeries)
        # print(desired_battery_power.size)

        for i in range(desired_battery_power.size):
            if i == 0:
                batteryPower, newSOC = self._calculate_battery_energy(
                    desired_battery_power[i], 0
                )
            else:
                batteryPower, newSOC = self._calculate_battery_energy(
                    desired_battery_power[i], self.batteryEnergy[i - 1]
                )

            self.batteryPower[i] = batteryPower
            self.batteryEnergy[i] = newSOC

    def get_battery(self) -> Battery:
        return Battery(self.batteryEnergy, self.batteryPower, capacity=self.batterySize)
