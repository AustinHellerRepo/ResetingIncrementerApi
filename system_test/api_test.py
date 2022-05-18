from __future__ import annotations
import unittest
import requests
import json
import os


base_url = "http://localhost:38160"
headers = {}


class ApiTest(unittest.TestCase):

	def test_increment(self):
		path = os.path.join(base_url, "add")

		for _ in range(10):
			response = requests.post(path, json={"key": "test", "value": 1}, headers=headers)
			self.assertEqual(response.status_code, 200)

		response = requests.post(path, json={"key": "test", "value": 1}, headers=headers)
		self.assertEqual(response.status_code, 409)

		for _ in range(5):
			response = requests.post(path, json={"key": "something", "value": 10}, headers=headers)
			self.assertEqual(response.status_code, 200)

		response = requests.post(path, json={"key": "something", "value": 10}, headers=headers)
		self.assertEqual(response.status_code, 409)

		for _ in range(40):
			response = requests.post(path, json={"key": "else", "value": 1}, headers=headers)
			self.assertEqual(response.status_code, 200)

		response = requests.post(path, json={"key": "else", "value": 1}, headers=headers)
		self.assertEqual(response.status_code, 409)
