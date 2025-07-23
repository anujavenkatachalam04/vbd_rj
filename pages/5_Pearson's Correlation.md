# Pearson's Correlation for Threshold (Tmin >=18 AND Tmax <=35 OR Rel Humidity b/w 60,80) & Lag (9 weeks) - Dengue & Climate (Jul–Dec 2024)

## Objective
To explore the relationship between **block-level dengue cases** and **lagged climate variables** during the period **July–December 2024**, focusing on lags between climate exposure and disease onset.

---

## Methodology

1. **Data Sources**
   - Daily dengue cases by block and date
   - Daily ERA 5 climate data (min temperature, max temperature, total rainfall, relative humidity) by block

2. **Preprocessing**
   - Limited analysis to dengue season of 2024. Filtered dengue cases between **July 1 and December 31, 2024**
   - Included only districts with **≥100 reported cases** during this period
   - Climate variables considered:
     - `temperature_2m_max`
     - `temperature_2m_min`
     - `relative_humidity_2m_mean`
     - `rain_sum`

3. **Lagged Climate Exposure**
   - For each dengue case, calculated the **mean (or sum)** of climate values over a **63-day window (9 weeks)** prior to the case date
     - Rainfall: **sum**
     - Temperature & humidity: **mean**

4. **Threshold Check**
   - Climate data included only if the threshold condition was met on **≥4 of the 7 days** leading up to the lag window:
     - `temperature_2m_min ≥ 18°C` AND `temperature_2m_max ≤ 35°C` OR `relative_humidity_2m_mean` between **60% and 80%**

5. **Analysis**
   - Computed **Pearson correlation coefficients** between dengue case counts and lagged climate values with a lag of 63 days (9 weeks) based on the EDA
   - Assessed statistical significance at **p < 0.05**

---

## Results

| Variable                   | Correlation | Significant (p<0.05) | Relationship                                      |
|----------------------------|-------------|-----------------------|-----------------------------------------------------|
| temperature_2m_max         | -0.007      |  N                    | No meaningful relationship                          |
| temperature_2m_min         | -0.059      |  Y                    | Weak negative effect — higher min temp, fewer cases |
| relative_humidity_2m_mean | -0.048      | Y                 | Weak negative — higher RH linked to fewer cases     |
| rain_sum                  | 0.035       | Y                 | Weak positive — more rain linked to more cases      |

---

## Interpretation & Next Steps

- Although statistically significant, **correlations are weak**, suggesting **nonlinear or delayed effects**.
- Further stratify by high-case blocks to detect localized patterns
- Test non-linear models - e.g., DLNM



---

