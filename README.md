INTERVIEW SCRIPT (AUTHORIZE)
This script is intent for interview porpose only.

I decide to use python as it is a great language for scripting and is a dynamic programming language.
During the development I faced some issues, on how to handle the time difference on the transactions, so I decide to create a list of transaction and keep track of the original list index, by creating a Transaction class and using a reference on it for the originalIndex, so I could return the violations to the original list with accounts. Using the sort I was able to validate the itens based on time, instead of the original order. To prevent memory overload, I started removing old items from the ordered list as soon as it becames 4 minutes old, that number can be modified, that was just a guess on how old logs would became since last log arrives.

I added a way to stop the script by adding the string EOF at end of each operation, to make it possible to run testcases, by removing the EOF from the end of the json list, it will run indefinitely.
Also added a testing variable, so when testing it will create a comparative result string to match the validations files inside testcases.
To stop the script, just press Ctrl+c

-------------------------------------------------------------------------

RUNNING THE APPLICATION:

To run the script inside a docker, just run the 2 commands bellow:

Build image:
docker build -t authorize .

Run the container:
docker run --name=authorize -v $(PWD) /home --rm -it -e PYTHONUNBUFFERED=0 authorize

Docker version will run all testcases and start the app over testcases/operations file that is inside testcases folder, that can be modified on Dockerfile to point to another file, also can modify the file on the fly by going inside the testcases folder and modifying the operations file by adding new lines while the application is running, that folder is set as a volume inside docker, so all changes on the folder will be reflected to container content, no need to go inside the container to modify it.


APPLICATION AND TESTCASES OUTSIDE DOCKER:

To run outside docker you will need to have python:2 installed, its installed by default on mac machines, on linux, it will require instalation:

python authorize.py < testcases/operations

All operation files ending with numbers(0-7) have a EOF at the end so it will stop application, to run multiple testcases at once

You can run this file to keep application on as it does not contain a EOF flag:
python authorize.py < testcases/operations

To run testcases only you can do:
python authorize_test.py 

This will run all testcases

__________________________________________________________

LIST OF FILES

authorize_test.py       Test application, will run over authorize.py with testcase, matching the respective validation
authorize.py            Main application
colorprint.py           Color for test results
Dockerfile              To build docker image
README.md               This file

testcases/              Folder containing all tests and validations
    operations          Single operation file without EOF, will let app run
    operations0         Multiple test cases with EOF to run on sequence
    operations1
    operations2
    operations3
    operations4
    operations5
    operations6
    operations7
    validations0
    validations1
    validations2
    validations3
    validations4
    validations5
    validations6
    validations7
