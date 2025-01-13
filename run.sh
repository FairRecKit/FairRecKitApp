#!/bin/bash

# Navigate to the client folder
cd client || exit 1  # Exit if the folder doesn't exist
# Run the client script in the background
./run-client.sh &

# Navigate back to the root folder
cd .. || exit 1
# Navigate to the server folder
cd server || exit 1
# Run the server script
./run-server.sh