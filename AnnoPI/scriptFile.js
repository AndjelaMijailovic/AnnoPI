$(document).ready(function () {

	var counter = 0;
	var heading = $('#headingTop')[0].innerText + "\n" + $('#goHpoVersion')[0].innerText;;

var buttonCommon = {
        exportOptions: {
            format: {
						body: function ( data, row, column, node ) {
									return column == 9 || column == 10 ? ( node.getElementsByTagName("a")[0] != undefined ? node.getElementsByTagName("a")[0].href : "" ): (column == 7 || column == 8 ? node.textContent.replace("<br />", " ") : node.textContent);
						}					
            },
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
                    dom: 'Bfrtip',
                    buttons: [{
                            extend: 'excelHtml5',
                            text: 'Export All',
                            exportOptions: {
                                columns: ':visible:not(.not-exported)',
								format: {
								body: function ( data, row, column, node ) {

								return column == 9 || column == 10 ? (node.getElementsByTagName("a")[0] != undefined ? node.getElementsByTagName("a")[0].href : ""): (column == 7 || column == 8 ? node.textContent.replace("<br />", " ") : node.textContent);
								}
								}
                            },
                            title: 'Export all data',
							messageTop: heading,
							messageBelow: 'Below msg',

                         }, 
						$.extend( true, {}, buttonCommon, {
							extend: 'excelHtml5',
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
										return column == 9 || column == 10 ? (node.getElementsByTagName("a")[0] != undefined ? node.getElementsByTagName("a")[0].href : ""): (column == 7 || column == 8 ? node.textContent.replace("<br />", " ") : node.textContent);
									}
								}
                            },
                            title: 'Exported Variations csv',
							caption: 'Exported csv data'
                        }						
                    ],
                    select: {
                    	style : "multi",
						fnPreRowSelect: function ( e, nodes ) {
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
				var searchTerm = this.value.toLowerCase();
				var term = searchTerm;
				regex = '\\b' + searchTerm;
				var searched = table.rows().search(regex, true, false);
				

				$("a.hiddenlinks").show();			
				
				searched.draw();
							
			});

		//change selected rows
		$('#rowsNumber').on('change', function() {

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


		//setting tooltips
		$("td:has(span)").each( function (i, value) {
			if (geneMap.has(value.textContent))
			{
				$("span", this).attr('title', geneMap.get(value.textContent).toString());
			}	
		});
		
		$("td:has(a)",  table.rows().nodes()).each( function (i, value) {

				$(this).children().each(function (j, valuee){
					
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
});
