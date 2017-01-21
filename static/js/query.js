function getData(cat,term,params){
	if (cat == "trends") {
		var url = 'https://www.google.com/trends/fetchComponent?cid=TIMESERIES_GRAPH_0&export=3'+$.param(params);
		var query = new google.visualization.Query(url);
		query.send(handleQueryResponse);

	}else if (term.toLowerCase() == "btc") {

	}else if (term.toLowerCase() == "housing") {

	}else if (term.toLowerCase() == "gold") {

	}else{

	}
}

function querySymbols(){
	$.ajax({
	  type: "GET",
	  url: "https://api.intrinio.com/companies?query=face",
	  dataType: 'json',
	  async: false,
	  headers: {
	    "Authorization": "Basic " + btoa( "f14a7f21a25d12f05be67615ac078841:2c75726a36c24361e8aeb00b769904d1")
	  },
	  success: function (data){
	    console.log(data);
	  }
	});
}