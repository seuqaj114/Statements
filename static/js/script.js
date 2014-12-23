$("#evaluate").on("click",function(e){
	e.preventDefault();

	$("#classification").text("");
	//Prevent empty input here!
	text = $("#statement").val()

	if(text.length < 2){
		console.log("Text area empty!");
		return 0;
	}

	$.ajax({
		type: "POST",
		url:"https://classify-my-statement.herokuapp.com/api/analyse",
		data:{"text":text},
		success:function(res){
			console.log("Stars "+res.stars);
			$("#classification").text("Mark: "+res.stars+" out of 5.");
		}
	});
});

$("#instructions").on("click",function(e){
	e.preventDefault();

	$("#classification").text("needed no one ever!");
});