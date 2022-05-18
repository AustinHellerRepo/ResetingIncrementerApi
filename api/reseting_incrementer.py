from __future__ import annotations
import threading
import os
from datetime import datetime, timedelta
import json
from austin_heller_repo.common import StringEnum
from typing import List, Dict, Tuple


class IntervalTypeEnum(StringEnum):
	DayOfMonth = "day_of_month"
	SecondsFromNow = "seconds_from_now"


class IncrementKeyOverLimitException(Exception):

	def __init__(self, *, key_value: float, increment_value: float, key_limit: float):
		super().__init__(f"Unable to increment due to reaching the limit with this request. Current value + increment > limit: {key_value} + {increment_value} > {key_limit}.")


class IncrementTotalOverLimitException(Exception):

	def __init__(self, *, total_value: float, increment_value: float, total_limit: float):
		super().__init__(f"Unable to increment due to reaching the total limit for this container. Current value + total > limit: {total_value} + {increment_value} > {total_limit}.")


class ResetingIncrementer():

	def __init__(self, next_reset_file_path: str, values_file_path: str, reset_interval_type: IntervalTypeEnum, reset_interval_value: int, limit_per_key: Dict[str, float], total_limit: float):

		self.__next_reset_file_path = next_reset_file_path
		self.__values_file_path = values_file_path
		self.__reset_interval_type = reset_interval_type
		self.__reset_interval_value = reset_interval_value
		self.__limit_per_key = limit_per_key
		self.__total_limit = total_limit

		self.__lock = threading.Lock()

	def __try_reset(self) -> bool:

		if not os.path.exists(self.__next_reset_file_path):
			is_reset_required = True
		else:
			with open(self.__next_reset_file_path, "rb") as file_handle:
				next_reset_file_contents = file_handle.read()
			next_reset_json = json.loads(next_reset_file_contents.decode())
			next_reset_datetime_string = next_reset_json["datetime"]
			next_reset_datetime = datetime.strptime(next_reset_datetime_string, "%Y-%m-%d %H:%M:%S")
			if datetime.utcnow() > next_reset_datetime:
				is_reset_required = True
			else:
				is_reset_required = False

		if is_reset_required:
			if os.path.exists(self.__values_file_path ):
				os.unlink(self.__values_file_path )

			if self.__reset_interval_type == IntervalTypeEnum.DayOfMonth:
				next_reset_datetime = (datetime.utcnow().replace(day=1) + timedelta(days=32)).replace(day=self.__reset_interval_value)
			elif self.__reset_interval_type == IntervalTypeEnum.SecondsFromNow:
				next_reset_datetime = (datetime.utcnow() + timedelta(seconds=self.__reset_interval_value))
			else:
				raise Exception(f"Unexpected Timing Interval: \"{self.__reset_interval_type}\".")
			next_reset_json = {
				"datetime": next_reset_datetime.strftime("%Y-%m-%d %H:%M:%S")
			}
			file_contents = json.dumps(next_reset_json).encode()
			with open(self.__next_reset_file_path, "wb") as file_handle:
				file_handle.write(file_contents)

		return is_reset_required

	def __get_file_json(self) -> Dict:
		if os.path.exists(self.__values_file_path):
			with open(self.__values_file_path, "rb") as file_handle:
				file_contents = file_handle.read()
			file_json = json.loads(file_contents.decode())  # type: Dict
		else:
			file_json = {}
		return file_json

	def __set_file_json(self, *, file_json: Dict):
		file_contents = json.dumps(file_json).encode()
		with open(self.__values_file_path, "wb") as file_handle:
			file_handle.write(file_contents)

	def __get_total_value(self) -> float:
		file_json = self.__get_file_json()
		if file_json:
			total_value = sum(file_json.values())
		else:
			total_value = 0
		return total_value

	def __get_value(self, *, key: str) -> float:
		return self.__get_file_json().get(key, 0)

	def __set_value(self, *, key: str, value: float):
		file_json = self.__get_file_json()
		file_json[key] = value
		self.__set_file_json(
			file_json=file_json
		)

	def increment(self, *, key: str, value: float):
		self.__lock.acquire(True)
		try:
			self.__try_reset()
			current_value = self.__get_value(
				key=key
			)
			incremented_value = current_value + value
			value_limit = self.__limit_per_key[key]

			total_value = self.__get_total_value()
			incremented_total_value = total_value + value
			total_limit = self.__total_limit

			if incremented_value > value_limit:
				raise IncrementKeyOverLimitException(
					key_value=current_value,
					increment_value=value,
					key_limit=value_limit
				)
			elif incremented_total_value > total_limit:
				raise IncrementTotalOverLimitException(
					total_value=total_value,
					increment_value=value,
					total_limit=total_limit
				)
			else:
				self.__set_value(
					key=key,
					value=incremented_value
				)
		finally:
			self.__lock.release()
