This script is intent for interview porpose only.

I decide to use python as it is a great language for scripting.
During the development I faced some issues, on how to handle the time difference on the transactions, so I decide to create a list of transaction and keep track of the original list index, so I could return the violations to the original list with accounts. Using the sort I was able to validate the itens based on time, instead of the original order. To prevent memory overload, I started removing old items from this list as soon as it becames 4 minutes old, keeping a range of 4 minutes, so the second list does not grow too much.
I added a way to stop the script by adding the string EOF at end of each operation, to make it possible to run testcases, by removing the EOF from the end of the json list, it will run indefinitely.
To stop the script, just press Ctrl+c


To run the script inside a docker, just run the 2 commands bellow:

docker build -t authorize .
docker run -t -i authorize


To run outside docker:
python authorize.py < testcases/operations0

To let it run indefinetly remove the EOF from end of opertions files
To run test cases:

python authorize_test.py 

This will run all testcases