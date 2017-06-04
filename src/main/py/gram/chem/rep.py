from rdkit import Chem
import gram.fol.rep as fol

# Energies of atoms for computing atomization energies for molecules
#=========================================================================================================
#  Ele-    ZPVE         U (0 K)      U (298.15 K)    H (298.15 K)    G (298.15 K)     CV
#  ment   Hartree       Hartree        Hartree         Hartree         Hartree        Cal/(Mol Kelvin)
#=========================================================================================================
#   H     0.000000     -0.500273      -0.498857       -0.497912       -0.510927       2.981
#   C     0.000000    -37.846772     -37.845355      -37.844411      -37.861317       2.981
#   N     0.000000    -54.583861     -54.582445      -54.581501      -54.598897       2.981
#   O     0.000000    -75.064579     -75.063163      -75.062219      -75.079532       2.981
#   F     0.000000    -99.718730     -99.717314      -99.716370      -99.733544       2.981
#=========================================================================================================
U_0_H = -0.500273
U_0_C = -37.846772
U_0_N = -54.583861
U_0_O = -75.064579
U_0_F = -99.718730

# Properties (unary) and relations (binary) for FOL relational structures
# NOTE: It's necessary that predicate names are greater than one character
# so that nltk doesn't stupidly treat them as variables... :(
ATOMIC_PROPERTIES = ["H_e", "C_e", "N_e", "O_e", "F_e"]
ATOMIC_RELATIONS = Chem.rdchem.BondType.names.keys()
ATOMIC_RELATIONS_LOADED = set([])

ATOMIC_PROPERTY_INDICES = dict()
ATOMIC_RELATION_INDICES = dict()
for i in range(len(ATOMIC_PROPERTIES)):
    ATOMIC_PROPERTY_INDICES[ATOMIC_PROPERTIES[i]] = i
for i in range(len(ATOMIC_RELATIONS)):
    ATOMIC_RELATION_INDICES[ATOMIC_RELATIONS[i]] = i 


class PositionedAtom:
    def __init__(self, index, element, x, y, z, Z_part):
        self._index = index
        self._element = element
        self._x = x
        self._y = y
        self._z = z
        self._Z_part = Z_part

    def get_index(self):
        return self._index

    def get_element(self):
        return self._element + "_e"

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_z(self):
        return self._z

    def get_Z_part(self):
        return self._Z_part
    
    def get_Z(self):
        if self._element == "C":
            return 6.0
        elif self._element == "H":
            return 1.0
        elif self._element == "O":
            return 8.0
        elif self._element == "N":
            return 7.0
        elif self._element == "F":
            return 9.0
        else:
            return None

    def get_U_0(self):
        if self._element == "C":
            return U_0_C
        elif self._element == "H":
            return U_0_H
        elif self._element == "O":
            return U_0_O
        elif self._element == "N":
            return U_0_N
        elif self._element == "F":
            return U_0_F
        else:
            return None

    def __str__(self):
        return self._element + "(" + str(self._index) + ")"


class Bond:
    def __init__(self, atom_0, atom_1, bond_type):
        self._atom_0 = atom_0
        self._atom_1 = atom_1
        self._bond_type = bond_type

    def get_first_atom(self):
        return self._atom_0

    def get_second_atom(self):
        return self._atom_1

    def get_bond_type(self):
        return self._bond_type

    def __str__(self):
        return str(self._atom_0) + "-" + self._bond_type + "-" + str(self._atom_1)


class Molecule:
    def __init__(self):
        pass

    def get_n_a(self):
        return self._n_a

    def get_n_b(self):
        return len(self._bonds)

    def get_model(self):
        return self._model

    def get_property(self, name):
        return self._props[name]

    def get_atom(self, index):
        return self._atoms[index]

    def get_bond(self, index):
        return self._bonds[index]

    def get_freq_count(self):
        return len(self._freqs)

    def get_freq(self, index):
        return self._freqs[index]

    def get_SMILES(self):
        return self._SMILES

    def get_model(self):
        return self._model

    @staticmethod
    def from_xyz(xyz):
        m = Molecule()
        lines = xyz.split("\n")

        # Line 1 (number of atoms)
        m._n_a = int(lines[0])

        # Line 2
        props = lines[1].split("\t")
        m._props = dict()
        m._props["id"] = props[0] # String identifier
        m._props["A"] = float(props[1].replace("*^", "E")) # A (GHz) - Rotational constant
        m._props["B"] = float(props[2].replace("*^", "E")) # B (GHz) - Rotational constant
        m._props["C"] = float(props[3].replace("*^", "E")) # C (GHz) - Rotational constant
        m._props["mu"] = float(props[4].replace("*^", "E")) # mu (D) - Dipole moment
        m._props["alpha"] = float(props[5].replace("*^", "E")) # alpha (a_0^3) - Isotropic polarizability
        m._props["epsilon_HOMO"] = float(props[6].replace("*^", "E")) # epsilon_HOMO (Ha) - Energy of HOMO
        m._props["epsilon_LUMO"] = float(props[7].replace("*^", "E")) # epsilon_LUMO (Ha) - Energy of LUMO
        m._props["epsilon_gap"] = float(props[8].replace("*^", "E")) # epsilon_gap (Ha) - Energy gap
        m._props["R2"] = float(props[9].replace("*^", "E")) # R^2 (a_0^2) - Electronic spatial extent
        m._props["zpve"] = float(props[10].replace("*^", "E")) # zpve (Ha) - Zero point vibrational energy
        m._props["U_0"] = float(props[11].replace("*^", "E")) # U_0 (Ha) - Internal energy at 0K
        m._props["U"] = float(props[12].replace("*^", "E")) # U (Ha) - Internal energy at 298.15K
        m._props["H"] = float(props[13].replace("*^", "E")) # H (Ha) - Enthalpy at 298.15K
        m._props["G"] = float(props[14].replace("*^", "E")) # G (Ha) - Free energy at 298.15K
        m._props["C_v"] = float(props[15].replace("*^", "E")) # C_v (cal/molK) - Heat capacity at 298.15K
        m._props["E_atomization"] = m._props["U_0"]
        
        m._atoms = []
        for i in range(2, m._n_a+2):
            xyz_props = lines[i].split("\t")
            element = xyz_props[0] # element symbol
            x = float(xyz_props[1].replace("*^", "E")) # x (angstrom) - X coordinate
            y = float(xyz_props[2].replace("*^", "E")) # y (angstrom) - Y coordinate
            z = float(xyz_props[3].replace("*^", "E")) # z (angstrom) - Z coordinate
            Z_part = float(xyz_props[4].replace("*^", "E")) # Z_part (e) - Mulliken partial charge 
            
            atom = PositionedAtom(i, element, x, y, z, Z_part)
            m._props["E_atomization"] -= atom.get_U_0()

            m._atoms.append(atom)

        freq_props = lines[m._n_a+2].split("\t")
        m._freqs = [float(freq_prop.replace("*^", "E")) for freq_prop in freq_props]
        
        SMILES = lines[m._n_a+3].strip().split("\t")
        m._SMILES = SMILES[len(SMILES)-1]

        # RDKit model
        m_rd = Chem.AddHs(Chem.MolFromSmiles(m._SMILES))
       
        # Make bond list
        m._bonds = []
        for i in range(m_rd.GetNumBonds()):
            bond_i = m_rd.GetBondWithIdx(i)
            bond_type = str(bond_i.GetBondType())
            begin_atom = str(bond_i.GetBeginAtomIdx())
            end_atom = str(bond_i.GetEndAtomIdx())
            m._bonds.append(Bond(m._atoms[bond_i.GetBeginAtomIdx()], m._atoms[bond_i.GetEndAtomIdx()], bond_type))
            ATOMIC_RELATIONS_LOADED.add(bond_type)

        #### FOL Relational structure ####
        domain = [str(i) for i in range(m_rd.GetNumAtoms())]
        properties = ATOMIC_PROPERTIES
        binary_rels = ATOMIC_RELATIONS
        
        property_sets = [set([]) for i in range(len(properties))]
        binary_rel_sets = [set([]) for i in range(len(binary_rels))]

        v = []
        for i in range(len(domain)):
            v.append((domain[i], domain[i]))
            element_i = m._atoms[i].get_element()
            element_property_index = ATOMIC_PROPERTY_INDICES[element_i]
            property_sets[element_property_index].add(domain[i])

        for i in range(m_rd.GetNumBonds()):
            bond_i = m_rd.GetBondWithIdx(i)
            bond_type = str(bond_i.GetBondType())
            begin_atom = str(bond_i.GetBeginAtomIdx())
            end_atom = str(bond_i.GetEndAtomIdx())
            bond_property_index = ATOMIC_RELATION_INDICES[bond_type]
            binary_rel_sets[bond_property_index].add((begin_atom, end_atom))
            # Keeping this makes double counts on satisfying bonds between common elements
            # When computing bond counts
            binary_rel_sets[bond_property_index].add((end_atom, begin_atom))

        for i in range(len(property_sets)):
            v.append((properties[i], property_sets[i]))

        for i in range(len(binary_rel_sets)):
            v.append((binary_rels[i], binary_rel_sets[i]))

        m._model = fol.RelationalModel(domain, properties, binary_rels, v)
        #### END FOL ####

        return m

    def get_structure_str(self):
        s = ""

        for i in range(len(self._bonds)):
            s += str(self._bonds[i]) + "\n"

        return s


    @staticmethod
    def from_xyz_file(file_path):
        xyz = None
        with open(file_path, 'r') as content_file:
             xyz = content_file.read()
        return Molecule.from_xyz(xyz)

