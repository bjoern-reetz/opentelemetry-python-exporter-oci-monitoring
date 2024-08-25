from oci.monitoring import MonitoringClient

from opentelemetry_exporter_oci_monitoring import OCIMonitoringExporter
from opentelemetry_exporter_oci_monitoring.converter import DefaultMetricsConverter


def make_default_exporter(
    client: MonitoringClient,
    *,
    namespace: str,
    resource_group: str,
    compartment_id: str,
) -> OCIMonitoringExporter:
    return OCIMonitoringExporter(
        client=client,
        converter=DefaultMetricsConverter(
            namespace=namespace,
            resource_group=resource_group,
            compartment_id=compartment_id,
        ),
    )
