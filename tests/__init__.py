from typing import Mapping

ASCII_PRINTABLE_MIN = 33
ASCII_PRINTABLE_MAX = 126
DIM_KEY_MAX_LEN = 256
DIM_VALUE_MAX_LEN = 512


def assert_wellformed_oci_metric_dimensions(dimensions: Mapping[str, str]) -> None:
    """Validate the dimensions conform to OCI specifications.

    The OCI documentation states: Qualifiers provided in a metric definition. Available
    dimensions vary by metric namespace. Each dimension takes the form of a key-value
    pair. A valid dimension key includes only printable ASCII, excluding spaces. The
    character limit for a dimension key is 256. A valid dimension value includes only
    Unicode characters. The character limit for a dimension value is 512. Empty strings
    are not allowed for keys or values. Avoid entering confidential information.
    """
    for key, value in dict(dimensions).items():
        assert all(
            ASCII_PRINTABLE_MIN <= ord(char) <= ASCII_PRINTABLE_MAX for char in key
        )
        assert 1 <= len(key) <= DIM_KEY_MAX_LEN
        assert 1 <= len(value) <= DIM_VALUE_MAX_LEN
