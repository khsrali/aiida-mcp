# AiiDA Phonon Calculation Workflow Guide

## Prerequisites
1. AiiDA installation with profile configured
2. Quantum ESPRESSO (pw.x) installed
3. Phonopy installed
4. aiida-vibroscopy plugin installed
5. Pseudopotentials (PBEsol recommended)

## Step-by-Step Process

### 1. Setup Check
- Verify codes: `verdi code list`
- Check pseudopotentials: `aiida-pseudo list`
- Ensure computer is configured: `verdi computer list`

### 2. Prepare Structure
- Obtain CIF or POSCAR file for your material
- Can download from Materials Project or other databases
- Ensure structure is properly formatted

### 3. Configure Calculation Parameters
- **Protocol**: fast/moderate/precise
- **K-points mesh**: Density for SCF calculation
- **Supercell size**: For phonon displacement calculations
- **Codes**: Select appropriate QE and Phonopy codes

### 4. Run Calculation
- Execute the generated Python script
- Monitor with verdi process commands
- Check for convergence and errors

### 5. Retrieve Results
- Export band structure data
- Visualize phonon dispersion
- Calculate phonon DOS if needed

## Common Issues
- Memory errors: Reduce supercell size or k-points
- Convergence issues: Adjust SCF parameters
- Missing features: Check aiida-vibroscopy version