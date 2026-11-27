# Part 2 Methodology and Findings

## Purpose and data
Create a reproducible hourly dataset and tools for monitoring traffic on the I-94 corridor. The Part 1 source contained 48,204 rows and nine columns. This pipeline keeps 40,575 unique hourly observations using the same weather ranking as SQL and Power BI.

## Method
Validate the schema, standardise categories, parse local timestamps, remove exact duplicates and select the highest-ranked weather label per hour. Impute invalid temperature, extreme rainfall and documented traffic dropouts with year-month medians. Apply the holiday label across observed hours on each flagged date. Preserve gaps, including September 2014 through May 2015.

Time features cover clock hour, weekday, weekend and cyclical encodings. Weather features include one-hot labels, severity and visibility. Celsius temperature and cloud cover are standardised. Congestion quartiles are stored separately from the fixed SQL threshold and Power BI bands.

## Figure findings
1. The full-period hourly profile peaks at 16:00, averaging 5,709 vehicles.
2. Weekday traffic peaks at 16:00 and weekend traffic peaks at 13:00. Compare each hour against its own day type.
3. The scatter is broad, with Pearson r = +0.140. Clock hour and season can influence the association.
4. Clouds has the highest mean and Squall has the lowest. The lowest category has 1 hour(s), so account for sample size.

## Reconciliation and limitations
The pre-imputation baseline reproduced the Part 1 totals and the Power BI 2017 16:00 mean of 5,834.37 vehicles. Part 2 imputations can change processed means. This historical dataset represents one corridor. Use current counts and matched hours when applying travel recommendations. For Part 3 evaluation, fit scaling and thresholds on training data and exclude traffic-derived categories from predictors.
