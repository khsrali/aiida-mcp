# AiiDA MCP Server for Phonon Calculations

A Model Context Protocol (MCP) server that provides tools for calculating phonon band structures using [AiiDA](https://www.aiida.net/) and [AiiDA-vibroscopy](https://aiida-vibroscopy.readthedocs.io/). This server enables AI assistants to help users set up, execute, and monitor phonon calculations through a conversational interface.

## Features

-  **Automated Setup**: Check and install prerequisites (Quantum ESPRESSO, Phonopy, pseudopotentials)
-  **Script Generation**: Create customized Python scripts for phonon calculations
-  **Execution Management**: Run calculations and monitor their progress
-  **Status Tracking**: Check calculation status and retrieve results
-  **AI-Friendly**: Designed for integration with Claude and other AI assistants via MCP

## Prerequisites

- Python 3.9+
- AiiDA installation with configured profile
- Quantum ESPRESSO (pw.x)
- Phonopy
- aiida-vibroscopy plugin

## Installation and Usage

1. Configure AiiDA (if not already done):
```bash
verdi quicksetup
verdi computer setup
verdi computer configure core.local localhost
```

2. Clone the repository:
```bash
git clone https://github.com/khsrali/aiida-mcp.git
cd aiida-mcp && pwd
```

3. Starting the MCP Server:
This codebase has been tested against Claude code

```bash
claude mcp add --scope user $(which python) <ABSOLUTE_PATH_TO_server.py>
```


## Configuration

The server uses YAML configuration files for code installation located in `configs/`:

- `pw-7.3.yaml`: Quantum ESPRESSO configuration
- `phonopy.yaml`: Phonopy configuration

This is only a proof of concept. In the future we could make these more generic, so that LLM would ask about specifics based on each users setup.


## How It Works: A Real Example

Imagine you're a researcher who needs to calculate phonon band structures and it's your first day of using AiiDA. Here's what a typical conversation looks like:

### The Magic of Natural Language

You simply ask: *"Please calculate phonons for silicon using AiiDA"*

What happens next is pretty cool. The AI assistant becomes your computational materials science expert. It checks if you have everything installed - Quantum ESPRESSO, Phonopy, the right pseudopotentials. If something's missing, it just... installs it for you. No googling installation guides, no debugging PATH issues.

### It Adopts with Your Specific Setup and Requests

The best part? It adapts to your environment. When I told it I had my own silicon CIF file, it immediately switched to using mine instead of trying to hallucinate. When I couldn't remember which compute node had my Quantum ESPRESSO installation, I literally said "I don't remember, find out yourself" - and it did! It found `pw-7.3@thor` and configured everything accordingly.

### Real Results, No Hassle

Within minutes, I had a phonon calculation running on our HPC cluster. The assistant generated a proper Python script, submitted it to AiiDA, and gave me the PK to monitor. When I asked about convergence, it pulled the actual SCF convergence data.

### Why This Matters

This isn't just about making things easier (though it definitely does that). It's about walking you through all the steps. Graduate students can focus on the science instead of debugging installation issues. Experimentalists can run calculations without becoming computational experts.

The MCP server acts as a bridge between the powerful but complex AiiDA framework and the intuitive conversational interface we all understand.

## Available MCP Tools

### `check_prerequisites`
Verifies installation of required codes and pseudopotentials.

### `install_code` 
Installs Quantum ESPRESSO or Phonopy codes from YAML configurations.
- Parameters: `code_type` (pw/phonopy)

### `install_pseudopotentials`
Installs pseudopotential libraries.
- Parameters: `library`, `functional`, `version`

### `generate_phonon_script`
Creates customized Python script for phonon calculations.
- Parameters: `material`, `structure_file`, `protocol`, `kpoints`, `supercell`, `pw_code`, `phonopy_code`

### `execute_calculation`
Runs the generated phonon calculation script.
- Parameters: `script_path`

### `check_calculation_status`
Monitors running calculations and retrieves status.
- Parameters: `process_id` (optional)

## Project Structure

```
aiida-mcp/
├── server.py                 # Main MCP server implementation
├── configs/                  # Code configuration files
│   ├── pw-7.3.yaml          # Quantum ESPRESSO config
│   └── phonopy.yaml         # Phonopy config
├── templates/               # Script and documentation templates
│   ├── phonon_script_template.py
│   ├── phonon_workflow_template.py
│   └── workflow_guide.md
├── prompts/                 # AI assistant instructions
│   └── aiida_phonon.md     # Detailed workflow protocol
├── aiida-mcp.log           # Server logs
└── README.md               # This file
```

## Advanced Features

### Custom Protocols
Modify calculation accuracy with three preset protocols:
- `fast`: Quick testing, lower accuracy
- `moderate`: Balanced accuracy and speed  
- `precise`: High accuracy, longer runtime

### Flexible Parameters
- K-points mesh density (e.g., 3×3×3 for testing, 6×6×6 for production)
- Supercell size for phonon calculations
- Custom convergence thresholds
- Q-point paths for band structure


## Acknowledgments

- [AiiDA](https://www.aiida.net/) team for the computational infrastructure
- [AiiDA-vibroscopy](https://aiida-vibroscopy.readthedocs.io/) developers

## References

- [AiiDA Documentation](https://aiida.readthedocs.io/)
- [AiiDA-vibroscopy Documentation](https://aiida-vibroscopy.readthedocs.io/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Quantum ESPRESSO](https://www.quantum-espresso.org/)
