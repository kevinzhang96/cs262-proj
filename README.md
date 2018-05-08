# CS262 Final Project - Personal File Backup System
*Kevin Zhang, Tomoya Hasegawa*

## Overview
This repository is an implementation of a distributed and replicated, personal file backup system.

## Requirements
* A Google account with payments set up
* All other requirements will be installed through the installation script, but include the Google Cloud SDK, Python2, Pip, and Paramiko

## Running

Installation is simple. To use our system, run `./install.sh` in the directory that you want to backup. Follow the instructions, and you're good to go! Your files will be automatically backed up to Google Cloud servers.

If you wish to use your own personal srvers, we cannot automate the setup process. However, plugging in your servers should be relatively simple. (We have not tested this.)
* Clone this repo onto your servers
* Edit the client config file to add the IP addresses of your servers
* Run `python server.py` on each server
* Exclude Google-specific setup, and then run `./install.sh` on the client