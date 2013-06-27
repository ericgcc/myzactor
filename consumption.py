from fabric.api import run
from fabric.api import env
from fabric.api import local
import sys
env.warn_only = True

MYCNF = "~/.my.cnf"


def toGB(number, unit):
    if unit in ['M', 'm']:
        return float(number) / 1024
    elif unit in ['K', 'k']:
        return float(number) / 1048576
    else:
        return number


#def measure(user, regex, passwd, data, host, zabbix_server):
def measure(user, passwd, data, host, zabbix_server):
    env.password = passwd

    #MySQL Process CPU & RAM Usage (Percentge)
    #$9 = CPU
    #$10 = RAM
    command = "MYSQL_PID=$($(which sudo) ps -u" + user + " | " + \
              "$(which tail) -n1 | " + \
              "$(which awk) \'FS=\" \" {print $1}\') && " + \
              "$(which sudo) top -b -n1 -p $MYSQL_PID | " + \
              "$(which tail) -n2 | $(which awk) \'FS=\" \" " + \
              "{print $9,$10}\'"

    output = run(command)
    output = output.split(" ")

    #Sending data to Zabbix Server
    command = "$(which zabbix_sender) " + \
              "-z %s -s \"%s\" -k mysql.cpu_usage -o %s" \
              % (zabbix_server, host, output[0])

    local(command)

    command = "$(which zabbix_sender) " + \
              "-z %s -s \"%s\" -k mysql.ram_usage_percent -o %s" \
              % (zabbix_server, host, output[1])

    local(command)

    #Total RAM used by MySQL Process (bytes)
    command = "MYSQL_PID=$($(which sudo) ps -u" + user + " | " + \
              "$(which tail) -n1 | " + \
              "$(which awk) \'FS=\" \" {print $1}\') && " + \
              "$(which pmap) -x $MYSQL_PID | $(which tail) -n1 | " + \
              "$(which awk) \'FS=\" \" {print $3}\'"

    output = run(command)
    output = toGB(output, 'k')

    command = "$(which zabbix_sender) " + \
              "-z %s -s \"%s\" -k mysql.ram_usage_bytes -o %s" \
              % (zabbix_server, host, output)

    local(command)

    ##CPU IDLE
    #command = "$(which top) -n1 | $(which head) -3 | $(which tail) -1 | " + \
    #"$(which awk) 'FS=\" \" {split($5, cpuidle, \"%\"); print cpuidle[1]}'"
    #output = run(command)

    ##Sending data to Zabbix Server
    #command = "$(which zabbix_sender) " + \
              #"-z %s -s \"%s\" -k system.cpu_idle -o %s" \
              #% (zabbix_server, host, output)
    #local(command)

    ##Occupied disk space of MySQL data
    #command = "$(which du) -sh %s | $(which awk) 'FS=\" \" {print $1}'" % data
    #output = run(command)
    #output = output.replace(',', '.')

    ##print output[:-1]
    ##print output[-1]
    #output = toGB(output[:-1], output[-1])
    ##print output

    ##Sending data to Zabbix Server
    #command = "$(which zabbix_sender) " + \
              #"-z %s -s \"%s\" -k mysql.occupied_disk -o %s" \
              #% (zabbix_server, host, output)
    #local(command)

    #Free disk space of MySQL data
    command = "$(which df) -h %s | " % data + \
               "$(which tail) -n1 | $(which awk) 'FS=\" \" {print $4}'"
    output = run(command)
    output = output.replace(',', '.')

    #print(command)
    #print output[:-1]
    #print output[-1]
    output = toGB(output[:-1], output[-1])
    #print output

    #Sending data to Zabbix Server
    command = "$(which zabbix_sender) " + \
              "-z %s -s \"%s\" -k mysql.free_disk -o %s" \
              % (zabbix_server, host, output)
    local(command)

    #Total disk space of MySQL data
    command = "$(which df) -h %s | " % data + \
               "$(which tail) -n1 | $(which awk) 'FS=\" \" {print $2}'"
    output = run(command)
    output = output.replace(',', '.')

    #print output[:-1]
    #print output[-1]
    output = toGB(output[:-1], output[-1])
    ##print output

    #Sending data to Zabbix Server
    command = "$(which zabbix_sender) " + \
              "-z %s -s \"%s\" -k mysql.total_disk -o %s" \
              % (zabbix_server, host, output)
    local(command)

    #MySQL Ping
    command = "$(which mysqladmin) -u zabbix --password=\'Er1C$2.*DB\'" + \
              " ping"
    output = run(command)

    if output == 'mysqld is alive':
        output = 1
    else:
        output = 0

    command = "$(which zabbix_sender) " + \
        "-z %s -s \"%s\" -k %s -o \'%s\'" \
        % (zabbix_server, host, "mysql.ping", output)
    local(command)

    sys.exit(0)
