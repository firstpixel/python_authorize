This script is intent for interview porpose only.

I decide to use python as it is a great language for scripting and is a dynamic programming language.
During the development I faced some issues, on how to handle the time difference on the transactions, so I decide to create a list of transaction and keep track of the original list index, by creating a Transaction class and using a reference on it for the originalIndex, so I could return the violations to the original list with accounts. Using the sort I was able to validate the itens based on time, instead of the original order. To prevent memory overload, I started removing old items from the ordered list as soon as it becames 4 minutes old, that number can be modified, that was just a guess on how old logs would became since last log arrives.

I added a way to stop the script by adding the string EOF at end of each operation, to make it possible to run testcases, by removing the EOF from the end of the json list, it will run indefinitely.
Also added a testing variable, so when testing it will create a comparative result string to match the validations files inside testcases.
To stop the script, just press Ctrl+c


To run the script inside a docker, just run the 2 commands bellow:

docker build -t authorize .
docker run -it --name authorize authorize

Docker version will run all testcases and start the app over operations file on same folder as authorize application, that can be modified on Dockerfile to point to another file, also can modify the file by going inside the container and modifying the operations file by adding new lines while the application is running, to do that just go inside the container by runing this:

docker run -it authorize /bin/bash


To run outside docker:
python authorize.py < testcases/operations0
python authorize.py < operations

To run testcases only you can do:
python authorize_test.py 

This will run all testcases