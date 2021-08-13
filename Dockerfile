FROM centos/python-36-centos7
WORKDIR /project
ADD . /project
RUN pip3 install -r requirements.txt
RUN pip3 install flask_bcrypt
RUN pip3 install python-dotenv
EXPOSE 5000
CMD ["python","run.py"]