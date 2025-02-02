"""FlexLM license server interface."""
import typing

from lm_agent.backend_utils.models import LicenseServerSchema
from lm_agent.config import settings
from lm_agent.exceptions import LicenseManagerBadServerOutput
from lm_agent.parsing import flexlm
from lm_agent.server_interfaces.license_server_interface import LicenseReportItem, LicenseServerInterface
from lm_agent.utils import run_command


class FlexLMLicenseServer(LicenseServerInterface):
    """Extract license information from FlexLM license server."""

    def __init__(self, license_servers: typing.List[LicenseServerSchema]):
        self.license_servers = license_servers
        self.parser = flexlm.parse

    def get_commands_list(self) -> typing.List[typing.List[str]]:
        """Generate a list of commands with the available license server hosts."""

        commands_to_run = []
        for license_server in self.license_servers:
            command_line = [
                f"{settings.LMUTIL_PATH}",
                "lmstat",
                "-c",
                f"{license_server.port}@{license_server.host}",
                "-f",
            ]
            commands_to_run.append(command_line)
        return commands_to_run

    async def get_output_from_server(self, product_feature: str):
        """Override abstract method to get output from FlexLM license server."""

        # get the list of commands for each license server host
        commands_to_run = self.get_commands_list()

        # run each command in the list, one at a time, until one succeds
        for cmd in commands_to_run:
            (_, feature) = product_feature.split(".")
            cmd.append(feature)
            output = await run_command(cmd)

            # try the next server if the previous didn't return the expected data
            if not output:
                continue
            return output

        raise RuntimeError("None of the checks for FlexLM succeeded!")

    async def get_report_item(self, product_feature: str):
        """Override abstract method to parse FlexLM license server output into License Report Item."""

        server_output = await self.get_output_from_server(product_feature)
        parsed_output = self.parser(server_output)

        # raise exception if parser didn't output license information
        if parsed_output.get("total") is None or any(
            [
                parsed_output.get("total", {}).get("used") is None,
                parsed_output.get("total", {}).get("total") is None,
            ]
        ):
            raise LicenseManagerBadServerOutput("Invalid data returned from parser.")

        report_item = LicenseReportItem(
            product_feature=product_feature,
            used=parsed_output["total"]["used"],
            total=parsed_output["total"]["total"],
        )

        return report_item
