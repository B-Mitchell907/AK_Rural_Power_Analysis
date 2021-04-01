import pandas as pd
import numpy as np

# determining a default capcity factor for a wind turbine for any given city based of wind power class
#### actual results will vary
def default_capacity_factor(df) -> float:
    wind_power_class = df['wpc'].item()
    wpc_to_cap_factor = {7:32, 6:29, 5:26, 4:22, 3:18, 2:14, 1:8}
    return wpc_to_cap_factor[wind_power_class]



# estimating size for a wind turbine installtion based of total amount of power consumed in city/grid
### using 30% of overall use. value is near median for other state projects.
def Turbine_size_est(df, est_cap_factor):
    total_kwh = df['total_kwh_sold'].item()
    est_size = total_kwh * 0.3 / (8760 * est_cap_factor)
    rounded_size = int(round(est_size, -2))
    
    # adjusting for round to zero error
    if rounded_size == 0:
        rounded_size = 50
    return int(rounded_size)


# estimating Capital Expenditure for a given city/village project.
## estimates are dervied from PCE (Power Cost Equalizer) rate.
## this can represent how costly it is to produce power in given city.
#### A Correlation between PCE rate and CapEx is used for estimation.   
def est_capex_per_kw(df,low_capex, high_capex):
    pce_cost = df['pce_rate'].item()
    if pce_cost == 0 or pce_cost == 'nan':
        capex = low_capex
    elif pce_cost >= 0.75:
        capex = high_capex
    else:
        diff = high_capex-low_capex
        capex = low_capex + pce_cost * diff
    return round(capex, -2)



# Adjusting CapEx relativie to size of turbine installation.
## Coefficents are taking from a Logistic Regression of past projects with respect to CapEx vs Installation size
def adjusted_capex_per_kw(default_capex, size):
    turbine_kw_installation = {50:29815, 100:20680, 500:9705, 1000:7319, 2000:5676, 5000:4236}
    x = np.array(turbine_kw_installation.keys)
    y = np.array(turbine_kw_installation.values)
    z = np.polyfit(x,y,deg=2)
    p = np.poly1d(z)

    if size > 1500:
        adjusted_cap = default_capex * ((turbine_kw_installation[5000] - turbine_kw_installation[2000]) / (5000-2000))
    else:
        adjusted_cap = p(size)
    return round(adjusted_cap, -2)



# calculating Levelized Cost Of Energy per kiloWatt-hour
def LCOE_per_kwh(interest, N, capacity_factor, turbine_size_kw, capex):
    #changing turbine size for cities if turnbine_size_kw == 0
    if turbine_size_kw == 0:
        turbine_size_kw = 50
    else:
        turbine_size_kw = turbine_size_kw    
    
    operating_maintence = 0.036   #dollars per kwh
    r = interest / 100
    cap_fac = capacity_factor / 100

    annaul_capex = capex * r * (1+r)**N / ((1+r)**N - 1)

    

    return round(lcoe, 3)




