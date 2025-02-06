import logging
import yaml
from sdcm.cluster import BaseNode
from sdcm.remote.remote_file import remote_file

LOGGER = logging.getLogger(__name__)


class IOTuneValidator:
    def __init__(self, node: BaseNode):
        self.node = node
        self.node_io_properties = {}

    def validate(self):
        self._run_io_tune()
        self._compare_results()

    def _read_io_properties(self, io_props_path="/etc/scylla.d/io_properties.yaml"):
        with remote_file(self.node.remoter, io_props_path) as f:
            return yaml.safe_load(f)

    def _run_io_tune(self, temp_props_path="/tmp/io_properties.yaml"):
        self.node.remoter.sudo(f"iotune  --evaluation-directory /var/lib/scylla --properties-file {temp_props_path}")
        self.node_io_properties = self._read_io_properties(temp_props_path)

        return self.node_io_properties

    def _compare_results(self):
        preset_io_props = self._read_io_properties()
        for key, value in self.node_io_properties.items():
            LOGGER.info("Comparing %s: %s vs %s", key, value, preset_io_props[key])
