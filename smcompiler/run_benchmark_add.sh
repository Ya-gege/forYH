#!/bin/bash
#pytest -v smc_benchmark.py::test_party_3_add_50 -v --benchmark-min-rounds=10 --benchmark-save="test_3_50"
#pytest -v smc_benchmark.py::test_party_10_add_50 -v --benchmark-min-rounds=10 --benchmark-save="test_10_50"
#pytest -v smc_benchmark.py::test_party_10_add_100 -v --benchmark-min-rounds=10 --benchmark-save="test_10_100"
#pytest -v smc_benchmark.py::test_party_10_add_500 -v --benchmark-min-rounds=10 --benchmark-save="test_10_500"



# actual test
pytest -v smc_benchmark.py::test_actual_party_5_add_50 -v --benchmark-min-rounds=1
pytest -v smc_benchmark.py::test_actual_party_10_add_50 -v --benchmark-min-rounds=1
pytest -v smc_benchmark.py::test_actual_party_15_add_50 -v --benchmark-min-rounds=1
pytest -v smc_benchmark.py::test_actual_party_20_add_50 -v --benchmark-min-rounds=1
pytest -v smc_benchmark.py::test_actual_party_25_add_50 -v --benchmark-min-rounds=1
pytest -v smc_benchmark.py::test_actual_party_30_add_50 -v --benchmark-min-rounds=1


#pytest -v smc_benchmark.py::test_actual_party_25_add_50 -v --benchmark-min-rounds=10 --benchmark-save="test_25_50"
