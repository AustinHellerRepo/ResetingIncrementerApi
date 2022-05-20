# ResetingIncrementerApi
Permits the incrementing of an internal set of key-value pair float values, reseting back to zero after a predetermined amount of time. It is essential that the docker container has a mounted volume to store the current state in the event that the container is stopped and restarted.

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
super_big_api = 4398046511104

[TotalLimit]
Value = 4398046511104
```
The "super_big_api" is able to use the entire four terrabytes of outbound data. Once the total usage from all of the APIs hits either their respective limits or the summation hits the total limit, a 409 HTTP error code will be sent to the calling process.

_Reset every 24 hours with total limit of 1GB_
```ini
[Timing]
Interval = seconds_from_now
Value = 86400

[KeyLimits]
simple_api_with_one_megabyte_limit = 1048576
another_service_with_one_gb_limit = 1073741824
some_other_service_with_one_gb_limit = 1073741824

[TotalLimit]
Value = 1073741824
```
This setup basically permits "another_service_with_one_gb_limit" and "some_other_service_with_one_gb_limit" to compete for the maximum limit of one gigabyte of outbound data. The "simple_api_with_one_megabyte_limit" would be something that is not expected to output much data and it is okay if it fails due to the other services hitting the total limit.
