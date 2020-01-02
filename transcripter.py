import argparse as _argparse
import boto3 as _boto3
import os as _os
import time as _time
import json as _json

_SCRIPT_TITLE_WITH_VERSION = "POC AWS Transcribe - Pollito"
_TRANCRIPT_HEARTBEAT_TIME = 5
_TRANSCRIPT_MAX_HEARTBEATS = 25

def parse_arguments():

    # Create the argument parser
    argument_parser = _argparse.ArgumentParser(description=_SCRIPT_TITLE_WITH_VERSION)

    # Create script arguments
    argument_parser.add_argument("-b", "--bucket_name", help="S3 Bucket name", required=True)
    argument_parser.add_argument("-i", "--input_file_path", help="File to upload", required=True)
    argument_parser.add_argument("-p", "--project_name", help="Project Name", required=True)

    # Parse script arguments
    arguments = argument_parser.parse_args()

    return arguments

def upload_file(input_file_path, bucket_name, server_side_input_file_name):

    # Open the s3 bucket to upload the file
    s3_client = _boto3.client("s3")
    
    try:

        # Upload the file
        print("--Uploading " + server_side_input_file_name + " to " + bucket_name + " bucket")
        s3_client.upload_file(input_file_path, bucket_name, server_side_input_file_name)

    except Exception as ex:
        
        print("---ERROR: Could not submit file: " + str(ex))
        return False

    return True


def transcript_file(server_side_input_file_name, bucket_name, project_name):

    # Create transcribe clients
    _boto3.client("s3")
    transcribe_client = _boto3.client('transcribe')
    job_uri = "https://" + bucket_name + ".s3.amazonaws.com/" + server_side_input_file_name
    
    try:

        print("--Launching transcripting job")

        # Initiate AWS Transcription job
        transcribe_client.start_transcription_job(
            TranscriptionJobName=project_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='mp4',
            LanguageCode='en-US',
            OutputBucketName=bucket_name,
        )

    except Exception as ex:

        print("--ERROR: Could not transcript the file: " + str(ex))
        return False

    # Log in console transcription status
    transcript_status = False
    heartbeat_counter = 0
    while not transcript_status:

        # Wait until the file is transcripted
        status = transcribe_client.get_transcription_job(TranscriptionJobName=project_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
           
            print("--File transcripted")
            return True
        else:

            # Transcript is not done
            print("---Waiting for transcript to be done")
            _time.sleep(_TRANCRIPT_HEARTBEAT_TIME)
            heartbeat_counter += 1

        # Check if need to fail
        if heartbeat_counter >= _TRANSCRIPT_MAX_HEARTBEATS:
            print("----Time limit reached")
            return False


def download_json_file(bucket_name, project_name):

    output_file = project_name + ".json"
    
    # Create s3 clients
    s3_client = _boto3.client('s3')

    try:

        print("--Downloading transcripted json file")
        # Download the transcriptions
        s3_client.download_file(bucket_name, output_file, output_file)

    except Exception as ex:

        print("--Error: Could not download transcripted json file: " + str(ex))
        return ""

    return output_file

def json_to_txt(input_file_path, output_file_path):

    with open(input_file_path, 'r') as input_file:

        # Opening json file
        json_dict = _json.load(input_file)

        #print(json_dict)

        with open(output_file_path, 'w') as output_file:

            output_file.write("Job name:" + str(json_dict['jobName']))
            output_file.write("\n")

            transcripts_list = json_dict['results']['transcripts']

            # Iterate thru all transcripts
            for transcript_dict in transcripts_list:
                output_file.write(transcript_dict['transcript'])
                output_file.write("\n")
                
    return output_file_path

def main():

    print(_SCRIPT_TITLE_WITH_VERSION)

    # Parsing arguments
    print("-Parsing arguments")
    arguments = parse_arguments()
    # Create the correct filesn path
    uploaded_file_path, uploaded_file_name = _os.path.split(arguments.input_file_path)
    print("--Bucket name: " + arguments.bucket_name)
    print("--Project name: " + arguments.project_name)
    print("--Input file path: " + arguments.input_file_path)
    print("--Server side file name: " + uploaded_file_name)

    # Uploading input file to bucket for transcripting
    print("-Uploding file")
    status = upload_file(arguments.input_file_path, arguments.bucket_name,  uploaded_file_name)
    if not status:
        exit(1)
    print("-File uploaded")

    # Start transcript job
    print("-Starting transcript job")
    status = transcript_file(uploaded_file_name, arguments.bucket_name, arguments.project_name)       
    if not status:
        exit(1)
    print("-File transcripted")

    # Downloading json transcription
    print("-Downloading json transcription file")
    json_output_file_name = download_json_file(arguments.bucket_name, arguments.project_name)       
    if len(json_output_file_name) == 0: 
        exit(1)
    print("-File downloaded: " + json_output_file_name)

    # Transform json to txt
    print("-Formating json file to human readable format")
    txt_output_file_name = json_to_txt(json_output_file_name, arguments.project_name + ".txt")       
    if len(txt_output_file_name) == 0: 
        exit(1)
    print("-File formated: " + txt_output_file_name)

    # Print if executed with no errors
    print(_SCRIPT_TITLE_WITH_VERSION + " done without errors")

if __name__== "__main__":
    main()
