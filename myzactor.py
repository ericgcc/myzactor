#!/usr/local/python-3.3/bin/python3.3

######################################################
#MySQL Zabbix Collector - Stats Performance Collector#
######################################################

import subprocess
import sys
import logging
import argparse
import re

################################
#SCRIPT CONFIGURATION VARIABLES#
################################
parser = argparse.ArgumentParser(prog='myzactor')

parser.add_argument('show', choices=['variable', 'VARIABLE', 'status',
'STATUS'], help='Show variables or status')

parser.add_argument('infile', type=argparse.FileType('r'),
help='File with the list of parameters to be monitored')

parser.add_argument('from', choices=['from', 'FROM'],
help='The word \'FROM\' must appear')

parser.add_argument('hostname', help='''Unique, case sensitive hostname.
Must match hostname as configured on the Zabbix Server.
''')

parser.add_argument('in', choices=['in', 'IN'],
help='The word \'IN\' must appear')

parser.add_argument('host_ip', help='IP address server to be monitored')

parser.add_argument('to', choices=['to', 'TO'],
help='The word \'TO\' must appear')

parser.add_argument('zabbix_ip', help='Zabbix Server IP address')

args = parser.parse_args()

#Absolute path to the optional configuration file
#This file is used to not write password and user
MYCNF = '~/.my.cnf'

#Absolute path to the mysql bin
MYSQL = '$(which mysql)'

GLOBAL_VARIABLES = 'SHOW GLOBAL VARIABLES'
GLOBAL_STATUS = 'SHOW GLOBAL STATUS'

logging.basicConfig(format='%(asctime)s (%(name)s) >> ' +
                    '%(levelname)s: %(message)s',
                    datefmt='%d-%m-%Y %H:%M',
                    filename='/tmp/myzactor.log', level=logging.DEBUG)

regexp = re.compile('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$')

if regexp.match(args.host_ip) is None:
    output = "IP Address appears to be invalid for option " + \
             "\'host_ip\': \'" + args.host_ip + "\'"
    sys.stderr.write(output + "\n")
    logging.error(output)
    sys.exit(1)

if regexp.match(args.zabbix_ip) is None:
    output = "IP Address appears to be invalid for option " + \
             "\'zabbix_ip\': \'" + args.zabbix_ip + "\'"
    sys.stderr.write(output + "\n")
    logging.error(output)
    sys.exit(1)

###################
#THE PARTY BEGINS!#
###################


def show():

    variables = args.infile
    prefix = ''

    for variable in variables:
        variable = variable.strip('\t\n\r')

        if args.show in ['status', 'STATUS']:
            #command = MYSQL + " --defaults-extra-file=" + MYCNF + " -e \"" + \
            command = MYSQL + " -u zabbix --password=\'Er1C$2.*DB\'" + " -e \"" + \
            GLOBAL_STATUS + " LIKE \'" + variable + "\'\" -h %s" \
            % args.host_ip

            prefix = 'mysql.status.'

        else:
            #command = MYSQL + " --defaults-extra-file=" + MYCNF + " -e \"" + \
            command = MYSQL + " -u zabbix --password=\'Er1C$2.*DB\'" + " -e \"" + \
             GLOBAL_VARIABLES + " LIKE \'" + variable + "\'\" -h %s" \
            % args.host_ip

            prefix = 'mysql.variable.'

        try:
            #Se ejecuta el comando y se captura la salida,
            #el resultado es un objeto de bytes
            output = subprocess.check_output(command, shell=True,
                                        stderr=subprocess.PIPE)
        except:
            output = subprocess.Popen(command, shell=True,
            stderr=subprocess.PIPE)

            output = output.stderr.read()
            output = str(output)
            output = output[2:-3]
            print(output)
            logging.error(output)
            sys.exit(1)

        if output == b'':
            sys.stderr.write("The parameter \'%s\' " % variable +
            "does not exist in MySQL as \'" + args.show + "\'.\n" +
            "In host: \'" + args.host_ip + "\'\n")

            logging.info("The parameter \'%s\' " % variable +
            "does not exist in MySQL as \'" + args.show + "\'. " +
            "In host: \'" + args.host_ip + "\'")

            continue

        #Cast object of bytes to string
        output = str(output)

        #Eliminates leftover characters and obtain only the necessary data
        output = output.split('\\n')
        output = output[1].split('\\t')

        output[0] = prefix + output[0]

        command = "$(which zabbix_sender) " + \
        "-z %s -s \"%s\" -k %s -o %s" \
        % (args.zabbix_ip, args.hostname, output[0], output[1])

        output = subprocess.check_output(command, shell=True,
                                        stderr=subprocess.PIPE)
        #print(command)

show()

#Program ends correctly
sys.exit(0)
