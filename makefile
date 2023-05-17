all: _molecule.so

_molecule.so: molecule_wrap.o libmol.so
	clang -Wall -std=c99 -pedantic -dynamiclib -L. -L/usr/lib/python3.7/config-3.7m-x86_64-linux-gnu -lmol -lpython3.7m -shared molecule_wrap.o -o _molecule.so

molecule_wrap.o: swig3.0 molecule_wrap.c
	clang -Wall -std=c99 -pedantic -fPIC -I/usr/include/python3.7m -c molecule_wrap.c -o molecule_wrap.o

swig3.0: molecule.i
	swig3.0 -python molecule.i

libmol.so: mol.o
	clang -Wall -std=c99 -pedantic -shared mol.o -o libmol.so -lm

mol.o: mol.c mol.h
	clang -Wall -std=c99 -pedantic -c -fPIC mol.c -o mol.o

clean:
	rm *.o *.so
