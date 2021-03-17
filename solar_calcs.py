import pandas as pd


# determing solar caparcity factor for location
### Estimates were etracted from NREL PVWatts calculator.
def capacity_factor(df):
    ac_annual_kwh = df['solar_ac_annual_1kw']
    capacity_factor = ac_annual_kwh / 8760
    return round(capacity_factor * 100, -1).item()
    sdf


# Estimating size of solar 
### using 30% of overall use. value is near median for other state projects.
def size_est(df, cap_factor):
    total_kwh = df['total_kwh_sold'].item()
    decimal_cap = cap_factor / 100
    est_size = total_kwh * 0.3 / (decimal_cap * 8760)    #solar_ac_annual_1kw is a measuremnt of kwh 
    return int(round(est_size, -2))


# Estimating Capital Expediture for a city project.
## estimates are dervied from PCE (Power Cost Equalizer) rate.
## this can represent how costly it is to produce power in given city.
#### A Correlation between PCE rate and CapEx is used for estimation.
def est_capex_per_kw(df, lowest_capex, highest_capex):
    pce_cost = df['pce_rate'].item()
    kw_coef = (highest_capex - lowest_capex) / 0.75
    if pce_cost == 0 or pce_cost == 'nan':
        capex = lowest_capex
    elif pce_cost >= 0.75:
        capex = highest_capex
    else:
        capex = lowest_capex + (pce_cost * kw_coef)
    return int(round(capex, -2))


    ###  Need to fix coefficient for adjusting solar array size by
def adjusting_capex():
    pass



# 
def annual_production_kwh(panel_array_size, solar_cap_factor):
    decimal_cap = solar_cap_factor / 100
    production_kwh = decimal_cap * 8760 * panel_array_size
    return float(production_kwh)



def LCOE_per_kwh(interest, inflation, N, solar_production, size_kw, capex):
    operating_maintence = 45 * size_kw
    r = interest / 100
    i = inflation / 100

    capital_recovery_factor = r / (1-(1+r)**(-N))  
    net_present_value = (capex * size_kw) + sum([( (1+i) / (1+r) )**x for x in range(1,N+1)]) + operating_maintence 
    annual_production_kwh = solar_production
    lcoe = (net_present_value * capital_recovery_factor) / annual_production_kwh         
    return float(round(lcoe, 3))
