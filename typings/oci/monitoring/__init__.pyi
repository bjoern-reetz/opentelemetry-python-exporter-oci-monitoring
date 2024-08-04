from typing import Mapping

from oci.monitoring.models import PostMetricDataDetails, PostMetricDataResponseDetails
from oci.response import Response

class MonitoringClient:
    base_client: object
    retry_strategy: object
    circuit_breaker_callback: object

    def __init__(  # noqa: PLR0913
        self,
        config: Mapping[str, object],
        *,
        service_endpoint: str | None = None,
        timeout: float | tuple[float, float] | None = None,
        signer: object = None,
        retry_strategy: object = None,
        circuit_breaker_strategy: object = None,
        circuit_breaker_callback: object = None,
        client_level_realm_specific_endpoint_template_enabled: bool | None = None,
        allow_control_chars: bool | None = None,
    ) -> None: ...
    def change_alarm_compartment(
        self,
        alarm_id: object,
        change_alarm_compartment_details: object,
        **kwargs: object,
    ) -> object: ...
    def create_alarm(
        self, create_alarm_details: object, **kwargs: object
    ) -> object: ...
    def create_alarm_suppression(
        self, create_alarm_suppression_details: object, **kwargs: object
    ) -> object: ...
    def delete_alarm(self, alarm_id: object, **kwargs: object) -> object: ...
    def delete_alarm_suppression(
        self, alarm_suppression_id: object, **kwargs: object
    ) -> object: ...
    def get_alarm(self, alarm_id: object, **kwargs: object) -> object: ...
    def get_alarm_history(self, alarm_id: object, **kwargs: object) -> object: ...
    def get_alarm_suppression(
        self, alarm_suppression_id: object, **kwargs: object
    ) -> object: ...
    def list_alarm_suppressions(self, alarm_id: object, **kwargs: object) -> object: ...
    def list_alarms(self, compartment_id: object, **kwargs: object) -> object: ...
    def list_alarms_status(
        self, compartment_id: object, **kwargs: object
    ) -> object: ...
    def list_metrics(
        self, compartment_id: object, list_metrics_details: object, **kwargs: object
    ) -> object: ...
    def post_metric_data(
        self,
        post_metric_data_details: PostMetricDataDetails,
        *,
        opc_request_id: str | None = None,
        content_encoding: str | None = None,
        retry_strategy: object = None,
        allow_control_chars: bool | None = None,
    ) -> Response[PostMetricDataResponseDetails, str]: ...
    def remove_alarm_suppression(
        self: object, alarm_id: object, **kwargs: object
    ) -> object: ...
    def retrieve_dimension_states(
        self: object, alarm_id: object, **kwargs: object
    ) -> object: ...
    def summarize_alarm_suppression_history(
        self: object, alarm_id: object, **kwargs: object
    ) -> object: ...
    def summarize_metrics_data(
        self: object,
        compartment_id: object,
        summarize_metrics_data_details: object,
        **kwargs: object,
    ) -> object: ...
    def update_alarm(
        self: object, alarm_id: object, update_alarm_details: object, **kwargs: object
    ) -> object: ...
