# LB2120 Watchdog

## What is this?

Currently the Netgear LB2120 modem does not support manual celltower selection. One way to work around this is to continuously reboot the modem in an attempt to try and force it to connect to the preferred celltower.

## usage

You need to get the password hash used to login to the modem and you need to find the celltower ID you want to connect to.

There currently are two versions: app.py and app_experimental.py

Only difference between these two versions is, that the experimental version is going to be a single script with no 3rd party dependencies.

Currently both versions require Beautifulsoup4

Each version has their own configuration file. Templates for both are provided.

### Password hash

This is pretty simple.

1. Open your browser devtools network tab and navigate to the login screen
2. Type in your password and login.
3. Find the "config" request from the network tab and get the "session.password" value.

### Celltower id

You can either find this from a website like cellmapper or you can try to manually connect to the right celltower and then get the ID from Settings => Mobile => Status Details => Cell ID

## Usage

Modify the provided config file according to your needs and place it in the same folder with the app.py file.

1. Navigate to src folder
2. Run the script:    
    1. Run the normal version with command "python ./app.py -c [CONFIG FILE NAME HERE]"
    2. Run the experimental version with with command "python ./app_experimental.py -c [CONFIG FILE NAME HERE]"

## Requirements

- Beautifulsoup4
