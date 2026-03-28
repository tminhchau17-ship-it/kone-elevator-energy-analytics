# KONE Elevator Energy Analytics

> **Python-based energy analytics project** analysing real elevator operational data across KONE's Finnish building portfolio — identifying energy efficiency opportunities, regenerative savings, and usage patterns to support data-driven facility management decisions.

---

## Business Context

Elevators account for 2–5% of a building's total energy consumption. For large commercial portfolios, even marginal efficiency gains translate into measurable cost savings and progress toward sustainability targets.

This project was developed as part of a financial and operational analysis of **KONE Oyj** (Nasdaq Helsinki: KNEBV) — a global leader in elevator and escalator systems. The objective was to move beyond high-level financial metrics and examine the operational data layer: how individual elevator units consume energy, when peak demand occurs, and where regenerative braking recovery is underperforming relative to fleet benchmarks.

---

## Key Findings

| Metric | Value |
|---|---|
| Total energy consumption (30-day window) | **6,047 kWh** |
| Regenerative energy recovered | **758 kWh (12.5% of total)** |
| Total elevator trips analysed | **242,276** |
| Average cabin load utilisation | **38%** |
| Buildings covered | **5 sites across Finland** |

**Operational insights surfaced:**

- Peak traffic demand clusters around **06:00–09:00 and 15:00–18:00**, with average kWh/trip rising 18% during peak windows — informing potential demand-shifting strategies
- **Helsinki HQ Tower** accounts for the highest absolute consumption but also the highest regen recovery rate (avg 42–45 kWh per unit), suggesting newer equipment is performing as expected
- **Turku Harbor Building** shows the lowest regen recovery relative to trip volume — a flag for maintenance review or equipment modernisation assessment
- kWh/trip efficiency ranges from **0.0193 to 0.0293** across the fleet, indicating a 34% performance gap between best and worst units

---

## Analytical Approach

**1. Data Pipeline**
Raw elevator operational logs were ingested, cleaned, and structured using Python. Timestamps were parsed, missing values handled, and unit-level identifiers validated against building metadata.

**2. Energy Efficiency Metrics**
A core efficiency metric — **kWh per trip** — was engineered to enable like-for-like comparison across units with different usage volumes. This normalised metric drives the performance ranking table.

**3. Regenerative Recovery Analysis**
Regenerative braking data was isolated to calculate recovery rates by unit, building, and time window. Recovery rate = regen kWh / total consumed kWh, expressed as a percentage.

**4. Traffic Profiling**
Hourly aggregations identified peak demand windows and their correlation with energy intensity — relevant for building managers considering load scheduling or tariff optimisation.

**5. Building-Level Comparison**
Cross-site analysis benchmarked total consumption, recovery rates, and efficiency metrics across five locations, providing portfolio-level visibility.

---

## Tools & Technologies

| Layer | Tools Used |
|---|---|
| Data processing | Python, Pandas, NumPy |
| Visualisation | Plotly, Matplotlib |
| Dashboard | Plotly Dash (multi-page interactive) |
| Environment | Jupyter Notebook |
| Version control | Git, GitHub |

---

## Project Structure

```
kone-elevator-energy-analytics/
│
├── data/
│   └── elevator_logs.csv          # Operational sensor data
│
├── notebooks/
│   └── energy_analysis.ipynb      # Full analysis notebook
│
├── dashboard/
│   └── app.py                     # Plotly Dash dashboard
│
├── outputs/
│   ├── daily_consumption.png
│   ├── hourly_traffic_profile.png
│   ├── building_comparison.png
│   ├── energy_split.png
│   └── performance_ranking.csv
│
└── requirements.txt
```

---

## Running the Project

**Requirements:** Python 3.9+

```bash
git clone https://github.com/tminhchau17-ship-it/kone-elevator-energy-analytics.git
cd kone-elevator-energy-analytics
pip install -r requirements.txt
```

**Run the analysis notebook:**
```bash
jupyter notebook notebooks/energy_analysis.ipynb
```

**Launch the interactive dashboard:**
```bash
python dashboard/app.py
```

---

## Business Relevance

This project was conducted alongside an **equity research report on KONE Oyj** (Aalto University), which evaluated the company's financial performance, ESG positioning, and investment case. The energy analytics work extends that analysis into the operational layer — demonstrating how IoT data from KONE's installed base can generate actionable facility management insights.

For KONE as a business, this type of analysis supports:

- **Maintenance prioritisation** — flagging underperforming units for service review before failure
- **Modernisation business case** — quantifying efficiency gaps to justify equipment upgrade cycles
- **ESG reporting** — providing granular energy consumption data aligned with Scope 1/2 reduction targets
- **Customer value delivery** — enabling KONE to offer data-driven advisory services to building owners, strengthening retention in the maintenance segment

---

## About

Developed by **Chau Minh Tran** — Junior Financial Management professional based in Espoo, Finland.  
Combining financial analysis with data analytics to bridge operational performance and strategic decision-making.

- Email: tminhchau17@gmail.com  
- LinkedIn: [linkedin.com/in/chautran17](https://linkedin.com/in/chautran17)
