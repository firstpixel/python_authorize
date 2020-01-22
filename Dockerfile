#to run the script just run the 2 commands above
# docker build -t authorize .
# docker run --name=authorize -v $(PWD) /home --rm -it -e PYTHONUNBUFFERED=0 authorize
# this will run all testcases and start the application over the operations file

#publicly available docker image "python" on docker hub will be pulled
FROM python:2.7.16

#creating directory authorize in container (linux machine)
#RUN cd home && mkdir authorize && cd authorize

WORKDIR /home

#running authorize.py in container
CMD python authorize_test.py && python -u authorize.py < testcases/operations



