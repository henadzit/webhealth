# Overview
This is a bunch of scripts to monitor state (OK/FAIL) of multiple websites and analyze the results later. There are gonna be blog posts about the research done with this tool on http://henadzit.com/.

## Design
There are couple of components:
* monitoring daemon
* script to import data into a SQL database (now it would work only with MySQL)
* bunch of IPython notebooks to analyse data

The monitoring daemon is supposed to be run as a Docker instance. It ingests a set of command line arguments and writes a log with probe results in JSON. This file can be imported into a SQL database for further analysis.
