# HopMQ tests

Tests are written using pytest framework.

## Structure

* [unit](unit) tests
* [integration](integration) tests
* [stub](stub) -- stub / dummy implementations for tests

## Basic concepts

1) specify expected behaviour in tests function name. E.g. `test_connection_established_with_broker` or `test_state_machine_transits_to_expected_state`
    * if function tests a specific case - also specify it in name using `after`, `when` keywords. E.g. `test_connection_reestablished_after_failure`
2) inject values for tests from fixtures or using `pytest.mark.parametrize`

Test function example:

```python
import typing as t

import pytest


@pytest.mark.parametrize(["items", "expected"], [pytest.param([1, 2, 3], 6)])
def test_sum_returns_expected_value(items: t.Sequence[int], expceted: int) -> None:
     assert sum(items) == expceted
```
