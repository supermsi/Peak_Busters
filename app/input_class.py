from viktor import File, UserError


class Inputs:
    def __init__(
        self,
        battery_capacity: float,
        solar_panel_present: bool,
        solar_panel_power: float,
        roof_area_min: float,
        roof_area_max: float,
        windturbine_present: bool,
        windturbine_type: float,
        windturbine_amount: float,
        load_profile: File,
    ):
        self.battery_capacity = battery_capacity
        self.solar_panel_present = solar_panel_present
        self.solar_panel_power = solar_panel_power
        self.roof_area_min = roof_area_min
        self.roof_area_max = roof_area_max
        self.windturbine_present = windturbine_present
        self.windturbine_type = windturbine_type
        self.windturbine_amount = windturbine_amount
        self._load_profile = load_profile

        if solar_panel_present == False:
            self.pv_output_max = 0
            self.pv_output_min = 0
        else:
            self.pv_output_min = solar_panel_power * 0.001 * roof_area_min
            self.pv_output_max = solar_panel_power * 0.001 * roof_area_max

        self.wind_output_min = 0

        if windturbine_present == False:
            self.wind_output_max = 0
        else:
            self.wind_output_max = windturbine_type * 1000 * windturbine_amount

    @classmethod
    def from_viktor_params(self, params):
        # self.check_params(params)
        return Inputs(
            battery_capacity=params.section_1.battery_capacity,
            solar_panel_present=params.section_2.solar_panel_present,
            solar_panel_power=params.section_2.solar_panel_power,
            roof_area_min=params.section_2.roof_area_min,
            roof_area_max=params.section_2.roof_area_max,
            windturbine_present=params.section_2.windturbine_present,
            windturbine_type=params.section_2.windturbine_type,
            windturbine_amount=params.section_2.windturbine_amount,
            load_profile=params.section_3.get("load_profile"),
        )

    @staticmethod
    def check_params(params):
        if params.section_1.get("battery_capacity") is None:
            raise UserError("No value was given to Battery capacity")
        if params.section_2.get("roof_area") is None:
            raise UserError("No value was given to Roof area")
        if params.section_2.get("peak_power_windturbine") is None:
            raise UserError("No value was given to peak power wind turbine")
        if params.section_3.get("load_profile") is None:
            raise UserError("No file was given to load profile")
