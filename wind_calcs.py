import pandas as pd


# determining a default capcity factor for a wind turbine for any given city based of wind power class
#### actual results will vary
def default_capacity_factor(df) -> float:
    wind_power_class = df['wpc'].item()
    wpc_to_cap_factor = {7:32, 6:29, 5:26, 4:22, 3:18, 2:14, 1:8}
    return wpc_to_cap_factor[wind_power_class]



# estimating size for a wind turbine installtion based of total amount of power consumed in city/grid
### using 30% of overall use. value is near median for other state projects.
def Turbine_size_est(df, est_cap_factor):
    decimal_cap_fac = est_cap_factor/100
    
    total_kwh = df['total_kwh_sold'].item()
    est_size = total_kwh * 0.3 / (8766 * decimal_cap_fac)
    rounded_size = int(round(est_size, -2))
    
    # adjusting for round to zero error
    if rounded_size == 0:
        rounded_size = 50
    return int(rounded_size)


# estimating Capital Expenditure for a given city/village project.
## estimates are dervied from PCE (Power Cost Equalizer) rate.
## this can represent how costly it is to produce power in given city.
#### A Correlation between PCE rate and CapEx is used for estimation.   
def est_capex_per_kw(df):
    pce_cost = df['pce_rate'].item()
    if pce_cost == 0 or pce_cost == 'nan':
        capex = 4000
    elif pce_cost >= 0.75:
        capex = 30000
    else:
        capex = 4000 + pce_cost * 34666
    return round(capex, -2)



# Adjusting CapEx relativie to size of turbine installation.
## Coefficents are taking from a Logistic Regression of past projects with respect to CapEx vs Installation size
def adjusted_capex_per_kw(default_capex, size):
    coef_dict = {50: 0.082,  100: 0.07634832, 200: 0.05886931, 500: 0.03408415, 1000: -0.02408789, 2000: -0.24361946}
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
    else:
        adjusted_cap = default_capex * (1 + coef_dict[50])
    return round(adjusted_cap, -2)


def project_capex(adj_capex, size_kw):
    if size_kw == 0:
        size_kw = 50
    else:
        size_kw = size_kw
    return adj_capex * size_kw



def total_annual_capex(proj_capex, lifetime, interest_rate):
    i = interest_rate / 100
    N = lifetime
    operating_maintence = 0.036

    annual_cap = proj_capex * i * (1+i)**N / ((1+i)**N -1)

    return annual_cap + operating_maintence



def lcoe_per_kwh():
    return





# calculating Levelized Cost Of Energy per kiloWatt-hour
def LCOE_per_kwh(interest, inflation, N, capacity_factor, turbine_size_kw, capex):
    #changing turbine size for cities if turnbine_size_kw == 0
    if turbine_size_kw == 0:
        turbine_size_kw = 50
    else:
        turbine_size_kw = turbine_size_kw    
    
    operating_maintence = 0.036
    r = interest / 100
    i = inflation / 100
    cap_fac = capacity_factor / 100

    capital_recovery_factor = r / (1-(1+r)**(-N))
    net_present_value = (capex * turbine_size_kw) + sum([( (1+i) / (1+r) )**x for x in range(1,N+1)]) * operating_maintence
    annual_production_kwh = turbine_size_kw * cap_fac * 8760
    LCOE = (net_present_value * capital_recovery_factor) / annual_production_kwh   
    return round(LCOE, 3)




