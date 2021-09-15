$(document).ready(function () {
	//debugger;
	var counter = 0;
	//var heading = $('#heading1')[0].innerText;
	var heading = $('#headingTop')[0].innerText + "\n" + $('#goHpoVersion')[0].innerText;;
		//tippy('[data-tippy-content]');

var buttonCommon = {
        exportOptions: {
            format: {
						body: function ( data, row, column, node ) {
							debugger;
									return column == 9 || column == 10 ? node.getElementsByTagName("a")[0].href : (column == 7 || column == 8 ? node.textContent.replace("<br />", " ") : node.textContent);
						}					
            },
                                // // columns: ':visible:not(.not-exported)',
			orthogonal: 'export',
            modifier: {
						selected: true
            }
        }
    };			

		
var table = $('#annotationTable').DataTable({
"lengthMenu": [5, 10, 50, 100],
                    "pageLength": 10,
					"pagingType": "input",
                    //"scrollX": true,
                    dom: 'Bfrtip',
                    buttons: [{
                            extend: 'excelHtml5',
                            text: 'Export All',
                            exportOptions: {
                                columns: ':visible:not(.not-exported)',
								format: {
								body: function ( data, row, column, node ) {
									debugger;
									//if (column === 9)
										// return "link"
									//return column == 9 ?
									//data = "link" : data;
								return column == 9 || column == 10 ? node.getElementsByTagName("a")[0].href : (column == 7 || column == 8 ? node.textContent.replace("<br />", " ") : node.textContent);
								}
								}
                            },
                            title: 'Export all data',
							messageTop: heading,
							messageBelow: 'Below msg',

                         }, 
						 //{
                            // extend: 'excelHtml5',
                            // text: 'Export selected',
                            // exportOptions: {
                                // columns: ':visible:not(.not-exported)',
                                // modifier: {
                                    // selected: true
                                // }
                            // },
                            // title: 'Data export'
                        // },
						$.extend( true, {}, buttonCommon, {
							extend: 'excelHtml5',
							// text: 'Export selected',
                            title: 'Export selected data',
							messageTop: heading,
							customize: function ( xlsx ){
							var sheet = xlsx.xl.worksheets['sheet1.xml'];
								
							}
						} ),
						{
                            extend: 'csv',
                            title: 'Export selected csv',
                            exportOptions: {
                                columns: ':visible:not(.not-exported)',
                                modifier: {
                                    selected: true
                                },
								format: {
									body: function ( data, row, column, node ) {
										debugger;
										return column == 9 || column == 10 ? node.getElementsByTagName("a")[0].href : (column == 7 || column == 8 ? node.textContent.replace("<br />", " ") : node.textContent);
									}
								}
                            },
                            title: 'Data export file title',
							caption: 'Data Export e e e'
                        }						
                    ],
                    select: {
                    	style : "multi",
						fnPreRowSelect: function ( e, nodes ) {
							debugger;
							if ( $(e.currentTarget).hasClass('editable') ) {
								return false;
							}
							return true;
						}
                    },
					fixedHeader: true
                });

				var self = this;

			$('.dataTables_filter input').unbind().bind('keyup', function() {
				debugger;
				var searchTerm = this.value.toLowerCase();
				var term = searchTerm;
				regex = '\\b' + searchTerm;
				var searched = table.rows().search(regex, true, false);
				

				$("a.hiddenlinks").show();			
				
				searched.draw();
							
			});
		
		

		//change selected rows
		$('#rowsNumber').on('change', function() {
			debugger;
			var selected = this.value;
			var selected2 = selected - 1;
			
			if (selected2 > -1)
			{
				table.rows(':lt(' + selected + ')', { page: 'all' }).select();
				table.rows(':gt(' + selected2 + ')', { page: 'all' }).deselect();
			}
			else
			{
				table.rows().deselect();
			}			
		});
		
		$('#selectFirst').on('click', function() {
			//debugger;
			table.rows(':lt(2)', { page: 'current' }).select();
			
		});
		
		//change select show XY  functions
		$('#showXFunctions').on('change', function() {
			var val = this.value;
			//$('#dialogWait').open();
			if (val == "all")
			{	$("td:has(a)", table.rows().nodes()).children().each( function (i, value) {
					$(this)[0].style.display="inline";
				});
				return true;
			}
			
			//tableElements
			//table.fnGetNodes when constructor is dataTable
			$("td:has(a)",  table.rows().nodes()).each( function (i, value) {

				$(this).children().each(function (j, valuee){
					// debugger;
					var content = valuee.textContent.trim();
					
					if (goMap.has(content))
					{
						
						$(valuee).attr('title', goMap.get(content).toString());
					}
					else if (hpoMap.has(content))
					{
						$(valuee).attr('title', hpoMap.get(content).toString());
					}	
					
					if (j >= val)
						valuee.style.display="none";
					else
						valuee.style.display = "inline";
				});	
			});
		});


		$("td:has(span)").each( function (i, value) {
			if (geneMap.has(value.textContent))
			{
				//$("span", this).attr('data-tippy-content', geneMap.get(value.textContent).toString());
				$("span", this).attr('title', geneMap.get(value.textContent).toString());
			}	
		});
		
		$("td:has(a)",  table.rows().nodes()).each( function (i, value) {

				$(this).children().each(function (j, valuee){
					// debugger;
					
					var content = valuee.textContent.trim();
					
					if (goMap.has(content))
					{
						
						$(valuee).attr('title', goMap.get(content).toString());
					}
					else if (hpoMap.has(content))
					{
						$(valuee).attr('title', hpoMap.get(content).toString());
					}	
				});	
			});
		
		
		
		//$("#CCNL2").attr('data-tippy-content', geneMap.get("CCNL2").toString());
		//$("#MORN1").attr('data-tippy-content', myMap.get("MORN1").toString());
		//let reader = new FileReader();
		//reader.readAsText("geneJsonFileAlt.json");
		
		// var sample_data = '';
		// $.getJSON("geneJsonFile.json", function (data) {
			// sample_data = data;
			// $.each(data, function (key, value) {
			// console.log(sample_data);
			// });
		// });
		
		//let jsonData = require("geneJsonFile.json"); 

		
		//$("#CCNL2").attr('title', myMap.get("CCNL2").toString());
		//$("#CCNL2").title = myMap.get("CCNL2");

		//window.localStorag
		// function loadJSON(callback) {

			// var xobj = new XMLHttpRequest();
			// xobj.overrideMimeType("application/json");
			// xobj.open('GET', 'geneJsonFileAlt.json', true);
			// xobj.onreadystatechange = function () {
				// if (xobj.readyState == 4 && xobj.status == "200") {
	
			// // .open will NOT return a value but simply returns undefined in async mode so use a callback
				// callback(xobj.responseText);
				// }
			// }
			// xobj.send(null);

			// }
		
		 // // Call to function with anonymous callback
		// loadJSON(function(response) {
		// // // Do Something with the response e.g.
			// jsonresponse = JSON.parse(response);
			// console.log("Finished");
		// // // Assuming json data is wrapped in square brackets as Drew suggests
		// // console.log(jsonresponse[0].SHANK3);

		// });
		
		// $("td").hover(function(){
			// debugger;
			// var currGene = $(this).find("span").text();
			// if (currGene == "MORN1")
				// $("span", this).attr('data-tippy-content', "MORN1");
			// //geneMap.get(currGene);
			// //tippy('[data-tippy-content]');
		// });
//tippy('[data-tippy-content]');


//tippy(table.$('[data-tippy-content]'));
});
