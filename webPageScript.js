var alreadyMol = [];
$(document).ready(
	function () {
		/* add a click handler for our button */
		$("#buttonAdd").click(function () {
			$.post("/addElement.html",
				{
					eleNumber: $("#elementnumber").val(),	/* retreive value of name field */
					eleCode: $("#elementcode").val(),
					eleName: $("#name").val(),
					eleCOne: $("#colourone").val(),
					eleCTwo: $("#colourtwo").val(),
					eleCThree: $("#colourthree").val(),
					eleRadius: $("#elementradius").val()
				},
				function (data, status) {
					alert("Data: " + data + "\nStatus: " + status);
				}
			);
		}
		);
		/* add a click handler for our button */
		$("#buttonRemove").click(function () {
			$.post("/removeElement.html",
				{
					eleNumber: $("#elementnumber").val(),	/* retreive value of name field */
					eleCode: $("#elementcode").val(),
					eleName: $("#name").val(),
					eleCOne: $("#colourone").val(),
					eleCTwo: $("#colourtwo").val(),
					eleCThree: $("#colourthree").val(),
					eleRadius: $("#elementradius").val()
				},
				function (data, status) {
					alert("Data: " + data + "\nStatus: " + status);
				}
			);
		}
		);

		$("#submitsvg").click(function () {
			$.post("/getSVG.html",
				{
					eleNumber: $("#selectm").val(),	/* retreive value of name field */
				},
				function (data, status) {
					alert("Data: " + data + "\nStatus: " + status);
					var wepdata = $('#svguplaod');
					console.log(wepdata);
					wepdata.append(data);
				}
			);
		}
		);



		$('#formone').submit(function (event) {
			event.preventDefault();
			var inputFile = document.getElementById("sdffile");
			var fileData = document.getElementById("formone");
			var dataFromForm = new FormData();
			var molName = $("#namemol").val();
			console.log(molName);
			dataFromForm.append(molName, inputFile.files[0])
			$.ajax(
				{
					url: '/sdfUpload.html',
					type: 'POST',
					data: dataFromForm,
					processData: false,
					contentType: false,
					success: function (response) {
						console.log(response)
					}
				}
			);
		});

		$("#listm").click(function () {
			$.get("/listMolecules.html",
				function (response) {
					var allMolecules = JSON.parse(response.allMolecules);
					var uploadMolAtom = JSON.parse(response.uploadMolAtom);
					var uploadMolBond = JSON.parse(response.uploadMolBond);
					console.log(allMolecules);
					console.log(uploadMolAtom);
					console.log(uploadMolBond);
					var i;
					var k;
					var x;
					var nameMol;
					var nameAtom;
					var nameBond;
					var found = 0;
					console.log(typeof allMolecules);

					var finalString = "";
					for (x in allMolecules) {
						//do nothing
					}
					console.log(allMolecules[x]);
					nameMol = allMolecules[x];
					alreadyMol.push(nameMol);
					console.log(alreadyMol);
					console.log(uploadMolAtom[allMolecules[x]]);
					nameAtom = uploadMolAtom[allMolecules[x]];
					nameBond = uploadMolBond[allMolecules[x]];
					console.log(nameMol);
					console.log(nameAtom);
					console.log(nameBond);
					finalString = "   Molecule:" + nameMol + "   Number of Atoms: " + nameAtom + "   Number of Bonds: " + nameBond + '\n';
					var listing = $('#displaylist');
					var listingitem = $('<li>').text(finalString);
					listing.append(listingitem);

					var listweb = $('#selectm');
					var listitem = $('<option>').text(alreadyMol[x]);
					listweb.append(listitem);


				}
			);
		});

	}
);