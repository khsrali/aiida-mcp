#!/usr/bin/env python3
"""
Phonon band structure calculation for {material}
Generated on {timestamp}
"""

from aiida import load_profile
from aiida.plugins import DbImporterFactory
from ase import io
from aiida import orm
from aiida.plugins import WorkflowFactory
from aiida.engine import run_get_node
from aiida_vibroscopy.common.properties import PhononProperty

# Load AiiDA profile
load_profile()

print("Starting phonon calculation for {material}")
print("=" * 50)

# Load structure
print("Loading structure from: {structure_file}")
structure = io.read('{structure_file}')

# Setup workflow
PhononWorkChain = WorkflowFactory("vibroscopy.phonons.phonon")

print("Building workflow with protocol: {protocol}")
builder = PhononWorkChain.get_builder_from_protocol(
    pw_code=orm.load_code('{pw_code}'),
    structure=orm.StructureData(ase=structure),
    protocol="{protocol}",
    phonopy_code=orm.load_code('{phonopy_code}'),
    phonon_property=PhononProperty.BANDS
)

# Configure parameters
print("Setting supercell: {supercell}")
builder.supercell_matrix = orm.List({supercell})

print("Setting k-points mesh: {kpoints}")
builder.scf.kpoints = orm.KpointsData()
builder.scf.kpoints.set_kpoints_mesh({kpoints})

# Run calculation
print("Submitting calculation...")
results, calc = run_get_node(builder)

print(f"Calculation submitted with PK: {{calc.pk}}")
print("=" * 50)
print("Monitor progress with:")
print(f"  verdi process show {{calc.pk}}")
print(f"  verdi process report {{calc.pk}}")
print("=" * 50)

# Save process ID for reference
with open("last_calculation_pk.txt", "w") as f:
    f.write(str(calc.pk))

print("Process ID saved to: last_calculation_pk.txt")