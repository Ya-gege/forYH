#!/bin/bash
pytest -v smc_benchmark.py::test_benchmark_suite_1 -v --benchmark-min-rounds=1 --benchmark-save="test"