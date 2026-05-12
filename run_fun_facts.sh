#!/bin/bash
# Move to project folder
cd /storage/emulated/0/cephasokshoes
# Activate environment and run command
source ~/cephas_env/bin/activate
python manage.py send_fun_facts >> fun_fact_log.txt 2>&1