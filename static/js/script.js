$("#evaluate").on("click",function(e){
	e.preventDefault();

	//Prevent empty input here!
	text = $("#statement").val()

	if(text.length < 2){
		console.log("Text area empty!");
		return 0;
	}

	$.ajax({
		type: "POST",
		url:"http://127.0.0.1:8000/api/analyse",
		data:{"text":text},
		success:function(res){
			console.log("Stars "+res.stars);
			$("#classification").text("Mark: "+res.stars+" out of 5.");
		}
	});

})