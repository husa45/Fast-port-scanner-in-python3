import re
import socket
import sys
import os
import datetime
import threading
from argparser import argparse
from time import time
from re import match
usage:"str"="""
Name 
    prtscan : enumerate tcp ports , to check if open or closed

usage:
python3 prtscan [-h|-v]  [--port=portlist,range] [--ip=ip adress]

Description :
    this script is used to find all open ports (tcp ones) in a list of ports (single port if you want)
    or a range of ports  for a certain ip adress
    It uses the python socket module , to send a tcp connection request (syn packet ) to a certain host , 
    and if the host replied , then the tcp port is open , otherwise it is closed .
    Making it verbose :some port replies with a Banner , containing an info about this service  , which we receive on our socket
    
    Performance enhancements :
        1. Set a time out for the socket connection ( as the socket is in blocking mode (stops until a response is recieved ) to prevent connection freezes )
        2. used python multithreading , so , (we dont need to wait until every port finishes to move to the next ) we porcess
        multiple port connections simultaneously , which drastically improves the scan time (about 9 seconds for 65000 ports)    
options :
    --help:
        show this manual page
    
    --version:
        shows the version of the portscanner
    
    --port=port1,port2,... or --port=start port-end port:
        to scan a port list , or a port range for a specific ip .
    
    --ip=ip_adress:
        specify the ip adress to be scanned . 
    
    --output=path to output file :
        specifies the output file  of the scan , and if not specified , wrote by default to the
        current working directory of the program
    
"""
version:'str'="1.0.0"
def validate_ip(ip_adress:'str'):
    pattern=re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))$')
    if match(pattern,ip_adress):
        return ip_adress
    else :
        raise SystemExit(f"Error, not  a valid ip adress")

def validate_arguments(args:'str')->'Match':
    return match(r'^((?:--help|-h)|(?:--version|-v)|(?:--port=.+\s--ip=.+(?:\s--output=.+)?)|(--ip=.+\s--port=.+(?:\s--output=.+)?))$',args)
def write_report(info:'str',output_file_path:'str'):
    report_writer=None
    try:
        report_writer=open(output_file_path,'a')
        report_writer.write(info)
    except IsADirectoryError:
        print("the entered path is a path to a directory not a file\n")
    finally:
        report_writer.close()
def read_report(output_file_path:'str')->'None':
    reader=None
    try:
        reader=open(output_file_path,'r')
        print(f"{reader.read()}")
    except FileNotFoundError:
        print("this report file does not exist")
    except IsADirectoryError:
        print(f"provide a file , not a directory")
    except:
        print("unknown error occured")
    finally:
        reader.close()
def tcp_port_scan(ip_adress:'str',port:'str',output_file_path:'str') ->'None':
    tcp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    tcp_client_socket.settimeout(0.4)
    try:
        results_writer=open(output_file_path,'a')
        result=tcp_client_socket.connect_ex((ip_adress,port))
        if result==0:
                try :
                    banner=tcp_client_socket.recv(1024).decode()
                    results_writer.write(f"{port}/tcp  open    {banner}\n")
                except:
                    results_writer.write(f"{port}/tcp  open\n")
        else:
                results_writer.write(f"{port}/tcp  closed\n")
    except socket.error:
        print("cant make a connection with the server")
    except:
        print("unknown error occured")
    finally:
        results_writer.close()
        tcp_client_socket.close()
def port_scan(ip_adress:'str',output_file_path:'str',start_port:'int',end_port:'int'=0) ->'None':
    #generating the range of ports to iterate over :
    port_range=None
    if end_port==0:
        port_range=range(start_port,start_port+1)
    else:
        port_range = range(start_port, end_port+1)


    for port in port_range:
        thread=threading.Thread(target=tcp_port_scan,args=(ip_adress,port,output_file_path))
        thread.start()
        thread.join()

def main():
    #the driver code :
    args=sys.argv[1:]
    if validate_arguments(' '.join(args)):
        command_parts=argparse(' '.join(args))
    #now everything is validated , we do not need to re check to structure of the script
        if '--help' in command_parts:
            print(f"{usage}")
            return
        elif '--version' in command_parts:
            print(f"{version}")
            return
        ip_adress=command_parts['--ip']
        output_file_path=(command_parts['--output'] if '--output' in command_parts else 'report.txt')                              #retrieving the file path
        #writing the first part of the report :
        start = datetime.datetime.now()
        write_report(
            f"[+] ip adress scanned : {ip_adress}\n[+] Scan type : tcp connect scan\n[+] start time : {start}\n[+] port report result : \n",output_file_path)
        ####################################################################################################################
        ports=command_parts['--port']
        if '-' in ports:
            start_port,end_port=ports.split('-')
            port_scan(validate_ip(ip_adress),output_file_path,int(start_port),int(end_port))
        else:
            port_list = ports.split(',')
            for port in port_list:
                 port_scan(validate_ip(ip_adress),output_file_path, int(port))
        end = datetime.datetime.now()
        write_report(
            f"[+] Total time elapsed : {end - start}\n[+] to see the results check the file porvided\n    And if not provided , see the default report in the current project directory:)\n",output_file_path)
    else:
        raise SystemExit(f"{usage}Syntax Error : read the help above")
    read_report(output_file_path)
if __name__=="__main__":
    main()
