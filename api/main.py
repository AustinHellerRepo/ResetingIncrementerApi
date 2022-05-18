from __future__ import annotations
from typing import Dict, List, Tuple
import json
import os
import pathlib
import sys
import threading
import configparser
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException
from api.reseting_incrementer import ResetingIncrementer, IncrementKeyOverLimitException, IntervalTypeEnum, IncrementTotalOverLimitException


def get_setting(*, category: str, key: str) -> str:
	config = configparser.ConfigParser()
	config.read(settings_file_path)
	if category not in config:
		raise Exception(f"Failed to find category \"{category}\" in {settings_file_path}.")
	elif key not in config[category]:
		raise Exception(f"Failed to find key \"{key}\" in config category \"{category}\" in {settings_file_path}.")
	setting = config[category][key]
	return setting


def get_settings_as_float(*, category: str) -> Dict[str, float]:
	config = configparser.ConfigParser()
	config.read(settings_file_path)
	if category not in config:
		raise Exception(f"Failed to find category \"{category}\" in {settings_file_path}.")
	float_per_key = {}  # type: Dict[str, float]
	for key in config[category]:
		value_string = config[category][key]
		try:
			value = float(value_string)
		except ValueError:
			raise Exception(f"Failed to parse limit float from string \"{value_string}\".")
		float_per_key[key] = value
	return float_per_key


app = FastAPI()

data_directory_path = os.path.join(os.getcwd(), "data")
pathlib.Path(data_directory_path).mkdir(
	parents=True,
	exist_ok=True
)

values_file_path = os.path.join(data_directory_path, "values.json")
settings_file_path = os.path.join(data_directory_path, "settings.ini")
next_reset_file_path = os.path.join(data_directory_path, "reset.ser")

interval_setting = get_setting(
	category="Timing",
	key="Interval"
)

try:
	interval = IntervalTypeEnum(interval_setting)
except ValueError:
	raise Exception(f"Failed to find interval type \"{interval_setting}\" in {IntervalTypeEnum.__name__}.")

interval_value_string = get_setting(
	category="Timing",
	key="Value"
)

try:
	interval_value = int(interval_value_string)
except ValueError:
	raise Exception(f"Failed to parse interval value into integer. Found: \"{interval_value_string}\".")


total_limit_string = get_setting(
	category="TotalLimit",
	key="Value"
)

try:
	total_limit = float(total_limit_string)
except ValueError:
	raise Exception(f"Failed to parse total limit into float. Found: \"{total_limit_string}\".")


incrementer = ResetingIncrementer(
	next_reset_file_path=next_reset_file_path,
	values_file_path=values_file_path,
	reset_interval_type=interval,
	reset_interval_value=interval_value,
	limit_per_key=get_settings_as_float(
		category="KeyLimits"
	),
	total_limit=total_limit
)


@app.post("/add")
async def increment(request: Request):
	request_json = await request.json()
	if "key" not in request_json:
		raise HTTPException(
			status_code=422,
			detail=f"Failed to find \"key\" key in input json. Found: {request_json}."
		)
	key = request_json["key"]
	if "value" not in request_json:
		raise HTTPException(
			status_code=422,
			detail=f"Failed to find \"value\" key in input json. Found: {request_json}."
		)
	value_string = request_json["value"]
	try:
		value = float(value_string)
	except ValueError:
		raise HTTPException(
			status_code=422,
			detail=f"Failed to cast value \"{value_string}\" to float."
		)

	try:
		incrementer.increment(
			key=key,
			value=value
		)
	except IncrementKeyOverLimitException as ex:
		raise HTTPException(
			status_code=409,
			detail=str(ex)
		)
	except IncrementTotalOverLimitException as ex:
		raise HTTPException(
			status_code=409,
			detail=str(ex)
		)
