CS 340 - Computer Systems Final Project

HTTP tile server used to register client and image to course-wide canvas server

Using this server, the user can upload and register an image. The course canvas server then approves your image, as well as multiple images from other users

Then, the canvas server creates a canvas of tiles, in which people can vote on their end for which tile they like, and this can be done with the frontend of my tile server

To run it:
1. clone the repository
2. Install flask: "pip install flask"
3. go to /tile
4. run the command: "python 3 -m flask run --port==5001"
