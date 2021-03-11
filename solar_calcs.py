import pandas as pd


# determing solar caparcity factor for location
### Estimates were etracted from NREL PVWatts calculator.
def solar_capacity_factor(df):
    ac_annual_kwh = df['solar_ac_annual_1kw']
    capacity_factor = ac_annual_kwh / 8760
    return round(capacity_factor * 100, -1).item()


# Estimating size of solar 
### using 30% of overall use. value is near median for other state projects..
def size_est(df, cap_factor):
    total_kwh = df['total_kwh_sold'].item()
    decimal_cap = cap_factor / 100
    est_size = total_kwh * 0.3 / (decimal_cap * 8760)    #solar_ac_annual_1kw is a measuremnt of kwh 
    return int(round(est_size, -2))
