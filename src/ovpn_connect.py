import os.path
import subprocess
import sys
from string import Template
from time import sleep
from typing import List

import boto3
from types_boto3_ec2 import Client
from types_boto3_ec2.type_defs import DescribeInstancesResultTypeDef

OVPN_FILE_PATH = 'src/profile-8808417773363479671'
SUFFIX = ".ovpn"


class ConnectVPN:
    def __init__(self, instance_id: str) -> None:
        self.instance_id = instance_id
        self.client: Client = boto3.client("ec2")

    def start_instance(self) -> None:
        print("Starting instance...")
        self.client.start_instances(InstanceIds=[self.instance_id])
        state = self.instance_status()
        while state != "running":
            state = self.instance_status()
            if state == "running":
                break
            sleep(5.0)
        print("Instance started successfully")

    def stop_instance(self) -> None:
        print("Stopping instance...")
        self.client.stop_instances(InstanceIds=[self.instance_id])

    def instance_status(self) -> str:
        print("Checking instance status...")
        instance: DescribeInstancesResultTypeDef = self.client.describe_instances(InstanceIds=[self.instance_id])
        return instance['Reservations'][0]['Instances'][0]['State']['Name']

    def get_instance_ip(self) -> str:
        print("Getting instance IP...")
        instance = self.client.describe_instances(InstanceIds=[self.instance_id])
        ip: str = ""
        try:
            ip = instance["Reservations"][0]["Instances"][0]["PublicIpAddress"]
            print("Instance IP is:", ip)
        except KeyError:
            print("Instance is not running")
        return ip


class OpenVPN:
    def __init__(self, ip: str) -> None:
        self.executable_path = ["sudo", "/opt/homebrew/sbin/openvpn"]
        self.connect(self.configure_ovpn_connection(ip))

    @staticmethod
    def configure_ovpn_connection(ip: str) -> str:
        print("Configuring OpenVPN connection...")
        with open(os.path.realpath(OVPN_FILE_PATH + SUFFIX), 'r') as file:
            ovpn_content = file.read()
        template = Template(ovpn_content)
        updated_content = template.safe_substitute(IP=ip)
        filename = OVPN_FILE_PATH + "_" + ip + SUFFIX
        with open(filename, 'w') as file:
            file.write(updated_content)
        return filename

    def connect(self, profile_file: str) -> None:
        self.run(self.executable_path + ["--config", profile_file])

    @staticmethod
    def run(command: List[str]) -> str:
        try:
            print(f"Running VPN command: {" ".join(command)}...")
            subprocess.call(command)
        except FileNotFoundError:
            print("OpenVPN binary not found. Ensure it is installed and in your system's PATH.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return ""


def main(instance_id: str):
    connect_vpn = ConnectVPN(instance_id)
    state = connect_vpn.instance_status()
    if state == "stopped":
        command = input("Instance is stopped. Do you want to start it? (y/n): ")
        if command.lower() != "y":
            return
        connect_vpn.start_instance()
    elif state == "running":
        command = input("Instance is already running. Do you want to stop it? (y/n): ")
        if command.lower() == "y":
            connect_vpn.stop_instance()
            return
    command = input("Do you want to configure VPN connection? (y/n): ")
    if command.lower() != "y":
        return
    ip: str = connect_vpn.get_instance_ip()
    if not ip:
        print("Couldn't configure connection")
        return
    command = input("Would you like to connect to the VPN? (y/n): ")
    if command.lower() == "y":
        OpenVPN(ip)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0:
        main(args[0])
    else:
        print("Please provide an instance ID as an argument.")
        sys.exit(1)
