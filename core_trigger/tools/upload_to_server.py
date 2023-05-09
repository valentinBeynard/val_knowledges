import subprocess
import argparse

"""
    THIS TOOL IS USED TO UPLOAD FOLDERS AND FILE ONTO THE WEBSERVER
"""

FOLDERS_TO_UPLOAD = "../css ../scripts ../images ../\*.html"

if __name__ == '__main__':

    # Create the parser
    parser = argparse.ArgumentParser(description='Upload Webser files to hardware target', epilog='Previous generation of SSH Key is mandatory')

    # Create associated arguments
    parser.add_argument('ip', metavar='ip', type=str, help='Webserver local IP')
    parser.add_argument('user', metavar='user', type=str, help='Webserver user')
    parser.add_argument('--path', metavar='path', type=str, default="/home", help='Webserver path for files upload')

    # Get arguments
    args = parser.parse_args()

    # Launch command for upload
    SCP_cmd = "scp -r " + FOLDERS_TO_UPLOAD + " " + args.user + "@" + args.ip + ":" + args.path
    #print(SCP_cmd)
    proc = subprocess.Popen(SCP_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out = proc.communicate(input=b'\n', timeout=5)[0].decode("utf-8")

    print(out)

    print("Done !")
