#to run the script jus run the 2 commands above
#docker build -t authorize .
#docker run authorize

#publicly available docker image "python" on docker hub will be pulled
FROM python

#creating directory authorize in container (linux machine)
RUN cd home && mkdir authorize && cd authorize

WORKDIR /home/authorize
#copying authorize.py from local directory to container's authorize folder

COPY authorize.py /home/authorize/authorize.py
COPY testcases/operations /home/authorize/operations

#running authorize.py in container
CMD python -u authorize.py < operations



