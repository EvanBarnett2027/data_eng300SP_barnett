# Homework 1 Write-up

Written responses for Tasks 1–6, extracted from `01_hw.ipynb`.

# Task 1

### General EDA



Aircraft Statuts - 'A' = Capital Lease, 'B' = Operating Lease, 'O' = Owned

### MANUFACTURE YEAR

The values above are almost certainly incorrect for the plane's manufacture year. These should all be treated the same. We can impute based on the average manufacture year of that specific plane model.

### CAPACITY_IN_POUNDS

Missing values are almost entirely in 2023 and 2022. This suggests that `CAPACITY_IN_POUNDS` is not MCAR, because it can be explained by `YEAR`. Also, it is likely not MNAR because all of the recent values are missing; it does not depend on the value of the missing entires itself. Therefore, this column is MAR.

#### CAPACITY_IN_POUNDS non-nans

**Manual Data Check**:
1. MCDONNELLDOUGLAS MD-83 - Maximum takeoff weight is 160k - `CAPACITY_IN_POUNDS` = 160

2. The Cessna Citation Excel (CE-560XL) has a maximum useful load of 7,500 pounds. Its maximum takeoff weight is 20,200 pounds, while the maximum payload (weight of passengers and baggage) is 2,300 pounds. -- `CAPACITY_IN_POUNDS` = 80
3. Embraer E190-100 mf year 2006 - Max takeoff weight ~ 105k - 115k -- `CAPACITY_IN_POUNDS` = 200

4. Douglas 2012 (model is not correct here, there is no model 2012?) - Maximum payload = 20,800, Maximum takeoff weight - 114,600 to 122,000, Cargo compartment = 12,180 -- `CAPACITY_IN_POUNDS` = 12 -- seems to line up with cargo weight, makes sense for FedEx plane

5. JetBlue A320-232 capacity in pounds 37400 -- `CAPACITY_IN_POUNDS` = 400 -- truncated???

6. Gulf Stream G-IV max payload = 3400 -- `CAPACITY_IN_POUNDS` = 400 -- truncated???

7. Pilatus PC-12 NG max payload = 2236 -- `CAPACITY_IN_POUNDS` = 400

8. DASSAULT-FALCON-50EX  max takeoff weight 39700, payload 3320 -- `CAPACITY_IN_POUNDS`

**Analysis**:

Capacity in pounds for values under 500, are almost entirely incorrect. Values under 1000, frequently incorrect. I'm confident the issue also propogates to higher values of `CAPACITY_IN_POUNDS` in someway, but I can't check every data point manually. It also seems like some planes use maximum takeoff weight, passenger weight, or cargo capacity. Some values appear to be truncated, whereas others are off by a factor of 1,000. Also, many values are zero, and I am not sure if this is more data missingness or intentional.

The above function imputes missingness and bad values treated as missing using the median of comparable groups in order of decreasing similarity. The idea is to find planes (with valid `CAPACITY_IN_POUNDS`) as similar as possible to the ones with missing values and use the median from the comaparable as the imputed value.

There are three groups used as comparables:
1. Use the median from planes with the exact same model
2. Use the median from planes from the same manufacturer and similar number of seats
3. Use the median from planes with a similar number of seats (any manufacturer)

If an observation with a missing value does not fall into one of these categories, then the populaton median is used.

This approach is likely preferred over a mice forest because the `CAPACITY_IN_POUNDS` column contains many incorrect values, so the gradient boosting methods would try to recreate the patterns in the contaminated data. This above approach is also preferred over a simple median imputation strategy because there is too much variance in the data for this to be meaningfully descriptive of the missing oservations.

### CARRIER

`CARRIER` is only missing for "North American Airlines"

Need to strip extra spaces.

North American Airlines is the only airline that uses `CARRIER` code 'NA'

### CARRIER_NAME

Carrier code can be repurposed in the future, e.g. 2011: OH -> Comair Inc., 2015: OH -> PSA Airlines Inc.

Can't just map (`YEAR`, `CARRIER`) -> `CARRIER_NAME` because it could be missing for an entire year.

The missing entries are likely Lynx and Comair (not PSA). The tail numbers end in 2-letter codes which can be used to differentiate the plane's carrier.

### NUMBER OF SEATS

Is there a pattern for when number of seats is missing?:
- Are there certain carriers who do not report number of seats?
- Are there certain types of planes who do not report number of seats?
- Are there planes with zero seats (passenger)?
    - Yes some small private planes only have 2 crew seats.

`NUMBER_OF_SEATS` appears to be MCAR. There is not another feature or set of features that can explain missingness, which can be seen from the performance of the decision tree. The accuracy of 0.93 is misleading as the class balance is 10% missing 90% not missing. The mediocre performance can be seen from recall, which implies that only 40% of missing entries are identified. Therefore, it is likely not MAR. Since there is no clear structural pattern, there is also little evidence that it is MNAR, because if the missingness were systematically related to the underlying number of seats, we would likely expect at least some stronger pattern in the observed features or in model performance. Thus, MCAR is the most reasonable classification for `NUMBER_OF_SEATS`.

The `NUMBER_OF_SEATS` column is imputed using the mode of comparables, if they exist, in decreasing order of similarity. Mode is chosen here because number of seats is a discrete label with repeated configurations. This results in the imputted value being a commonly observed seating configuration.

### AIRLINE_ID

From the general EDA, we can see that `AIRLINE_ID` is missing exactly when `CARRIER_NAME` is missing. Also according to the data description, it seems that there is a one-to-one relationship between `CARRIER_NAME` and `AIRLINE_ID`.

Mostly true that it is 1-to-1. Leave nan if there are conflicts.

# Task 2

For each of `MANUFACTURER`, `MODEL`, `AIRCRAFT_STATUS`, and `OPERATING_STATUS`, inspect the raw values with `value_counts()` to decide whether standardization is needed. The two status columns are categorical, so capitalization and whitespace fixes are sufficient. `MANUFACTURER` and `MODEL` are very messy: for these we use `value_counts()` rather than attempting to catch every variant.

### AIRCRAFT_STATUS

Aircraft Statuts - 'A' = Capital Lease, 'B' = Operating Lease, 'O' = Owned

Both versions appear (`A`/`a`, `B`/`b`, `O`/`o`), and there are 122 rows with value `'L'`, which is not a unknwon code? Standardization is needed

1. Uppercase everything
2. Treat `'L'` as unknown and set it to `pd.NA`. `'L'` is not in the published code list, and all 122 instances are on a single carrier in a single year.

### OPERATING_STATUS

Expected to be a Y/N flag.

mostly `'Y'` and `'N'`, but there are 71 `'y'` entries and 1 value empty string.

1. Strip whitespace and uppercase
2. Everything else becomes `pd.NA`

### MANUFACTURER

a lot of duplicates for the same manufacturer. 

to fix:
1. Trailing whitespace
2. capitalization
3. Punctuation / dashes
4. Company naming variants

### MODEL

messier than `MANUFACTURER`

to fix:
1. Inconsistent prefixes and separators
2. Suffixes describing configuration e.g. "PASSENGERONLY".
3. capitalization, whitespace, punctuation

### Apply Imputation and Standardization

1. Standardize the 4 text columns
2. Impute carriers `CARRIER`, `CARRIER_NAME`, and then `AIRLINE_ID`.
3. Impute numeric `MANUFACTURE_YEAR`, `NUMBER_OF_SEATS`, and then`CAPACITY_IN_POUNDS`.

# Task 3

The cleaning functions are applied in a specific order because later steps depend on earlier standardized values. First, the text columns are standardized so that grouping keys like `MODEL`, `MANUFACTURER`, `AIRCRAFT_STATUS`, and `OPERATING_STATUS` are consistent. Otherwise, the imputation functions would treat the same plane or status as separate categories due only to capitalization, spacing, or punctuation. Carrier fields are imputed next, with `CARRIER` and `CARRIER_NAME` filled before `AIRLINE_ID` because the ID is mapped from the cleaned carrier name. The numeric fields are then imputed in dependency order: `MANUFACTURE_YEAR`, then `NUMBER_OF_SEATS`, then `CAPACITY_IN_POUNDS`, since capacity imputation uses the cleaned model/manufacturer and seat count to find comparable aircraft. Finally, `clean_dropped = clean.dropna(subset=inventory.columns)` removes rows that still have missing values after all reasonable standardization and imputation steps. These remaining values are mostly unresolved or invalid entries, such as unknown status codes or carrier/name combinations with no reliable mapping, so they are removed rather than guessed.

# Task 4

- `CAPACITY_IN_POUNDS` is strongly right skewed at 4.0 and `NUMBER_OF_SEATS` is more symmetric at -0.2, but is bimodal rather than normal.

- After the transformation, `CAPACITY_IN_POUNDS_BOXCOX` loses almost all of its skew at 0.11. `NUMBER_OF_SEATS_BOXCOX` becomes more skewed, going from -0.2 to -0.6. This is because Boxcox is targets right skew, so it cannot fix bimodality.

# Task 5

### OPERATING_STATUS by SIZE

### AIRCRAFT_STATUS by SIZE

### Summary

Quartile edges [0, 50], (50, 117], (117, 154] (154, 190+] seats. 

`OPERATING_STATUS` by size: Operating rates are high across the board (>95% in every bin). `XLARGE` has the highest operating rate (~97%) and `SMALL` the lowest (~95%). 

`AIRCRAFT_STATUS` by size: The lease structure is not monotonic in size.

- `SMALL` is dominated by O  at ~58% with a significant (B) share at ~37% 
- `MEDIUM` is the outlier: only ~49% Owned and ~47% Operating Lease the highest B share of any group.
- `LARGE` shifts back toward Owned (~64%) with a increases in capital Lease (A) (~15%)
- `XLARGE` has the highest Owned share (~70%).

Therefore, `SIZE` is a useful engineered feature as it correlates with operating probability and ownership.

# Task 6

Feature choice:

- Numeric: `YEAR`, `MANUFACTURE_YEAR`, and the other numeric target of `CAPACITY_IN_POUNDS` and `NUMBER_OF_SEATS` depending on the target
- Categorical: `MANUFACTURER` `AIRCRAFT_STATUS`, `OPERATING_STATUS`
- Not Used: `SIZE` (leakage), `MODEL` and `AIRCRAFT_TYPE` (too many values)

### Observations


| target              | model            | train RMSE | test RMSE |
|---------------------|------------------|-----------:|----------:|
| NUMBER_OF_SEATS     | LinearRegression |      ~49.0 |     ~49.0 |
| CAPACITY_IN_POUNDS  | LinearRegression |    ~77,660 |   ~77,430 |
| NUMBER_OF_SEATS     | RandomForest     |      ~3.4  |     ~6.0  |
| CAPACITY_IN_POUNDS  | RandomForest     |    ~50,650 |   ~56,500 |

- Random forest beats linear regression on both targets. For `NUMBER_OF_SEATS`, test RMSE drops from ~49 to ~6.5. For `CAPACITY_IN_POUNDS` it drops from ~77k to ~55k. 

- Linear regression appears to underfit as its train and test RMSEs are almost the same. That most likely implies the model it isn't flexible enough to learn the structure in the data at all.

- Random forest shows mild overfitting. For seats, train RMSE is 3.5 vs test of 5.5. This could potentially be fixed via hyperparameter tuning.
