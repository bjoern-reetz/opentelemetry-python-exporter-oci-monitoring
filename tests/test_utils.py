from unittest.mock import NonCallableMock

from opentelemetry_exporter_oci_monitoring import OCIMonitoringExporter
from opentelemetry_exporter_oci_monitoring.converter import DefaultMetricsConverter
from opentelemetry_exporter_oci_monitoring.utils import make_default_exporter


def test_make_default_exporter(monitoring_client: NonCallableMock) -> None:
    namespace = "my-ns"
    resource_group = "my-res-grp"
    compartment_id = "ocid.compartment.abc123"

    exporter = make_default_exporter(
        monitoring_client,
        namespace=namespace,
        resource_group=resource_group,
        compartment_id=compartment_id,
    )
    assert isinstance(exporter, OCIMonitoringExporter)
    assert exporter.client is monitoring_client

    converter = exporter.converter
    assert isinstance(converter, DefaultMetricsConverter)
    assert converter.namespace == namespace
    assert converter.resource_group == resource_group
    assert converter.compartment_id == compartment_id
