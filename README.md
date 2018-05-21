### Kapsh Categorize Images Pset

# Start
To start the application execute the following command in the terminal:
flask run

# Kapsch Study Case:
* User opens the website.
* User register or login if registered.
* if there is any uncategorized images redirects user to categorize image.
* First image of several images is shown.
* User chooses which category the image belongs to (A, B or C) from the dropdown list and clicks on submit.
* Next image is shown.
* If all images categorized redirects user to upload more jpg images.

# Challenge:
* Create a web-app with user login area.
* Create database.
* Create database access (read, write).
* Store images in database as BLOP type.
* Create a page to allow user to upload more images.
* Show images in a page.
* Store the categorization for each image in the database.

# Details:
Create database with 1 table -- Table 1 contains 2 columns (image | category) image can be of type "blob" (depends on database) category is varchar (1), can be null -- insert some images by hand

Create Website -- Show the image stored in the database -- Show a dropdown with 3 entries, "A", "B", "C" -- Goal: categorize the image -- There is a next button > -- You choose an entry from the dropdown = you categorize the image -- If you press the > button the categorization is saved and the next image is shown.