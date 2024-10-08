from __future__ import annotations

from typing import TYPE_CHECKING

import hypothesis.strategies as st
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    DataT,
    Metric,
    NumberDataPoint,
    Sum,
)

if TYPE_CHECKING:
    from opentelemetry_exporter_oci_monitoring.converter import Attributes


def simple_strings(
    *, min_size: int = 0, max_size: int | None = None
) -> st.SearchStrategy[str]:
    return st.text(
        alphabet=st.characters(
            categories=[
                "Lu",  # Letter, uppercase
                "Ll",  # Letter, lowercase
                "Nd",  # Number, decimal digit
                "Pc",  # Punctuation, connector
                "Pd",  # Punctuation, dash
            ]
        ),
        min_size=min_size,
        max_size=max_size,
    )


def attributes(
    *, min_size: int = 0, max_size: int | None = None
) -> st.SearchStrategy[Attributes]:
    return st.dictionaries(
        simple_strings(min_size=1, max_size=12),
        st.one_of(
            st.booleans(),
            st.integers(),
            st.floats(),
            simple_strings(max_size=12),
            st.lists(st.booleans()),
            st.lists(st.integers()),
            st.lists(st.floats()),
            st.lists(simple_strings(max_size=12)),
        ),
        min_size=min_size,
        max_size=max_size,
    )


@st.composite
def number_data_points(
    draw: st.DrawFn,
    attributes: st.SearchStrategy[Attributes] = attributes(),
    value: st.SearchStrategy[int | float] = st.integers() | st.floats(),
) -> NumberDataPoint:
    start_time_unix_nano = draw(st.integers(min_value=0))
    delta_time_unix_nano = draw(st.integers(min_value=1))
    return NumberDataPoint(
        attributes=draw(attributes),
        start_time_unix_nano=start_time_unix_nano,
        time_unix_nano=start_time_unix_nano + delta_time_unix_nano,
        value=draw(value),
    )


@st.composite
def sums(
    draw: st.DrawFn,
    data_points: st.SearchStrategy[list[NumberDataPoint]] = st.lists(
        number_data_points()
    ),
    aggregation_temporalities: st.SearchStrategy[
        AggregationTemporality
    ] = st.sampled_from(AggregationTemporality),
    is_monotonics: st.SearchStrategy[bool] = st.booleans(),
) -> Sum:
    return Sum(
        data_points=draw(data_points),
        aggregation_temporality=draw(aggregation_temporalities),
        is_monotonic=draw(is_monotonics),
    )


@st.composite
def metrics(
    draw: st.DrawFn,
    names: st.SearchStrategy[str] = simple_strings(min_size=3, max_size=12),
    data: st.SearchStrategy[DataT] = sums(),
) -> Metric:
    return Metric(name=draw(names), description=None, unit=None, data=draw(data))
