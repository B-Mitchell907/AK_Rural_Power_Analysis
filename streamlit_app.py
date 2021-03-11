from numpy import rot90
import streamlit as st
from logging import error
from streamlit.logger import setup_formatter

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# program files with calculations for energy sources.
from source_data import data_df_dict
import wind_calcs
import solar_calcs



#####################################################################
# Main Script
#####################################################################

##################################
# Page Layout
###################################
st.set_page_config(layout="wide")

col1a, col2a, col3a = st.beta_columns((1.5,1,1))

col1b, col2b, col3b = st.beta_columns((1.5,1,1))

col1c, col2c = st.beta_columns((1.5,2))


###########################
# Title
###########################
col1a.title('Alaska Rural Energy Cost Calculator')

######################################################
# Loading in DataFrame 
@st.cache
def load_data():
    fh = os.getcwd() + '\Documents\Coding-Scripts\Professional_Projects\AK_Rural_Power_Analysis\data\processed\Complete_combined_wind_solar_diesel.pkl'
    return pd.read_pickle(filepath_or_buffer=fh, compression='bz2')


data_df = load_data()

######################################################################
# Selections on which city to comapre and making dataframe for it

#extracting city list for options
city_options = list(data_df['Name'])

#Selecting Data
city_selector = col2a.selectbox(label='Select City', options=city_options)

# city dataframe
@st.cache
def selected_city_df(df: object, selected_city):
    selected_df = df.loc[df['Name'] == selected_city]
    return pd.DataFrame(data=selected_df)


selected_df = selected_city_df(data_df, selected_city=city_selector)


############################################################
# Creating drop down menu for setting interest rate
expand = col3a.beta_expander('Interest Rate for Project', expanded=False)

interest_rate = expand.select_slider(label='Precentage (%)', options=[x/10 for x in range(1,101)], value=5.0)

# Set Inflation rate as it has minimal effect of Levelised Cost of Energy Calculations.
inflation_rate = 2.0


##################################################################
#           Performing Calculations for all energy sources         
##################################################################


##################################################################
# Wind Energy Calculations and Selections
##################################################################
col2b.subheader('Wind Energy')

# selecting lifetime span of turbines for the project
turbine_lifetime = col2b.slider(
                            label='Wind Turbine Lifetime (years)', 
                            min_value=15, 
                            max_value=35, 
                            value=20, 
                            step=1
                            )

# Capcity factor for Wind turbine output
default_cap_factor = wind_calcs.default_capacity_factor(df=selected_df)

# slider for selecting capacity factor
capacity_factor = col2b.select_slider(
                            label='Output Capacity Factor (%)', 
                            options=[x for x in range(10,46)], 
                            value=default_cap_factor
                            )

# Turbine Installation Size 
est_turbine_size = wind_calcs.Turbine_size_est(selected_df, est_cap_factor=0.25) 

# Slider for manually selecting installation size
wind_installation_size = col2b.select_slider(
                                label='Total Size of Installation (kW)', 
                                options=[x*50 for x in range(1,201)], 
                                value=est_turbine_size
                                )

# Default estimate for Capital Expenditure 
default_capex = wind_calcs.est_capex_per_kw(df=selected_df)
    
# adjusting Capital expenditure to reflect construction cost based of city/village size and remoteness 
wind_adjusted_capex = wind_calcs.adjusted_capex_per_kw(default_capex=default_capex, size=wind_installation_size)

# manual slider for adjusting Capital Expenditure per kiloWatt
wind_capex_value = col2b.select_slider(
                        label='CapEx of Wind Project ($/kW)', 
                        options=[x*100 for x in range(40,301)], 
                        value=wind_adjusted_capex
                        )

# Levelised Cost of Energy 
est_wind_LCOE = wind_calcs.LCOE_per_kwh(
                        interest=interest_rate, inflation=inflation_rate, 
                        N=turbine_lifetime, capacity_factor=capacity_factor, 
                        turbine_size_kw=wind_installation_size, capex=wind_capex_value,
                        )




########################################################################
# Solar Calcs
########################################################################
col3b.subheader('Solar Energy')

# selecting 
panel_lifetime = col3b.slider(
                        label='Solar Panel Lifetime (years)', 
                        min_value=20, 
                        max_value=45, 
                        value=30, 
                        step=1,
                        )

# Extracting default Capacity factor
default_solar_cap_factor = solar_calcs.capacity_factor(df=selected_df)

# Manual slider for adjusting solar output capacity factor
est_solar_cap_factor = col3b.select_slider(
                                label='Output Capacity Factor (%)', 
                                options=[x/10 for x in range(50,201)], 
                                value=default_solar_cap_factor,
                                )

# Solar Installation Size 
est_panel_size = solar_calcs.size_est(selected_df, cap_factor=est_solar_cap_factor) 

# selecting installtion size
solar_installation_size = col3b.select_slider(
                        label='Installion Size of Panels (kW)', 
                        options=[x*100 for x in range(1,151)], 
                        value=est_panel_size,
                        )


# Capital Expenditure for Solar Project
solar_default_capex = solar_calcs.est_capex_per_kw(df=selected_df)

solar_capex_value = col3b.select_slider(
                            label='CapEx of Solar Project ($/kW)', 
                            options=[x*100 for x in range(10,151)], 
                            value=solar_default_capex,
                            )

# Annual Production of Solar 
solar_production = solar_calcs.annual_production_kwh(
                            panel_array_size=solar_installation_size, 
                            solar_cap_factor=est_solar_cap_factor,
                            )

# Solar Levelised Cost of Energy 
est_solar_LCOE = solar_calcs.LCOE_per_kwh(
                    interest=interest_rate, 
                    inflation=inflation_rate, 
                    N=panel_lifetime, 
                    solar_production= solar_production,
                    size_kw=solar_installation_size, 
                    capex=solar_capex_value,
                    )



################################################
# Diesel Calculations
################################################

diesel_cost = round(float(selected_df['diesel_cost_per_kwh']), 3)



###################################################################################
# Plotting 
#######################################################################################
col1b.header('Energy Cost Comparison')

combined_lcoe = {'Wind': est_wind_LCOE, 'Solar': est_solar_LCOE, 'Diesel':diesel_cost}

df_combined_lcoe = pd.DataFrame.from_dict(data=combined_lcoe, orient='index').rename(columns={0:'Cost per kilowatt-hour, ($/kWh)'})


fig,ax = plt.subplots()
ax = sns.barplot(
            y=df_combined_lcoe.index, 
            x=df_combined_lcoe['Cost per kilowatt-hour, ($/kWh)'], 
            palette='colorblind',
            )

ax.set(xlim=(0,4.0))


col1b.pyplot(fig)




# Table ########
table_dict = {
            'Installation Size (kW)': [wind_installation_size, solar_installation_size, '-'], 
            'Capital Expenditure ($/kW)': [wind_capex_value, solar_capex_value, '-'],
            'Energy Production Cost ($/kWh)': [round(est_wind_LCOE,3), round(est_solar_LCOE,3), diesel_cost]}

table_df = pd.DataFrame.from_dict(data=table_dict, orient='index', columns=['Wind', 'Solar', 'Diesel'])

col1c.table(table_df)




#### Adding Descripotion of Calculator and citing data sources

#st.subheader('Calculator Description')

col2c.write("*Alaska Rural Energy Cost Calculator:* \n"
    "This program does not garuntee the default estimations and approximation about each energy sources is correct for a given city/village."
)
