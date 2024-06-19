from pathlib import Path
import pandas as pd

import plotly.graph_objects as go
from viktor import UserError, ViktorController
import plotly.graph_objects as go
from viktor.parametrization import (
    AnalyseButton,
    FileField,
    LineBreak,
    Lookup,
    NumberField,
    OptionField,
    OptionListElement,
    Section,
    ToggleButton,
    ViktorParametrization,
    OutputField,
    Text
)
from viktor.views import DataGroup, DataResult, DataView, PlotlyResult, PlotlyView, PDFView, PDFResult, ImageView, ImageResult

from .input_class import Inputs


from src.project.energy_series import Demand, PhotoVoltaic, WindTurbine, Grid
from src.project.energy_management import EMS


### Lists ###
solar_panel_list = [
    OptionListElement(label="Panel 1 - 200W", value=200),
    OptionListElement(label="Panel 2 - 300W", value=300),
    OptionListElement(label="Panel 3 - 400W", value=400),
]

windturbine_list = [
    OptionListElement(label="Turbine 1 - 2MW", value=2),
    OptionListElement(label="Turbine 2 - 5MW", value=5),
    OptionListElement(label="Turbine 3 - 8MW", value=8),
]
### output functions 
def peak_solar_wattage(params, **kwargs):
    return round(params.section_2.roof_area_max * params.section_2.solar_panel_power * 0.001, 1)

def peak_turbine_wattage(params, **kwargs):
    return round(params.section_2.windturbine_type * params.section_2.windturbine_amount * 1000, 1)

class Parametrization(ViktorParametrization):
    section_1 = Section("Battery input")
    section_1.battery_text = Text(
        """
## Battery
Use this section to define the maximum capacity of the battery. 
"""
    )
    section_1.battery_capacity = NumberField(
        "Maximum battery capacity",
        suffix="kWh",
        min=10,
        max=100000,
        num_decimals=0,
        variant="slider",
        default = 1000,
        step = 10
    )


    section_2 = Section("Sustainable energy sources")
    section_2.pv_text = Text(
        """
## Solar Array
Use this section to add the available solar array
Select the efficiency of the solar panels available to you.
Choose how many solar panels you would like, this is dependent on the area you have available. 
"""
    )
    section_2.solar_panel_present = ToggleButton("Solarpanels", flex=20)
    section_2.solar_panel_power = OptionField(
        "Wpeak of solar panels",
        options=solar_panel_list,
        visible=Lookup("section_2.solar_panel_present"),
        default = 200
    )
    section_2.lb1 = LineBreak()

    section_2.roof_area_min = NumberField(
        "Minimal roof area",
        suffix="m^2",
        min=0,
        max=500,
        variant="slider",
        visible=Lookup("section_2.solar_panel_present"),
        flex=50,
        default = 0
    )
    section_2.roof_area_max = NumberField(
        "Maximum roof area",
        suffix="m^2",
        min=0,
        max=10000,
        num_decimals=0,
        variant="slider",
        visible=Lookup("section_2.solar_panel_present"),
        flex=50,
        default = 1000,
        step = 100
    )
    section_2.roof_output = OutputField(
        "Watt peak of Solar Array",
        value = peak_solar_wattage,
        visible=Lookup("section_2.solar_panel_present"),
        suffix = "Kw"
    )
    section_2.lb2 = LineBreak()
    section_2.turbine_text = Text(
        """
## Wind Turbine Array
Use this section to add the available wind turbine array
Select the size of the wind turbines available to you.
Choose how many wind turbines you would like, this is dependent on the area you have available. 
"""
    )

    section_2.windturbine_present = ToggleButton("Windturbines", flex=20)
    section_2.windturbine_type = OptionField(
        "Windturbine type",
        options=windturbine_list,
        visible=Lookup("section_2.windturbine_present"),
        default = 2
    )
    section_2.lb3 = LineBreak()
    section_2.windturbine_amount = NumberField(
        "Amount of windturbine",
        suffix="-",
        min=0,
        max=30,
        num_decimals=0,
        variant="slider",
        visible=Lookup("section_2.windturbine_present"),
        flex=50,
        default = 5
    )
    section_2.lb3a = LineBreak()
    section_2.turbine_output = OutputField(
        "Watt peak of Wind Turbine Array",
        value = peak_turbine_wattage,
        visible=Lookup("section_2.windturbine_present"),
        suffix = "Kw"
    )

    section_3 = Section("Load Profile")
    section_3.load_text = Text(
        """
## Load 
Use this section to upload your companies load profile. 
"""
)
    section_3.load_profile = FileField("Upload .csv file")

class Controller(ViktorController):
    label = "My Entity Type"
    parametrization = Parametrization

    def analyse_button_method_1(self, params, **kwargs):
        model = self.build_model_based_on_params(params)

        if params.section_3.get("load_profile") is None:
            raise UserError("No file was given to load profile")
        if model.roof_area_min > model.roof_area_max:
            raise UserError("Minimal roof area is bigger than maximum roof area")

        # print(f'Battery capacity is {model.battery_capacity}')
        # print(model.solar_panel_present)
        # print(model.pv_output_max)
        # print(model.pv_output_min)

        # print(model.wind_output_max)
        # print(model.wind_output_min)
        return

    @staticmethod
    def build_model_based_on_params(params):
        return Inputs.from_viktor_params(params)
    
    @PDFView("Welcome", duration_guess=1)
    def show_pdf(self, **kwargs):
        project_path = Path(__file__).parent.parent
        filepath=project_path / "docs"/ "_static" / "image" / "peak_busters.pdf"

        return PDFResult.from_path(filepath)
    
    @PlotlyView("Sustainable energy contribution", duration_guess=1)
    def get_plotly_view_1(self, params, **kwargs):
        model = self.build_model_based_on_params(params)

        project_path = Path(__file__).parent.parent
        print(project_path)
        pv = PhotoVoltaic(filepath=project_path / "Input_files" / "PV_data_normalized.csv", multiplier=model.pv_output_max)
        turbine = WindTurbine(filepath=project_path / "Input_files"/ "Wind_data_normalized.csv", multiplier=model.wind_output_max)

        fig = go.Figure()
        fig.add_trace(pv.plot())
        fig.add_trace(turbine.plot())

        return PlotlyResult(fig.to_json())

    
    @PlotlyView("Grid load before and after", duration_guess=1)
    def get_plotly_view_2(self, params, **kwargs):
        model = self.build_model_based_on_params(params)

        project_path = Path(__file__).parent.parent
        pv = PhotoVoltaic(filepath=project_path / "Input_files" / "PV_data_normalized.csv", multiplier=model.pv_output_max)
        turbine = WindTurbine(filepath=project_path / "Input_files"/ "Wind_data_normalized.csv", multiplier=model.wind_output_max)
        load = Demand(project_path / "Input_files/Load_data.csv")
        battery = EMS(pv, turbine, load, capacity = params.section_1.battery_capacity).get_battery()
        supply_list = [pv, turbine]
        grid = Grid(load, supply_list, battery)


        fig = go.Figure()
        fig.add_trace(load.plot())
        fig.add_trace(grid.plot())

        return PlotlyResult(fig.to_json())

    


    @ImageView("Battery charging", duration_guess=1)
    def create_img_result(self, params, **kwargs):
        image_path = Path(__file__).parent.parent / "docs"/ "_static"/ "image"/ "series.png"
        return ImageResult.from_path(image_path)