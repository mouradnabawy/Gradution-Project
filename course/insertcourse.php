<?php
		$con = new mysqli("localhost", "root", "","graduation_project");
		$sql="SELECT * FROM courses";
	    $result=mysqli_query($con,$sql);
		
		?>
		<select name="course">
		<?php 
		while($rows = mysqli_fetch_array($result))
		{
		$Branch=$rows['CourseTitle'];
		echo"<option value='$course'>$course</option>";
		}
		?>
		</select>