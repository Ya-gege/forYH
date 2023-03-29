#!/bin/bash
pytest -v smc_benchmark.py::test_party_3_add_50 -v --benchmark-min-rounds=10 --benchmark-save="test_3_50"
#pytest -v smc_benchmark.py::test_party_10_add_50 -v --benchmark-min-rounds=10 --benchmark-save="test_10_50"
#pytest -v smc_benchmark.py::test_party_10_add_100 -v --benchmark-min-rounds=10 --benchmark-save="test_10_100"
#pytest -v smc_benchmark.py::test_party_10_add_500 -v --benchmark-min-rounds=10 --benchmark-save="test_10_500"