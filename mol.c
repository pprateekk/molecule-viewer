#include "mol.h"

/*
	this function sets the value of memebers in an atom struct with the values pointed to by element, x, y and z
*/
void atomset(atom *atom, char element[3], double *x, double *y, double *z)
{
	// copying the element
	strcpy(atom->element, element);
	// copying x, y, z positions
	atom->x = *x;
	atom->y = *y;
	atom->z = *z;
}

/*
	this function is used to get the values from an atom struct to locations pointed to by elements, x, y, and z
*/
void atomget(atom *atom, char element[3], double *x, double *y, double *z)
{
	// copying the element
	strcpy(element, atom->element);
	// copying x, y, z positions
	*x = atom->x;
	*y = atom->y;
	*z = atom->z;
}

/*
	this is the modified function used to set the values of the members in the new bond struct
*/
void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs)
{
	// copy the values pointed to by a1, a2, atoms, epairs
	bond->a1 = *a1;
	bond->a2 = *a2;
	bond->atoms = *atoms;
	bond->epairs = *epairs;
	compute_coords(bond);
}

/*
	this function has been modified to gets the values from the new bond struct
*/
void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs)
{
	// copy the struct attributes in bond to corresponding args.
	*a1 = bond->a1;
	*a2 = bond->a2;
	*atoms = bond->atoms;
	*epairs = bond->epairs;
}

/*
	allocating enough memory for a molecule
*/
molecule *molmalloc(unsigned short atom_max, unsigned short bond_max)
{
	molecule *memoryPointer = NULL;
	memoryPointer = malloc(sizeof(molecule)); // allocating memory to a molecule struct

	memoryPointer->atom_max = atom_max;
	memoryPointer->atom_no = 0;
	memoryPointer->bond_max = bond_max;
	memoryPointer->bond_no = 0;

	// allocating memory to *atoms and **atom_ptrs
	memoryPointer->atoms = malloc(sizeof(struct atom) * atom_max);
	memoryPointer->atom_ptrs = malloc(sizeof(struct atom *) * atom_max); // struct atom * - allocating memory for a pointer (pointing to atom )

	// allocating memory to *bonds and **bond_ptrs
	memoryPointer->bonds = malloc(sizeof(struct bond) * bond_max);
	memoryPointer->bond_ptrs = malloc(sizeof(struct bond *) * bond_max); // struct bond -  allocating memory for a pointer (pointing to atom variable)

	return memoryPointer;
}

molecule *molcopy(molecule *src)
{
	molecule *memPtrSrc = NULL;
	memPtrSrc = molmalloc(src->atom_max, src->bond_max); // allocating enough memory

	// append the atoms from src to the **atoms array (of memPtrSrc)
	for (int i = 0; i < src->atom_no; i++)
	{
		molappend_atom(memPtrSrc, &src->atoms[i]);
	}

	// append the bonds from src to the **atoms array (of memPtrSrc)
	for (int i = 0; i < src->bond_no; i++)
	{
		molappend_bond(memPtrSrc, &src->bonds[i]);
	}

	// assign the values from src to the new struct
	memPtrSrc->atom_no = src->atom_no;
	memPtrSrc->bond_no = src->bond_no;
	memPtrSrc->atom_max = src->atom_max;
	memPtrSrc->bond_max = src->bond_max;

	return memPtrSrc;
}

void molappend_atom(molecule *molecule, atom *atom)
{
	// printf("\nThe atom no. is: %d\n\n", molecule->atom_no);
	if (molecule->atom_no == molecule->atom_max)
	{
		if (molecule->atom_max == 0)
		{
			molecule->atom_max += 1;
		}
		else
		{
			molecule->atom_max = molecule->atom_max * 2;
		}
	}
	// realloc *atoms and **atom_ptrs
	molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
	molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom *) * molecule->atom_max);

	// after realloc, **atom_ptrs being pointed to corresponding *atoms
	for (int i = 0; i < molecule->atom_no; i++)
	{
		molecule->atom_ptrs[i] = &molecule->atoms[i];
	}

	// append the atom to *atoms, point **atom_ptrs to correct location, increment atom_no
	molecule->atoms[molecule->atom_no] = *atom;
	molecule->atom_ptrs[molecule->atom_no] = &molecule->atoms[molecule->atom_no];
	molecule->atom_no++;
}

void molappend_bond(molecule *molecule, bond *bond)
{
	if (molecule->bond_no == molecule->bond_max)
	{
		if (molecule->bond_max == 0)
		{
			molecule->bond_max += 1;
		}
		else
		{
			molecule->bond_max = molecule->bond_max * 2;
		}
	}

	// realloc *bonds and **bond_ptrs
	molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
	molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond *) * molecule->bond_max);
	bond->atoms = molecule->atoms; // added this for assignment 2

	// after realloc, **bond_ptrs being pointed to corresponding *bonds
	for (int i = 0; i < molecule->bond_no; i++)
	{
		molecule->bond_ptrs[i] = &molecule->bonds[i];
	}

	// append the bond to *bonds, point **bond_ptrs to correct location, increment bond_no
	molecule->bonds[molecule->bond_no] = *bond;
	molecule->bond_ptrs[molecule->bond_no] = &molecule->bonds[molecule->bond_no];
	molecule->bond_no++;
}

// assigning values to the matrix elements for rotation around x-axis
void xrotation(xform_matrix xform_matrix, unsigned short deg)
{
	double degToRadian;
	degToRadian = deg * (3.14159265358979323846264338327950288 / 180);
	xform_matrix[0][0] = 1;
	xform_matrix[0][1] = 0;
	xform_matrix[0][2] = 0;
	xform_matrix[1][0] = 0;
	xform_matrix[1][1] = cos(degToRadian);
	xform_matrix[1][2] = -sin(degToRadian);
	xform_matrix[2][0] = 0;
	xform_matrix[2][1] = sin(degToRadian);
	xform_matrix[2][2] = cos(degToRadian);
}

// assigning values to the matrix elements for rotation around y-axis
void yrotation(xform_matrix xform_matrix, unsigned short deg)
{
	double degToRadian;
	degToRadian = deg * (3.14159265358979323846264338327950288 / 180);
	xform_matrix[0][0] = cos(degToRadian);
	xform_matrix[0][1] = 0;
	xform_matrix[0][2] = sin(degToRadian);
	xform_matrix[1][0] = 0;
	xform_matrix[1][1] = 1;
	xform_matrix[1][2] = 0;
	xform_matrix[2][0] = -sin(degToRadian);
	xform_matrix[2][1] = 0;
	xform_matrix[2][2] = cos(degToRadian);
}

// assigning values to the matrix elements for rotation around z-axis
void zrotation(xform_matrix xform_matrix, unsigned short deg)
{
	double degToRadian;
	degToRadian = deg * (3.14159265358979323846264338327950288 / 180);
	xform_matrix[0][0] = cos(degToRadian);
	xform_matrix[0][1] = -sin(degToRadian);
	xform_matrix[0][2] = 0;
	xform_matrix[1][0] = sin(degToRadian);
	xform_matrix[1][1] = cos(degToRadian);
	xform_matrix[1][2] = 0;
	xform_matrix[2][0] = 0;
	xform_matrix[2][1] = 0;
	xform_matrix[2][2] = 1;
}

void mol_xform(molecule *molecule, xform_matrix matrix)
{
	double arrXYZAtom[3][1];	// matrix to x,y,z values from atoms
	double arrWithNewVal[3][1]; // matrix to store the new values of x,y,z

	for (int i = 0; i < molecule->atom_no; i++)
	{
		arrXYZAtom[0][0] = molecule->atoms[i].x;
		arrXYZAtom[1][0] = molecule->atoms[i].y;
		arrXYZAtom[2][0] = molecule->atoms[i].z;

		// vector-multiplication
		arrWithNewVal[0][0] = (matrix[0][0] * arrXYZAtom[0][0]) + (matrix[0][1] * arrXYZAtom[1][0]) + (matrix[0][2] * arrXYZAtom[2][0]);
		arrWithNewVal[1][0] = (matrix[1][0] * arrXYZAtom[0][0]) + (matrix[1][1] * arrXYZAtom[1][0]) + (matrix[1][2] * arrXYZAtom[2][0]);
		arrWithNewVal[2][0] = (matrix[2][0] * arrXYZAtom[0][0]) + (matrix[2][1] * arrXYZAtom[1][0]) + (matrix[2][2] * arrXYZAtom[2][0]);

		// updating the values x,y,z in the atoms
		molecule->atoms[i].x = arrWithNewVal[0][0];
		molecule->atoms[i].y = arrWithNewVal[1][0];
		molecule->atoms[i].z = arrWithNewVal[2][0];
	}

	// apply compute func to each bond in the molecule
	for (int i = 0; i < molecule->bond_no; i++)
	{
		compute_coords(&(molecule->bonds[i]));
	}
}

// freeing the memory of pointers
void molfree(molecule *ptr)
{
	free(ptr->atom_ptrs);
	free(ptr->atoms);

	free(ptr->bond_ptrs);
	free(ptr->bonds);

	free(ptr);
}

void molsort(molecule *molecule)
{
	qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(struct atom *), compareAtom); // to sort the atom_ptrs in increasing order of z values
	qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(struct bond *), bond_comp);   // to sort the bond_ptrs in increasing order of z values
}

int compareAtom(const void *a, const void *b)
{
	atom *Atom1, *Atom2; // atom struct to hold the values

	// dereferencing and casting the values to struct atom datatype to get z
	Atom1 = *(struct atom **)a;
	Atom2 = *(struct atom **)b;

	if (Atom1->z == Atom2->z)
	{
		return 0;
	}
	else if (Atom1->z > Atom2->z)
	{
		return 1;
	}
	else
	{
		return -1;
	}
}

/*
	new bond comparison function based on the new structure of the bond struct
*/
int bond_comp(const void *a, const void *b)
{
	bond *bond1, *bond2;

	// dereferencing and casting the values to struct bond datatype to get z
	bond1 = *(struct bond **)a;
	bond2 = *(struct bond **)b;

	if (bond1->z == bond2->z)
	{
		return 0;
	}
	else if (bond1->z > bond2->z)
	{
		return 1;
	}
	else
	{
		return -1;
	}
}

/*
	this function calculates the other values in struct bond
*/
void compute_coords(bond *bond)
{
	// compute z
	bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2;

	// update the x1, y1, x2, y2 for atom at indices a1, a2;
	bond->x1 = bond->atoms[bond->a1].x;
	bond->y1 = bond->atoms[bond->a1].y;
	bond->x2 = bond->atoms[bond->a2].x;
	bond->y2 = bond->atoms[bond->a2].y;

	// calc the distance
	double x1x2 = bond->x1 - bond->x2;
	double y1y2 = bond->y1 - bond->y2;
	bond->len = sqrt((x1x2 * x1x2) + (y1y2 * y1y2));
	// bond->len = sqrt(((bond->x1 * bond->x1) + (bond->x2 * bond->x2) - (2 * bond->x1 * bond->x2)) + ((bond->y1 * bond->y1) + (bond->y2 * bond->y2) - (2 * bond->y1 * bond->y2)));

	// calc dx and dy
	bond->dx = (bond->x2 - bond->x1) / bond->len;
	bond->dy = (bond->y2 - bond->y1) / bond->len;
}

rotations *spin( molecule *mol )
{
	//do something
	
}
void rotationsfree( rotations *rotations )
{
	//do something
}
