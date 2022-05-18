from __future__ import annotations
import unittest
import tempfile
import os
import time
from api.reseting_incrementer import ResetingIncrementer, IntervalTypeEnum, IncrementKeyOverLimitException


class ResetingIncrementerTest(unittest.TestCase):

	def test_missing_key_on_increment(self):

		temp_directory = tempfile.TemporaryDirectory()

		try:
			incrementer = ResetingIncrementer(
				next_reset_file_path="next_reset.json",
				values_file_path="values.json",
				reset_interval_type=IntervalTypeEnum.SecondsFromNow,
				reset_interval_value=1,
				limit_per_key={
					"system_test": 10
				}
			)

			self.assertIsNotNone(incrementer)

			with self.assertRaises(KeyError) as ex:
				incrementer.increment(
					key="missing key",
					value=0
				)
			self.assertEqual("'missing key'", str(ex.exception))

		finally:
			temp_directory.cleanup()

	def test_increment_zero(self):

		temp_directory = tempfile.TemporaryDirectory()

		try:

			next_reset_file_path = os.path.join(temp_directory.name, "next_reset.json")
			values_file_path = os.path.join(temp_directory.name, "values.json")

			incrementer = ResetingIncrementer(
				next_reset_file_path=next_reset_file_path,
				values_file_path=values_file_path,
				reset_interval_type=IntervalTypeEnum.SecondsFromNow,
				reset_interval_value=1,
				limit_per_key={
					"system_test": 10
				}
			)

			self.assertIsNotNone(incrementer)

			incrementer.increment(
				key="system_test",
				value=0
			)

		finally:
			temp_directory.cleanup()

	def test_increment_to_limit_not_over(self):

		temp_directory = tempfile.TemporaryDirectory()

		try:

			next_reset_file_path = os.path.join(temp_directory.name, "next_reset.json")
			values_file_path = os.path.join(temp_directory.name, "values.json")

			incrementer = ResetingIncrementer(
				next_reset_file_path=next_reset_file_path,
				values_file_path=values_file_path,
				reset_interval_type=IntervalTypeEnum.SecondsFromNow,
				reset_interval_value=1,
				limit_per_key={
					"system_test": 10
				}
			)

			self.assertIsNotNone(incrementer)

			for reset_index in range(3):

				for _ in range(10):
					incrementer.increment(
						key="system_test",
						value=1
					)

				incrementer.increment(
					key="system_test",
					value=0
				)

				with self.assertRaises(IncrementKeyOverLimitException):
					incrementer.increment(
						key="system_test",
						value=1
					)

				time.sleep(1.1)

		finally:
			temp_directory.cleanup()
