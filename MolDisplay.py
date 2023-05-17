# import the molecule module to access the functions of C file
import molecule

# defining constants
# radius = {'H': 25, 'C': 40, 'O': 40, 'N': 40, }
# element_name = {'H': 'grey', 'C': 'black', 'O': 'red', 'N': 'blue', }
header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""
footer = """</svg>"""
offsetx = 500
offsety = 500


class Atom:
    def __init__(self, c_atom):  # constructor to initialize the objects of Atom class
        self.c_atom = c_atom
        self.z = c_atom.z

    def __str__(self):  # method for debugging
        return self.c_atom.element, self.c_atom.x, self.c_atom.y, self.c_atom.z  # here

    def svg(self):  # method to return the strings that will help to display the atoms
        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (((self.c_atom.x * 100) + offsetx), ((self.c_atom.y * 100)+offsety), (radius[self.c_atom.element]), (element_name[self.c_atom.element]))


class Bond:
    def __init__(self, c_bond):  # constructor to initialize the objects of Bond class
        self.c_bond = c_bond
        self.z = c_bond.z

    def __str__(self):  # method for debugging
        return self.c_bond.a1, self.c_bond.a2, self.c_bond.epairs, self.c_bond.x1, self.c_bond.x2, self.c_bond.y1, self.c_bond.y2, self.c_bond.z, self.c_bond.len, self.c_bond.dx, self.c_bond.dy

    def svg(self):  # method to return the strings that will help to display the bonds
        # calculate the coordinates of the corners of the rectangle (representing a bond between atoms)
        centrex1 = (self.c_bond.x1 * 100) + offsetx
        centrey1 = (self.c_bond.y1 * 100) + offsety
        centrex2 = (self.c_bond.x2 * 100) + offsetx
        centrey2 = (self.c_bond.y2 * 100) + offsety

        # corners from centre1
        corner1x = centrex1 - (self.c_bond.dy*10)
        corner1y = centrey1 - (self.c_bond.dx*10)
        corner2x = centrex1 + (self.c_bond.dy*10)
        corner2y = centrey1 + (self.c_bond.dx*10)

        # corners from centre 2
        corner3x = centrex2 - (self.c_bond.dy*10)
        corner3y = centrey2 - (self.c_bond.dx*10)
        corner4x = centrex2 + (self.c_bond.dy*10)
        corner4y = centrey2 + (self.c_bond.dx*10)

        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (corner1x, corner2y, corner2x, corner1y, corner4x, corner3y, corner3x, corner4y)


class Molecule(molecule.molecule):
    def __str__(self):  # for debugging
        return self.atom_no, self.bond_no

    def svg(self):  # method to return the svg strings of atoms and bonds in order of increasing z values, to display the molecule
        storeList = header
        i = 0
        j = 0
        k = 0
        l = 0
        # using the merge sort algorithm to sort the atom and bond svg strings in order to display the correct molecule
        while ((i < self.atom_no) and (j < self.bond_no)):
            # instances of Atom and Bond created to access the svg strings for both
            objAtom = Atom(self.get_atom(i))
            objBond = Bond(self.get_bond(j))
            if (objAtom.z < objBond.z):
                storeList = storeList + objAtom.svg()
                i += 1
            else:
                storeList = storeList + objBond.svg()
                j += 1

        for k in range(i, self.atom_no):
            objAtom = Atom(self.get_atom(i))
            storeList = storeList + objAtom.svg()
            i += 1

        for l in range(j, self.bond_no):
            objBond = Bond(self.get_bond(j))
            storeList = storeList + objBond.svg()
            j += 1

        storeList = storeList + footer
        # print(storeList) #to debug
        return storeList  # returning the sorted svg strings

    def parse(self, fileObj):
        sdfLines = fileObj.readlines()
        totalLines = len(sdfLines)
        x = 0.0  # used to store the x-coordinate
        y = 0.0  # for y-coordinate
        z = 0.0  # for z-coordinate
        element = ""  # empty string to store the element name
        lineNum = 1
        word = ""
        # print(sdfLines)
        count = 0  # to count the total atoms read from the sdf file
        countB = 0  # to count the total bonds read from the sdf file

        # lineNum is used to skip the first four lines, and oneLine represents a line from the list sdfLines (which consists of all the lines of a .sdf file)
        for oneLine in sdfLines:
            if oneLine == "M END\n":
                break
            if lineNum == 1 or lineNum == 2 or lineNum == 3:
                # do nothing
                pass
            elif lineNum == 4:
                # print("HERE_MOLDISPLAY:",oneLine, lineNum)
                totalAtoms = int(oneLine[1:3].strip())
                totalBonds = int(oneLine[4:6].strip())
                # print("total atoms: ", totalAtoms)
                # print("total bonds: ", totalBonds)
            else:
                for char in oneLine:
                    lengthLine = len(oneLine)
                    # print(len(oneLine))
                    if count != totalAtoms:
                        x = float(oneLine[3:10].strip())
                        y = float(oneLine[13:20].strip())
                        z = float(oneLine[23:30].strip())
                        element = oneLine[31].strip()
                        # print(x, y, z, element)
                        # call append_atom
                        self.append_atom(element, x, y, z)
                        count += 1
                        break
                    elif countB != totalBonds:
                        a1 = int(oneLine[1:3].strip())
                        a2 = int(oneLine[4:6].strip())
                        epairs = int(oneLine[7:9])
                        # print(a1,a2,epairs)
                        # call append_bond
                        self.append_bond(a1-1, a2-1, epairs)
                        countB += 1
                        break
            lineNum += 1
