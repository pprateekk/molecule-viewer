import sqlite3
import os
import MolDisplay


class Database:
    # creating and opening a database connection to molecules.db
    def __init__(self, reset=False):
        if (reset == True):
            if os.path.exists('molecules.db'):
                os.remove('molecules.db')
        self.conn = sqlite3.connect('molecules.db')
        self.conn.commit()
        # self.conn.isolation_level = None

    # check if the table already exists, if yes: do not recreate, else: create
    def create_tables(self):
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Elements 
							( 	ELEMENT_NO	INTEGER NOT NULL,
								ELEMENT_CODE VARCHAR(3) NOT NULL,
								ELEMENT_NAME VARCHAR(32) NOT NULL,
								COLOUR1	CHAR(6) NOT NULL,
								COLOUR2	CHAR(6) NOT NULL,
								COLOUR3	CHAR(6) NOT NULL,
								RADIUS DECIMAL(3) NOT NULL,
								PRIMARY KEY (ELEMENT_CODE) );""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS Atoms
							(	ATOM_ID	INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
								ELEMENT_CODE	VARCHAR(3) NOT NULL,
								X	DECIMAL(7,4) NOT NULL,
								Y	DECIMAL(7,4) NOT NULL,
								Z	DECIMAL(7,4) NOT NULL,
								FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements);""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS Bonds
							(	BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
								A1 INTEGER	NOT NULL, 
								A2 INTEGER 	NOT NULL, 
								EPAIRS	INTEGERS NOT NULL);""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS Molecules
							(	MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
								NAME TEXT UNIQUE NOT NULL);""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeAtom
							(	MOLECULE_ID INTEGER NOT NULL, 
								ATOM_ID	INTEGER NOT NULL,
								PRIMARY KEY (MOLECULE_ID, ATOM_ID)
								FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules, 
								FOREIGN KEY (ATOM_ID) REFERENCES Atoms);""")

        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeBond
							(	MOLECULE_ID INTEGER NOT NULL,
								BOND_ID	INTEGER	NOT NULL, 
								PRIMARY KEY (MOLECULE_ID, BOND_ID),
								FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules, 
								FOREIGN KEY (BOND_ID) REFERENCES Bonds);""")
        # self.conn.commit()

        # populating the table with the given values
    def __setitem__(self, table, values):
        execute_query = f"INSERT INTO {table} VALUES {values};"
        self.conn.execute(execute_query)
        self.conn.commit()

        # populating the Atoms table with the attributes of object atom
    def add_atom(self, molname, atom):
        # atom - object (MolDisplay)
        element_atomname = atom.element
        element_x = atom.x
        element_y = atom.y
        element_z = atom.z
        execute_query = "INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES ('{}', '{}', '{}', '{}');".format(
            element_atomname, element_x, element_y, element_z)
        self.conn.execute(execute_query)
        # self.conn.commit()
        

        # add in MoleculeAtom table - link molname to the atom entry in the atoms table
        execute_query2 = "SELECT ATOM_ID FROM Atoms WHERE ELEMENT_CODE = '{}' AND X = '{}' AND Y = '{}' AND Z = '{}';".format(
            element_atomname, element_x, element_y, element_z)
        atomId = self.conn.execute(execute_query2).fetchone()[0]
        # print(atomId);
        execute_query3 = "SELECT MOLECULE_ID FROM Molecules WHERE NAME = '{}'".format(
            molname)
        moleculeId = self.conn.execute(execute_query3).fetchone()[0]
        # print(moleculeId);
        execute_query4 = "INSERT INTO MoleculeAtom VALUES ('{}', '{}');".format(
            moleculeId, atomId)
        self.conn.execute(execute_query4)
        self.conn.commit()
        
        

        # populating the Bonds table with the attributes of object bond
    def add_bond(self, molname, bond):
        ele_a1 = bond.a1
        ele_a2 = bond.a2
        ele_epairs = bond.epairs
        execute_query = "INSERT INTO Bonds (A1, A2, EPAIRS) VALUES ('{}', '{}', '{}');".format(
            ele_a1, ele_a2, ele_epairs)
        self.conn.execute(execute_query)
        # self.conn.commit()
        # link
        execute_query2 = "SELECT BOND_ID FROM Bonds WHERE A1 = '{}' AND A2 = '{}' AND EPAIRS = '{}';".format(
            ele_a1, ele_a2, ele_epairs)
        bondId = self.conn.execute(execute_query2).fetchone()[0]
        # print(bondId);
        execute_query3 = "SELECT MOLECULE_ID FROM Molecules WHERE NAME = '{}';".format(
            molname)
        moleculeId = self.conn.execute(execute_query3).fetchone()[0]
        # print(moleculeId);
        execute_query4 = "INSERT INTO MoleculeBond VALUES ('{}', '{}');".format(
            moleculeId, bondId)
        self.conn.execute(execute_query4)
        self.conn.commit()

        # populating Molecules table with the name
    def add_molecule(self, name, fp):
        # create MolDisplay.Molecule object
        newMol = MolDisplay.Molecule()
        newMol.parse(fp)
        # add entry to Molecules table
        execute_query = "INSERT INTO Molecules (NAME) VALUES ('{}');".format(
            name)
        self.conn.execute(execute_query)
        self.conn.commit()
        # call add_atom add_bond for each atom bond from get_atom get_bond methods of molecule - its in MolDisplay
        # add_atom(name, get_atom(i)) inside a for loop i < atom_no and j < bond.no
        i = 0
        j = 0
        for i in range(newMol.atom_no):
            objAtom = newMol.get_atom(i)
            self.add_atom(name, objAtom)

        for j in range(newMol.bond_no):
            objBond = newMol.get_bond(j)
            self.add_bond(name, objBond)

        # returning a Molecule object
    def load_mol(self, name):
        newestMol = MolDisplay.Molecule()
        query = "SELECT ELEMENT_CODE, X, Y, Z FROM Atoms INNER JOIN Molecules ON Molecules.MOLECULE_ID=MoleculeAtom.MOLECULE_ID INNER JOIN MoleculeAtom ON MoleculeAtom.ATOM_ID = Atoms.ATOM_ID WHERE Molecules.NAME = '{}' ORDER BY Atoms.ATOM_ID;".format(
            name)
        tupleAtomId = self.conn.execute(query).fetchall()
        # print(type(tupleAtomId));
        # print(tupleAtomId[0]);
        # print(tupleAtomId[0][0]);
        i = 0
        k = 0
        for i in tupleAtomId:
            newestMol.append_atom(
                tupleAtomId[k][0], tupleAtomId[k][1], tupleAtomId[k][2], tupleAtomId[k][3])
            k += 1

        query2 = "SELECT A1, A2, EPAIRS FROM Bonds INNER JOIN Molecules ON Molecules.MOLECULE_ID=MoleculeBond.MOLECULE_ID INNER JOIN MoleculeBond ON MoleculeBond.BOND_ID = Bonds.BOND_ID WHERE Molecules.NAME = '{}' ORDER BY Bonds.BOND_ID;".format(
            name)
        tupleBondId = self.conn.execute(query2).fetchall()
        j = 0
        l = 0
        # print(tupleBondId);
        for j in tupleBondId:
            newestMol.append_bond(
                tupleBondId[l][0], tupleBondId[l][1], tupleBondId[l][2])
            l += 1

        return newestMol

    def radius(self):
        query = "SELECT ELEMENT_CODE, RADIUS FROM Elements;"
        dicInfo = self.conn.execute(query).fetchall()
        # print(dicInfo);
        retDict = {}
        i = 0
        j = 0
        for i in dicInfo:
            retDict[dicInfo[j][0]] = dicInfo[j][1]
            j += 1
        # print(retDict)
        return retDict

    def element_name(self):
        query = "SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements;"
        dicInfo = self.conn.execute(query).fetchall()
        retDict = {}
        i = 0
        j = 0
        for i in dicInfo:
            retDict[dicInfo[j][0]] = dicInfo[j][1]
            j += 1
        # print(retDict)

        return retDict

    def radial_gradients(self):
        query = "SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements;"
        newList = self.conn.execute(query).fetchall()
        i = 0
        j = 0
        retString = ""
        for i in newList:
            radialGradientSVG = """
				<radialGradient id="{}" cx="-50%" cy="-50%" r="220%" fx="20%" fy="20%">
					<stop offset="0%" stop-color="#{}"/> 
					<stop offset="50%" stop-color="#{}"/> 
					<stop offset="100%" stop-color="#{}"/>
					</radialGradient>""".format(newList[j][0], newList[j][1], newList[j][2], newList[j][3])
            # radialGradientSVG = """
            # 	<radialGradient id="{}" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
            # 		<stop offset="0%%" stop-color="#{}"/>
            # 		<stop offset="50%%" stop-color="#{}"/>
            # 		<stop offset="100%%" stop-color="#{}"/>
            # 		</radialGradient>""".format(newList[j][0], newList[j][1], newList[j][2], newList[j][3])
            retString = retString + radialGradientSVG
            j += 1
        # print(retString);
        return retString
