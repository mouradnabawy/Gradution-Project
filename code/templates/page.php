<html>
  <head>
    <title>Video Streaming Demonstration</title>
  </head>
  <body>
    <h1>E-Learning System</h1>
  <p></p>


<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jqyery.min.js"></script>
<script language="javascript">

function Redirect() {
  document.location= "http://localhost:5000/start"

}

$(document).ready(function()
{
	// set trigger and container varables
	var tri = $('nav'),
		container = $('btn');

	//fire on click
	tri.on('click',function()
	{
		//set $this for re-use. set tareget from data attr
		var $this = $(this)
		target = $this.data('target');

		//load target page into container
		container.load(target + 'PageNextLevel.php');

		//stop mormal link behavior
		return false;

	});
});


</script>
<nav id="nav">
  	<!-- <h1>{{ url_for('calc') }}</h1> -->
  <p>helllllllllllo </p>

 </nav>

 <div id="content">

	<input type="button" name="btn" value="WELCOME" onClick="Redirect()">

  </div>
  </body>
</html>
