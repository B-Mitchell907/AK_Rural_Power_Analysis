from logging import error
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from source_data import data_df_dict
from streamlit.logger import setup_formatter
import seaborn as sns



########## Loading Data into Streamlit ############

#@st.cache
# def load_data():
    #fh = os.path('Users\mitch\Documents\Coding-Scripts\Professional_Projects\AK_Rural_Power_Analysis\data\processed\combined_wind_solar_diesel.pkl')
    #return pd.read_pickle(filepath_or_buffer=fh , compression='bz2')


#### Looking creating calculations for wind power cost: includes size, capacity factor, wind class suggestion,



###Main Script
st.set_page_config(layout="wide")
col1a, col2a = st.beta_columns((1,1))


#Title
col1a.title('Alaska Rural Energy Calculator')


#Loading in DataFrame ###################################################

#data_df = pd.read_csv(filepath_or_buffer=os.path.commonpath('TabSep_Complete_combined_wind_solar_diesel.tsv'), sep='\t')

data_df = pd.DataFrame.from_dict(data=data_df_dict)

#extracting city list for options
city_options = list(data_df['Name'])

#Selecting Data
city_selector = col2a.selectbox(label='Select City', options=city_options)

#Display DataFrame
@st.cache
def selected_city_df(df: object, selected_city):
    selected_df = df.loc[df['Name'] == selected_city]
    return pd.DataFrame(data=selected_df)

selected_df = selected_city_df(data_df, selected_city=city_selector)




# Dividing up columns For displaying data
col1, col2, col3 = st.beta_columns((2,1,1))

col1b, col2b = st.beta_columns((1,1))





# Creating drop down menu for setting interest and inflation rate
expand = col2b.beta_expander('Interest Rate for Project', expanded=False)

interest_rate = expand.select_slider(label='Precentage (%)', options=[x/10 for x in range(1,201)], value=5.0)
#inflation_rate = expand.select_slider(label='Inflation Rate (%)', options=[x/10 for x in range(0,101)], value=2.0)
inflation_rate = 2.0




col1.header('Energy Cost Comparison')

##### Performing calculations ####









######################################################################
### Wind Calcs
######################################################################## 
col2.subheader('Wind Energy')

#
turbine_lifetime = col2.slider(label='Wind Turbine Lifetime (years)', min_value=15, max_value=35, value=20, step=1)


def default_capacity_factor(df) -> float:
    wind_class = df['wpc'].item()
    wpc_to_cap_factor = {7:32, 6:29, 5:26, 4:23, 3:21, 2:18, 1:15}
    return wpc_to_cap_factor[wind_class]


default_cap_factor = default_capacity_factor(df=selected_df)
capacity_factor = col2.select_slider(label='Output Capacity Factor (%)', options=[x for x in range(10,46)], value=default_cap_factor)


# Turbine Installation Size ###############################################
def Turbine_size_est(df, est_cap_factor):
    total_kwh = df['total_kwh_sold'].item()
    est_size = total_kwh * 0.3 / (8760 * est_cap_factor)
    return round(est_size, -2)


est_turbine_size = Turbine_size_est(selected_df, est_cap_factor=0.25) 

wind_installation_size = col2.select_slider('Total Size of Installation (kW)', options=[x*100 for x in range(1,101)], value=est_turbine_size)


# Capital Expenditure #############################################

def Wind_est_capex_per_kw(df):
    pce_cost = df['pce_rate'].item()
    if pce_cost == 0 or pce_cost == 'nan':
        capex = 4000
    elif pce_cost >= 0.75:
        capex = 30000
    else:
        capex = 4000 + pce_cost * 34666
    return round(capex, -2)


default_capex = Wind_est_capex_per_kw(df=selected_df)


def wind_adjusted_capex_per_kw(default_capex, size):
    coef_dict = {100:0.07634832, 200:0.05886931, 500:0.03408415, 1000:-0.02408789, 2000:-0.24361946}
    if size >= 2000:
        adjusted_cap = default_capex * (1 + coef_dict[2000])
    elif size >= 1000:
        adjusted_cap = default_capex * (1 + coef_dict[1000])
    elif size >=  500:
        adjusted_cap = default_capex * (1 + coef_dict[500])
    elif size >= 200:
        adjusted_cap = default_capex * (1 + coef_dict[200]) 
    elif size >= 100:
        adjusted_cap = default_capex * (1 + coef_dict[100])
    return round(adjusted_cap, -2)
    

wind_adjusted_capex = wind_adjusted_capex_per_kw(default_capex=default_capex, size=wind_installation_size)

wind_capex_value = col2.select_slider(label='CapEx of Wind Project ($/kw)', 
                                        options=[x*100 for x in range(40,301)], 
                                        value=wind_adjusted_capex)


# Wind Levelised Cost of Energy #############################################

def Wind_LCOE_per_kwh(interest, inflation, N, capacity_factor, turbine_size_kw, capex):
    operating_maintence = 0.036
    r = interest / 100
    i = inflation / 100
    cap_fac = capacity_factor / 100

    capital_recovery_factor = r / (1-(1+r)**(-N))
    net_present_value = (capex * turbine_size_kw) + sum([( (1+i) / (1+r) )**x for x in range(1,N+1)]) * operating_maintence
    annual_production_kwh = turbine_size_kw * cap_fac * 8760
    LCOE = (net_present_value * capital_recovery_factor) / annual_production_kwh   
    return round(LCOE, 3)



est_wind_LCOE = Wind_LCOE_per_kwh(
                        interest=interest_rate, inflation=inflation_rate, 
                        N=turbine_lifetime, capacity_factor=capacity_factor, 
                        turbine_size_kw=wind_installation_size, capex=wind_capex_value)






########################################################################
# Solar Calcs
########################################################################
#  
col3.subheader('Solar Energy')

panel_lifetime = col3.slider(label='Solar Panel Lifetime (years)', min_value=20, max_value=45, value=30, step=1)



def solar_capacity_factor(df):
    ac_annual_kwh = df['solar_ac_annual_1kw']
    capacity_factor = ac_annual_kwh / 8760
    return round(capacity_factor * 100, -1).item()


default_solar_cap_factor = solar_capacity_factor(df=selected_df)

est_solar_cap_factor = col3.select_slider(label='Output Capacity Factor (%)', 
                                options=[x/10 for x in range(50,201)], 
                                value=default_solar_cap_factor,
                                )


# Solar Installation Size ####################################################################################

def solar_size_est(df, cap_factor):
    total_kwh = df['total_kwh_sold'].item()
    decimal_cap = cap_factor / 100
    est_size = total_kwh * 0.2 / (decimal_cap * 8760)    #solar_ac_annual_1kw is a measuremnt of kwh 
    return int(round(est_size, -2))


est_panel_size = solar_size_est(selected_df, cap_factor=est_solar_cap_factor) 


solar_installation_size = col3.select_slider(
                        label='Installion Size of Panels, (kW)', 
                        options=[x*100 for x in range(1,101)], 
                        value=est_panel_size)


# Capital Expenditure ####################################################################

def solar_est_capex_per_kw(df, lowest_capex, highest_capex):
    pce_cost = df['pce_rate'].item()
    kw_coef = (highest_capex - lowest_capex) / 0.75
    if pce_cost == 0 or pce_cost == 'nan':
        capex = lowest_capex
    elif pce_cost >= 0.75:
        capex = lowest_capex
    else:
        capex = 1500 + pce_cost * kw_coef
    return round(capex, -2)


solar_default_capex = solar_est_capex_per_kw(df=selected_df, lowest_capex=3000, highest_capex=13500)

solar_capex_value = col3.select_slider(
                label='CapEx of Solar Project ($/kW)', 
                options=[x*100 for x in range(10,150)], 
                value=solar_default_capex)



# Annual Production of Solar #############################

def solar_annual_production(panel_array_size, solar_cap_factor):
    decimal_cap = solar_cap_factor / 100
    production_kwh = decimal_cap * 8760 * panel_array_size
    return production_kwh


solar_production = solar_annual_production(
                    panel_array_size=solar_installation_size, 
                    solar_cap_factor=est_solar_cap_factor)



# Solar Levelised Cost of Energy ###########################################################

def Solar_LCOE_per_kwh(interest, inflation, N, solar_production, size_kw, capex):
    operating_maintence = 45 * size_kw
    r = interest / 100
    i = inflation / 100

    capital_recovery_factor = r / (1-(1+r)**(-N))  
    net_present_value = (capex * size_kw) + sum([( (1+i) / (1+r) )**x for x in range(1,N+1)]) + operating_maintence 
    annual_production_kwh = solar_production
    lcoe = (net_present_value * capital_recovery_factor) / annual_production_kwh         
    return round(lcoe, 3)


est_solar_LCOE = float(Solar_LCOE_per_kwh(
                    interest=interest_rate, 
                    inflation=inflation_rate, 
                    N=panel_lifetime, 
                    solar_production= solar_production,
                    size_kw=solar_installation_size, 
                    capex=solar_capex_value))










####################################################################################
# Plotting
#######################################################################################



diesel_cost = round(float(selected_df['diesel_cost_per_kwh']), 3)

combined_lcoe = {'Wind': est_wind_LCOE, 'Solar': est_solar_LCOE, 'Diesel':diesel_cost}

df_combined_lcoe = pd.DataFrame.from_dict(data=combined_lcoe, orient='index').rename(columns={0:'Cost per kilowatt-hour, ($/kWh)'})

#col3.bar_chart(df_combined_lcoe)

fig,ax = plt.subplots()
ax = sns.barplot(
            y=df_combined_lcoe.index, 
            x=df_combined_lcoe['Cost per kilowatt-hour, ($/kWh)'], 
            palette='colorblind',
            )

col1.pyplot(fig)




# Table ########
table_dict = {
            'Installation Size (kW)': [wind_installation_size, solar_installation_size, '-'], 
            'Capital Expenditure ($/kW)': [wind_capex_value, solar_capex_value, '-'],
            'Energy Production Cost ($/kWh)': [round(est_wind_LCOE,3), round(est_solar_LCOE,3), diesel_cost]}

table_df = pd.DataFrame.from_dict(data=table_dict, orient='index', columns=['Wind', 'Solar', 'Diesel'])

col1b.table(table_df)







#### Adding Descripotion of Calculator and citing data sources

st.subheader('Calculator Description')
st.text(
    "This is a test for commiting verison to different branches. \n"
    "C:\Users\mitch\Documents\Coding-Scripts\Professional_Projects\AK_Rural_Power_Analysis\streamlit_app.py"
)