#!/bin/bash

# Variables
INSTANCE_ID="$1"
TEMPLATE_FILE="profile-8808417773363479671.ovpn"
PLACEHOLDER_IP="\$IP"

# Function to get the instance status
get_instance_status() {
  aws ec2 describe-instances --instance-ids "$INSTANCE_ID" --query "Reservations[0].Instances[0].State.Name" --output text
}

# Function to start the instance
start_instance() {
  echo "Starting instance..."
  aws ec2 start-instances --instance-ids "$INSTANCE_ID"
  while [ "$(get_instance_status)" != "running" ]; do
    sleep 5
  done
  echo "Instance started successfully"
}

# Function to stop the instance
stop_instance() {
  echo "Stopping instance..."
  aws ec2 stop-instances --instance-ids "$INSTANCE_ID"
}

# Get the instance status
INSTANCE_STATUS=$(get_instance_status)

# Check if the instance is stopped and prompt to start it
if [ "$INSTANCE_STATUS" == "stopped" ]; then
  read -p "Instance is stopped. Do you want to start it? (y/n): " command
  if [ "$command" != "y" ]; then
    exit 0
  fi
  start_instance
elif [ "$INSTANCE_STATUS" == "running" ]; then
  read -p "Instance is already running. Do you want to stop it? (y/n): " command
  if [ "$command" == "y" ]; then
    stop_instance
    exit 0
  fi
fi

# Prompt to configure VPN connection
read -p "Do you want to configure VPN connection? (y/n): " command
if [ "$command" != "y" ]; then
  exit 0
fi

# Get the public IP of the EC2 instance
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" --query "Reservations[0].Instances[0].PublicIpAddress" --output text)

# Check if the public IP was retrieved successfully
if [ -z "$PUBLIC_IP" ]; then
  echo "Failed to retrieve the public IP address."
  exit 1
fi

OUTPUT_FILE="profile-8808417773363479671_$PUBLIC_IP.ovpn"
# Replace the placeholder IP in the template file and create a new file
sed "s/$PLACEHOLDER_IP/$PUBLIC_IP/g" $TEMPLATE_FILE > "$OUTPUT_FILE"

# Prompt to connect to the VPN
read -p "Would you like to connect to the VPN? (y/n): " command
if [ "$command" == "y" ]; then
  sudo /opt/homebrew/sbin/openvpn --config "$OUTPUT_FILE"
fi