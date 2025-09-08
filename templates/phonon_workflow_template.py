from aiida import load_profile
from aiida.plugins import DbImporterFactory
from ase import io
from aiida import orm
from aiida.plugins import WorkflowFactory
from aiida.engine import run_get_node
from aiida_vibroscopy.common.properties import PhononProperty

load_profile()

# Load structure
structure = io.read('Si_mp-149_primitive.cif')

# Setup workflow
PhononWorkChain = WorkflowFactory("vibroscopy.phonons.phonon")
builder = PhononWorkChain.get_builder_from_protocol(
    pw_code=orm.load_code('pw-7.3@thor'),
    structure=orm.StructureData(ase=structure),
    protocol="fast",
    phonopy_code=orm.load_code('phonopy@localhost'),
    phonon_property=PhononProperty.BANDS
)

# Configure parameters
builder.supercell_matrix = orm.List([1,1,1])
builder.scf.kpoints = orm.KpointsData()
builder.scf.kpoints.set_kpoints_mesh([3,3,3])

# Run calculation
results, calc = run_get_node(builder)