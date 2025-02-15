# A wrapper project for openvpn
I have an OpenVPN server running on AWS EC2.
I used bitnami OpenVPN AMI to create it, and downloaded the client configuration files.

When I want to use it, the code would handle starting it, getting its IP, and connecting to it.

When I'm done, the code would handle disconnecting from it and stopping it.

Python code runs fine, except for running the subprocess call to connect, and handle SIGINT to disconnect.

Shell code runs flawlessly.

Enjoy!

Feel free to make suggestions, or contribute.

## Pre-requisites
- OpenVPN server running on AWS EC2
- OpenVPN client configuration files
- OpenVPN client installed on your machine
- AWS CLI installed on your machine
- AWS CLI configured with your AWS account
- Python 3.6 or higher
- Boto3 installed on your machine
