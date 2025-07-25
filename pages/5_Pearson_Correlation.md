## Correlation Analysis
 
- The objective is to identify any significant correlations between climatic predictors and dengue cases for further modeling.

## Scope
* In 2024, five out of 33 districts accounted for 50% of dengue cases in Rajasthan.
* Sparse and under-reported data limits the reliability of state-wide climate lag and threshold analysis.
* Therefore, the analysis is restricted to sub-districts reporting ≥5% of total state cases. Of these,  two subdistricts - Ganganagar & Bikaner were excluded due to reporting anomalies (e.g., sudden spikes, delayed onset).
  
## Pearson's Correlation Without Threshold 
   
| **Variable**              | 2 weeks | 6 weeks | 7 weeks | 9 weeks | **10 weeks** | Association|
|---------------------------|-------------|-------------|-------------|-------------|--------------|-----------------------------|
| **Max Temperature (°C)**  | -0.143 *     | -0.357 *     | -0.382 *     | -0.420 *     | -0.428 *      | Strong negative             |
| **Min Temperature (°C)**  | -0.147 *     | -0.255 *     | -0.271 *     | -0.291 *     | -0.293 *      | Moderate negative           |
| **Relative Humidity (%)** | 0.055        | 0.269 *      | 0.311 *      | 0.376 *      | 0.400 *       | Strong positive (≥6 weeks)  |
| **Rainfall (mm)**         | -0.151 *     | -0.024       | 0.006        | 0.052        | 0.071         | Weak/unclear                |
* `*` denotes statistically significant correlation (**p < 0.05**).

## Pearson's Correlation Post Threshold (Mean Max Temp ≤ 35°C AND Min Temp ≥ 18°C OR RH 60–80%)

| Climate Variable        | 2 Weeks   | 6 Weeks   | 7 Weeks   | 9 Weeks   | 10 Weeks  | Association |
|-------------------------|-------------|-----------|-----------|-----------|-----------|-----------|
| Max Temperature (°C)    | -0.052    | -0.311*   | -0.347*   | -0.368*   | -0.350*   | Moderate negative    |
| Min Temperature (°C)    |  -0.081    | -0.064    | -0.049    | -0.009    | 0.025     |Weak/unclear    |
| Relative Humidity (%)   |  0.001     | 0.195*    | 0.230*    | 0.301*    | 0.328*    |Moderate positive    |
| Rainfall (mm)           |  -0.165*   | -0.067    | -0.041    | -0.003    | 0.004     |Weak/unclear       |

* `*` denotes statistically significant correlation (**p < 0.05**).
* Only includes cases where threshold conditions were met in atleast 4 out of the 7 days prior to the lagged exposure date.

## DLNM

### 📊 Climate–Dengue DLNM Summary (June–Nov 2024)

| **Variable**        | **Notable Lags (Weeks)**      | **Direction of Effect**   | **Short-Term Interpretation (0–2 weeks)**              | **Long-Term Interpretation (3–12 weeks)**                           | **Cumulative Effect** |
|---------------------|-------------------------------|----------------------------|--------------------------------------------------------|---------------------------------------------------------------------|------------------------|
| **Max Temperature** | Lag 3–4 (sig. negative), 12 (positive) | Mixed: 🔻 (lag 3–4), 🔺 (lag 12) | Little immediate effect                                 | Dengue cases increase **as temperatures fall** (3–4 weeks later); early season warmth may briefly suppress | **–0.18**              |
| **Min Temperature** | Lag 0 (sig. positive)          | 🔺 Positive                 | **Warm nights** → more cases in same week              | Effect tapers after 3–4 weeks                                       | **+0.10**              |
| **Humidity**        | Lag 2–4, 9 (positive)          | 🔺 Positive                 | Little effect in week 0                                 | High humidity **2–4 weeks earlier** increases mosquito survival     | **+0.07**              |
| **Rainfall**        | Lag 5–7, 10, 12 (mixed)        | Mixed: 🔺 & 🔻              | No immediate impact                                     | Moderate rain increases risk **5–7 weeks later**; excess rain may reduce it | **≈0**                 |

---

### Takeaway

- 🌡️ **Max temp drops → dengue rises** (after 3–4 weeks).
- 🌙 **Warm nights = more dengue**, especially in the same or next week.
- 💧 **High humidity** 2–4 weeks before case spikes helps mosquito survival.
- 🌧️ **Rainfall** has a mixed effect: **moderate rain promotes breeding**, while **excess rain can flush breeding sites**.


