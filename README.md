# AWSTranscribe
 
## Requirements
This script only supports Python 3, and requires the following:

* Boto3 Amazon Web Services (AWS) Software Development Kit (SDK) for Python
* AWS Command Line Interface (CLI) configured
* S3 bucket

## Usage

    $ python3 transcripter.py -b [S3 bucket name] -i [input audio file] -p [project name]


    $ python3 transcripter.py -b testbucket -i ./Audio/test.m4a -p test01

### Output files

* project.json
* project.txt


### Notes
Project names are unique and cannot be repeated. 

## Future work

* Validations
* S3 bucket creation
* File management