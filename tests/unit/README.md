# HopMQ unit tests

Test each module (unit) from `src` project dir.

The test structure SHOULD repeat the `src` structure. E.g. tests for unit `src/hopmq/my_package/my_module.py` should be
written in `tests/unit/hopmq/my_package/my_module.py`

## Basic concepts

1) Include [root concepts](../README.md)
2) Instantiate objects of testing unit in `pytest.fixture` and inject it into test function
    * Avoid writing fixtures in `conftest.py`, define fixtures in appropriate test unit modules under test functions
      for readability and easy to lookup.
3) Use `create_autospec(Interface)` to inject dependencies into testing unit
