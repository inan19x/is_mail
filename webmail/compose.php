<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Web Mail Client</title>
</head>
<body>
    <h3>Send an email:</h3>
    <form action="send.php" method="POST">
        <label for="from_email">From:</label><br>
	<input type="email" id="from_email" name="from_email" value="<?php echo $username; ?>" required readonly><br><br>
        
        <label for="to_email">To:</label><br>
        <input type="email" id="to_email" name="to_email" required><br><br>
        
        <label for="subject">Subject:</label><br>
        <input type="text" id="subject" name="subject" required><br><br>
        
        <label for="body">Body:</label><br>
        <textarea id="body" name="body" rows="6" cols="30" required></textarea><br><br>
        
        <button type="submit">Send Email</button>
    </form>
</body>
</html>

