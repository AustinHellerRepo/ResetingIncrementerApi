# ResetingIncrementerApi
Permits the incrementing of an internal set of values, reseting back to zero after a predetermined amount of time.

## Features

- Accumulates floating point values for specific keys as they are sent to the "add" entrypoint
- Resets accumulated float point values after specified interval (monthly or after X seconds)

## Usage

_Reset after first of month with total limit of 4TB_
```ini
[Timing]
Interval = day_of_month
Value = 1

[KeyLimits]
some_api_with_one_kilobyte_limit = 1024
api_with_gig_limit = 1073741824

[TotalLimit]
Value = 4398046511104
```

_Reset every 24 hours with total limit of 1GB_
```ini
[Timing]
Interval = seconds_from_now
Value = 86400

[KeyLimits]
simple_api_with_one_megabyte_limit = 1048576
another_service_with_one_gb_limit = 1073741824

[TotalLimit]
Value = 1073741824
```
