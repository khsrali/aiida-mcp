#!/usr/bin/env python3
"""
AiiDA Phonon Calculator MCP Server
Provides tools for AiiDA phonon band structure calculations
"""

import os
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aiida-mcp")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aiida-mcp.log'),
        logging.StreamHandler()
    ]
)

class AiidaMCPServer:
    def __init__(self):
        self.server = Server("aiida-phonon-calculator")
        self.templates_dir = Path(__file__).parent / "templates"
        self.config_dir = Path(__file__).parent / "configs"

        self.setup_handlers()

    def _load_template(self, filename: str) -> str:
        """Load template from file"""
        try:
            template_path = self.templates_dir / filename
            return template_path.read_text()
        except Exception as e:
            logger.error(f"Failed to load template {filename}: {e}")
            return f"Error loading template: {filename}"

    def setup_handlers(self):
        """Setup all MCP handlers"""

        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List available resources"""
            return [
                types.Resource(
                    uri="aiida://examples/phonon_workflow",
                    name="Phonon Workflow Example",
                    description="Template for phonon band structure calculations",
                    mimeType="text/x-python",
                ),
                types.Resource(
                    uri="aiida://config/codes",
                    name="AiiDA Codes Configuration",
                    description="YAML configurations for Quantum ESPRESSO and Phonopy",
                    mimeType="text/yaml",
                ),
                types.Resource(
                    uri="aiida://docs/workflow_guide",
                    name="Workflow Documentation",
                    description="Step-by-step guide for phonon calculations",
                    mimeType="text/markdown",
                ),
            ]

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a specific resource"""

            if uri == "aiida://examples/phonon_workflow":
                return self.get_phonon_workflow_template()
            elif uri == "aiida://config/codes":
                return self.get_code_configs()
            elif uri == "aiida://docs/workflow_guide":
                return self.get_workflow_guide()
            else:
                raise ValueError(f"Unknown resource: {uri}")

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="check_prerequisites",
                    description="Check if AiiDA codes and pseudopotentials are installed",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="install_code",
                    description="Install an AiiDA code from YAML configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code_type": {
                                "type": "string",
                                "enum": ["pw", "phonopy"],
                                "description": "Type of code to install"
                            }
                        },
                        "required": ["code_type"]
                    }
                ),
                types.Tool(
                    name="install_pseudopotentials",
                    description="Install pseudopotential library",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "library": {
                                "type": "string",
                                "default": "sssp",
                                "description": "Pseudopotential library"
                            },
                            "functional": {
                                "type": "string",
                                "default": "PBEsol",
                                "description": "Exchange-correlation functional"
                            },
                            "version": {
                                "type": "string",
                                "default": "1.3",
                                "description": "Library version"
                            }
                        },
                        "required": []
                    }
                ),
                types.Tool(
                    name="generate_phonon_script",
                    description="Generate Python script for phonon calculation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "material": {"type": "string"},
                            "structure_file": {"type": "string"},
                            "protocol": {
                                "type": "string",
                                "enum": ["fast", "moderate", "precise"],
                                "default": "moderate"
                            },
                            "kpoints": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "default": [3, 3, 3]
                            },
                            "supercell": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "default": [2, 2, 2]
                            },
                            "pw_code": {
                                "type": "string",
                                "default": "pw-7.3@localhost"
                            },
                            "phonopy_code": {
                                "type": "string",
                                "default": "phonopy@localhost"
                            }
                        },
                        "required": ["material", "structure_file"]
                    }
                ),
                types.Tool(
                    name="execute_calculation",
                    description="Execute the phonon calculation script",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "script_path": {
                                "type": "string",
                                "description": "Path to the Python script"
                            }
                        },
                        "required": ["script_path"]
                    }
                ),
                types.Tool(
                    name="check_calculation_status",
                    description="Check status of running calculations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "process_id": {
                                "type": "string",
                                "description": "Optional process ID to check specific calculation"
                            }
                        },
                        "required": []
                    }
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str,
            arguments: dict
        ) -> list[types.TextContent]:
            """Execute a tool"""

            if name == "check_prerequisites":
                return await self.check_prerequisites()
            elif name == "install_code":
                return await self.install_code(arguments["code_type"])
            elif name == "install_pseudopotentials":
                return await self.install_pseudopotentials(
                    arguments.get("library", "sssp"),
                    arguments.get("functional", "PBEsol"),
                    arguments.get("version", "1.3")
                )
            elif name == "generate_phonon_script":
                return await self.generate_phonon_script(**arguments)
            elif name == "execute_calculation":
                return await self.execute_calculation(arguments["script_path"])
            elif name == "check_calculation_status":
                return await self.check_calculation_status(
                    arguments.get("process_id")
                )
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def check_prerequisites(self) -> list[types.TextContent]:
        """Check if required codes and pseudopotentials are installed"""
        results = []

        # Check codes
        try:
            result = subprocess.run(
                ["verdi", "code", "list"],
                capture_output=True,
                text=True
            )
            codes = result.stdout

            has_pw = "pw-" in codes
            has_phonopy = "phonopy" in codes

            status = f"Code Status:\n"
            status += f"✓ Quantum ESPRESSO: {'Installed' if has_pw else 'Not found'}\n"
            status += f"✓ Phonopy: {'Installed' if has_phonopy else 'Not found'}\n"

            results.append(types.TextContent(
                type="text",
                text=status
            ))
        except Exception as e:
            results.append(types.TextContent(
                type="text",
                text=f"Error checking codes: {e}"
            ))

        # Check pseudopotentials
        try:
            result = subprocess.run(
                ["aiida-pseudo", "list"],
                capture_output=True,
                text=True
            )
            pseudos = result.stdout

            has_pbesol = "PBEsol" in pseudos

            status = f"\nPseudopotential Status:\n"
            status += f"✓ PBEsol: {'Installed' if has_pbesol else 'Not found'}\n"

            results.append(types.TextContent(
                type="text",
                text=status
            ))
        except Exception as e:
            results.append(types.TextContent(
                type="text",
                text=f"Error checking pseudopotentials: {e}"
            ))

        return results

    async def install_code(self, code_type: str) -> list[types.TextContent]:
        """Install an AiiDA code"""
        config_map = {
            "pw": "pw-7.3.yaml",
            "phonopy": "phonopy.yaml"
        }

        config_file = config_map.get(code_type)
        if not config_file:
            return [types.TextContent(
                type="text",
                text=f"Unknown code type: {code_type}"
            )]

        config_file_path = self.config_dir.joinpath(config_file)

        try:
            result = subprocess.run(
                ["verdi", "code", "create", "core.code.installed",
                 "--config", config_file_path, "--no-use-double-quotes"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return [types.TextContent(
                    type="text",
                    text=f"Successfully installed {code_type} code:\n{result.stdout}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Error installing {code_type}:\n{result.stderr}"
                )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Installation failed: {e}"
            )]

    async def install_pseudopotentials(
        self,
        library: str,
        functional: str,
        version: str
    ) -> list[types.TextContent]:
        """Install pseudopotential library"""
        try:
            result = subprocess.run(
                ["aiida-pseudo", "install", library,
                 "-x", functional, "-v", version],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return [types.TextContent(
                    type="text",
                    text=f"Successfully installed {functional} pseudopotentials:\n{result.stdout}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Error installing pseudopotentials:\n{result.stderr}"
                )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Installation failed: {e}"
            )]

    async def generate_phonon_script(
        self,
        material: str,
        structure_file: str,
        protocol: str = "moderate",
        kpoints: List[int] = None,
        supercell: List[int] = None,
        pw_code: str = "pw-7.3@localhost",
        phonopy_code: str = "phonopy@localhost"
    ) -> list[types.TextContent]:
        """Generate Python script for phonon calculation"""

        kpoints = kpoints or [3, 3, 3]
        supercell = supercell or [2, 2, 2]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_name = f"phonon_calculation_{material}_{timestamp}.py"

        # Load template and substitute variables
        script_template = self._load_template("phonon_script_template.py")
        script_content = script_template.format(
            material=material,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            structure_file=structure_file,
            protocol=protocol,
            supercell=supercell,
            kpoints=kpoints,
            pw_code=pw_code,
            phonopy_code=phonopy_code
        )

        # Save script to file
        script_path = Path.cwd() / script_name
        script_path.write_text(script_content)
        script_path.chmod(0o755)  # Make executable

        return [types.TextContent(
            type="text",
            text=f"Generated script: {script_path}\n\nScript saved with parameters:\n"
                 f"- Material: {material}\n"
                 f"- Structure: {structure_file}\n"
                 f"- Protocol: {protocol}\n"
                 f"- K-points: {kpoints}\n"
                 f"- Supercell: {supercell}\n"
                 f"- PW code: {pw_code}\n"
                 f"- Phonopy code: {phonopy_code}"
        )]

    async def execute_calculation(self, script_path: str) -> list[types.TextContent]:
        """Execute the phonon calculation script"""
        try:
            result = subprocess.run(
                ["verdi", "run", script_path],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Try to extract PK from output
                for line in result.stdout.split('\n'):
                    if 'pk:' in line:
                        # Extract number from line
                        import re
                        match = re.search(r'\d+', line)
                        if match:
                            pk = match.group()
                            break

                response = f"Calculation started successfully!\n{result.stdout}"
                if pk:
                    response += f"\n\nProcess ID: {pk}\n"
                    response += f"Monitor with: verdi process show {pk}"

                return [types.TextContent(type="text", text=response)]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Error starting calculation:\n{result.stderr}"
                )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Execution failed: {e}"
            )]

    async def check_calculation_status(
        self,
        process_id: Optional[str] = None
    ) -> list[types.TextContent]:
        """Check status of calculations"""
        try:
            if process_id:
                # Check specific process
                result = subprocess.run(
                    ["verdi", "process", "show", process_id],
                    capture_output=True,
                    text=True
                )
            else:
                # List all recent processes
                result = subprocess.run(
                    ["verdi", "process", "list", "-p", "5", "-a"],
                    capture_output=True,
                    text=True
                )

            return [types.TextContent(
                type="text",
                text=result.stdout if result.returncode == 0 else result.stderr
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error checking status: {e}"
            )]

    def get_phonon_workflow_template(self) -> str:
        """Return the phonon workflow template"""
        return self._load_template("phonon_workflow_template.py")

    def get_code_configs(self) -> str:
        """Return YAML configurations for codes"""
        return self._load_template("code_configs.yaml")

    def get_workflow_guide(self) -> str:
        """Return the workflow documentation"""
        return self._load_template("workflow_guide.md")

    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="aiida-phonon-calculator",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

if __name__ == "__main__":
    import asyncio
    server = AiidaMCPServer()
    asyncio.run(server.run())