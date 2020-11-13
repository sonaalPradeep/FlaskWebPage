# Image Metadata Storage System

### A simple webpage which that can extract, store and search images based on the metadata.

<i>Program designed by </i>[Sonaal Pradeep](https://github.com/sonaalPradeep) and <i>[Varun Kumar Reddy Ramireddy](https://github.com/varunrami)</i>

<hr>

## Packages Pre-requisites
The program runs and is tested on <b>Linux using python3.7.5</b> and required additional packages. To install these packages, run the following command on your terminal:
```bash
# It is suggested to have a seperate virtual environment. Otherwise, just run the pip3 command. You need to have virtualenv installed for this.
virutalenv /path/to/venv
source /path/to/venv/bin/activate

pip3 install -r requirements.txt
```

## How to run the program
Make sure the frontend and backend are configured coorectly. After verifying, run the following commands to start the app.
```bash
python3 frontend.py
python3 backend.py
```

## Notes
* The program supports extracting metadata from only <b>JPG</b> images.
* There are instances when the image doesn't correspond to the correct metadata. When this happens, <b>hard reset the browser</b>.
