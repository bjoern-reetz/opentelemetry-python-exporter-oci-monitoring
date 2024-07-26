from typing import Any

from oci.monitoring.models import PostMetricDataDetails, PostMetricDataResponseDetails
from oci.response import Response

class MonitoringClient:
    def post_metric_data(
        self,
        post_metric_data_details: PostMetricDataDetails,
        /,
        opc_request_id: str | None = None,
        content_encoding: str | None = None,
        retry_strategy: Any = None,  # noqa: ANN401
        allow_control_chars: bool | None = None,
    ) -> Response[PostMetricDataResponseDetails, str]: ...
