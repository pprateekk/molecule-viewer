import sys  # to get the port number from the user as a command-line argument
from http.server import HTTPServer, BaseHTTPRequestHandler
import MolDisplay
import io  # for TextIOWrapper
import urllib  # code to parse for data
import molsql
import json

allFiles = ['/webPage.html', '/webPageStyle.css', '/webPageScript.js', '/mol6.png'];

database = molsql.Database(reset=True)
database.create_tables()
database['Elements'] = (1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25)
database['Elements'] = (6, 'C', 'Carbon', '808080', '010101', '000000', 40)
database['Elements'] = (7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40)
database['Elements'] = (8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40)
allMolecules = [] #a list to store all the name of the molecules added
uploadMol = {} #a dict to store the contents of svg for each molecule
uploadMolAtom = {}
uploadMolBond = {}

# fp = open('water-3D-structure-CT1000292221.sdf')
# database.add_molecule('Water', fp)
# fp = open('caffeine-3D-structure-CT1001987571.sdf')
# database.add_molecule('Caffeine', fp)
# print(database.conn.execute("SELECT * FROM Molecules;").fetchall())
# print(database.conn.execute("SELECT * FROM Atoms;").fetchall())
# print(database.conn.execute("SELECT * FROM Bonds;").fetchall())
# print(database.conn.execute("SELECT * FROM MoleculeAtom;").fetchall())
# print(database.conn.execute("SELECT * FROM MoleculeBond;").fetchall())

class serverHandler (BaseHTTPRequestHandler):
    def do_GET(self):
        # for self.path in allFiles:
        if self.path in allFiles:
            # print(self.path);
            self.send_response(200)
            if self.path == '/webPageStyle.css':
                self.send_header("Content-type", "text/css")
                filePointer = open(self.path[1:])
                webPage = filePointer.read()
                filePointer.close()
                self.send_header("Content-length", len(webPage))
                self.end_headers()
                self.wfile.write(bytes(webPage, "utf-8"))
            elif self.path == '/mol6.png':
                self.send_header("Content-type", "image/png")
                fileImage = open(self.path[1:], 'rb')
                pngData = fileImage.read()
                byteObject = io.BytesIO(pngData)
                byteObject.seek(0,2)
                pngLength = byteObject.tell()
                self.send_header("Content-length", pngLength)
                self.end_headers()
                self.wfile.write(pngData)
            else:
                self.send_header("Content-type", "text/html")
                filePointer = open(self.path[1:])
                webPage = filePointer.read()
                filePointer.close()
                self.send_header("Content-length", len(webPage))
                self.end_headers()
                self.wfile.write(bytes(webPage, "utf-8"))
                
        elif self.path == '/listMolecules.html':
            
            # print(allMolecules);
            #show all the molecule with atom no and bond no
            # newMol = MolDisplay.Molecule()
    
            MolDisplay.radius = database.radius()
            MolDisplay.element_name = database.element_name()
            MolDisplay.header += database.radial_gradients()
            for molecule in allMolecules:
                mol = database.load_mol(molecule)
                atomNumber = mol.atom_no
                bondNumber = mol.bond_no
                mol.sort()
                contentSVG = mol.svg()
                uploadMol[molecule] = contentSVG
                uploadMolAtom[molecule] = atomNumber
                uploadMolBond[molecule] = bondNumber
                
            # print(contentSVG)
            # print(uploadMol)
            finalString = ""
            for i in allMolecules:
                nameMol = i;
                nameAtom = str(uploadMolAtom[i]);
                nameBond = str(uploadMolBond[i]);
                finalString += "Molecule: " + nameMol + " Number of Atoms: " + nameAtom + " Number of Bonds: " + nameBond + '\n'
                
            #pass the list and dictionaries as json object
            nameJ = json.dumps(allMolecules);
            atomNoJ = json.dumps(uploadMolAtom);
            bondNoJ = json.dumps(uploadMolBond);
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {'allMolecules': nameJ, 'uploadMolAtom': atomNoJ, 'uploadMolBond':bondNoJ}
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))

    def do_POST(self):
        if self.path == "/sdfUpload.html":
            contentLength = int(self.headers["Content-length"])
            contentWeb = self.rfile.read(contentLength)
            
            dictContentWeb = urllib.parse.parse_qs(contentWeb.decode('utf-8'))
            # print(dictContentWeb)
            
            nameOfMolecule = dictContentWeb[' name'][0][1:-1] #remove the "" 1 and last chars
            # print("--HERE==",nameOfMolecule)
            contentFileData = dictContentWeb[' filename'][0]
            
            # print(contentFileData)
            fileObj = io.StringIO(contentFileData)
            fileObj.readline()
            fileObj.readline()
            fileObj.readline()
            
            # print("1",fileObj.readline())
            # print("2", fileObj.readline())
            # print("3" ,fileObj.readline())

            database.add_molecule(nameOfMolecule, fileObj) #to be changed
            allMolecules.append(nameOfMolecule);
        
            message = "The sdf file has been uploaded to the system!"

            self.send_response(200)  # OK
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(message))
            self.end_headers()

            self.wfile.write(bytes(message, "utf-8"))
        
        elif self.path == "/getSVG.html":
            self.send_response(200)  # successful server response
            self.send_header("Content-type", "text/plain")
            contentLength = int(self.headers["Content-length"])
            contentWeb = self.rfile.read(contentLength)

            print(repr(contentWeb.decode('utf-8')))
            dictContentWeb = urllib.parse.parse_qs(contentWeb.decode('utf-8'))
            name = dictContentWeb['eleNumber'][0]
            
            svgContent = uploadMol[name];
            # print(name);
            # print(svgContent);
            svgContentLen = len(svgContent);
            
            # print(contentSVG)
            self.send_header("Content-length", svgContentLen)
            self.end_headers()
            # sending the svg strings to display the appropriate vector graphic molecule on the webpage
            self.wfile.write(bytes(svgContent, "utf-8"))
            

        elif self.path == "/addElement.html":
            contentLength = int(self.headers["Content-length"])
            contentWeb = self.rfile.read(contentLength)

            print(repr(contentWeb.decode('utf-8')))
            # convert POST content into a dictionary
            dictContentWeb = urllib.parse.parse_qs(contentWeb.decode('utf-8'))

            #get the values from the dictionary (the values in dict are in the form of list)
            number = dictContentWeb['eleNumber'][0]
            code = dictContentWeb['eleCode'][0]
            name = dictContentWeb['eleName'][0]
            one = dictContentWeb['eleCOne'][0]
            two = dictContentWeb['eleCTwo'][0]
            three = dictContentWeb['eleCThree'][0]
            radiusE = dictContentWeb['eleRadius'][0]
            
            database['Elements'] = (number, code, name, one[1:], two[1:], three[1:], radiusE)
            # print(database.conn.execute("SELECT * FROM Elements;").fetchall()) #REMOVE THIS !!!!

            # print(dictContentWeb)
            message = "The Element has been added to the system!"

            self.send_response(200)  # OK
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(message))
            self.end_headers()
            self.wfile.write(bytes(message, "utf-8"))
        
        elif self.path == "/removeElement.html":
            contentLength = int(self.headers["Content-length"])
            contentWeb = self.rfile.read(contentLength)

            print(repr(contentWeb.decode('utf-8')))
            # convert POST content into a dictionary
            dictContentWeb = urllib.parse.parse_qs(contentWeb.decode('utf-8'))

            #get the values from the dictionary (the values in dict are in the form of list)
            number = dictContentWeb['eleNumber'][0]
            code = dictContentWeb['eleCode'][0]
            name = dictContentWeb['eleName'][0]
            one = dictContentWeb['eleCOne'][0]
            two = dictContentWeb['eleCTwo'][0]
            three = dictContentWeb['eleCThree'][0]
            radiusE = dictContentWeb['eleRadius'][0]
            # print(number, code, name, one[1:].upper(), two[1:].upper(), three[1:].upper(), radiusE)
            
            query = "DELETE FROM Elements WHERE ELEMENT_NO = '{}' AND ELEMENT_CODE = '{}' AND ELEMENT_NAME = '{}' AND COLOUR1 = '{}' AND COLOUR2 = '{}' AND COLOUR3 = '{}' AND RADIUS = '{}';".format(number, code, name, one[1:].upper(), two[1:].upper(), three[1:].upper(), radiusE)
            database.conn.execute(query);
            
            # print(database.conn.execute("SELECT * FROM Elements;").fetchall()) #REMOVE THIS !!!!
        
            # print(dictContentWeb)
            message = "The Element has been removed from the system!"

            self.send_response(200)  # OK
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(message))
            self.end_headers()
            self.wfile.write(bytes(message, "utf-8"))
            

        else:
            self.send_response(404)  # err, error!
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))


httpd = HTTPServer(('localhost', int(sys.argv[1])), serverHandler)

httpd.serve_forever()
# httpd.server.close()
