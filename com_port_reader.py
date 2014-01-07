#!/usr/bin/python
# -*- coding: utf-8 -*-
import time, serial, threading, os, sys
import optparse


def init_parser(options):                                                     
           options.add_option("-f", "--frequency",
                              action = "store",
                              dest = "port_freq",
                              default = 57600, 
                              help = "Set port frequency. 57600 is default.")
           options.add_option("-t", "--port_type",
                              action = "store",
                              dest = "port_type",
                              default = '',
                              help = "Set path to port, like 'ttyM' or 'ttyCTI'. Nothing for Windows.")
           options.add_option("-l", "--create_logs",
                              action="store_true",
                              default = False,
                              dest = "create_logs",
                              help = "Set to create logs files. Only for reading mode.")
           options.add_option("-w", "--write_mode",
                              action="store_true",
                              default = False,
                              dest = "write_mode",
                              help = "Start to write to ports, instead of reading.")
           options.add_option("-n", "--ports_count",
                              action="store",
                              default = 59,
                              dest = "ports_count",
                              help = "Set number of existing ports. 59 by default.")

def check_options(options):
    if not options.port_freq:
        options.port_freq = int(options.port_freq)
    options.ports_count= int(options.ports_count)
    if options.create_logs:
        if not os.path.exists(os.path.join(os.getcwd(), "log_serial")):
            os.makedirs(os.path.join(os.getcwd(), "log_serial"))           

class Port(threading.Thread):
    def __init__(self, port, mutex, freq, port_type, logs, write_mode):
        threading.Thread.__init__(self)
        self.port_num = port
        self.freq = freq
        self.port_type = port_type
        self.logs = logs
        if self.logs:
            if self.port_type:
                self.log_file = open(os.path.join(os.getcwd(),"log_serial", str(self.port_type) + str(self.port_num) +".txt"), 'w', 0)
            else:
                self.log_file = open(os.path.join(os.getcwd(),"log_serial", "COM_" + str(self.port_num + 1) +".txt"), 'w', 0)
        self.write_mode = write_mode
        self.mutex = mutex

    def run(self):
        if self.port_type:
            self.ser_port = serial.Serial("/dev/" + str(self.port_type) + str(self.port_num), self.freq, timeout=0)
        else:
            self.ser_port = serial.Serial(self.port_num, self.freq, timeout=0)
        with self.mutex:
            print self.ser_port
        while True:
            time.sleep(0.5)
            if self.write_mode:
                if self.port_type:
                    self.ser_port.write(str(self.port_type) +  "-"  + str(self.port_num))
                else:
                    self.ser_port.write("COM"  + str(self.port_num + 1))
            else:
                data = self.ser_port.read(100)
                if data:
                    if self.logs: 
                        self.log_file.write(data + "\n")
                    else:
                        with self.mutex:
                            if self.port_type:
                                print "From port", str(self.port_type) +  "-"  + str(self.port_num), data
                            else:
                                print "From port", "COM" + str(self.port_num + 1), ":", data

if __name__ == "__main__":
    parser = optparse.OptionParser()
    init_parser(parser)
    (options, args) = parser.parse_args()
    check_options(options)
    ports = []; threads = []
    stdoutmutex = threading.Lock()
    print options
    for i in range(options.ports_count):
        port = Port(i, stdoutmutex, 
                    options.port_freq, 
                    options.port_type,
                    options.create_logs,
                    options.write_mode)
        ports.append(port)

    threads = threads + ports
    for thread in threads:
        thread.start()

    working = True
    while working:
        command = ""
        command = raw_input()
        if command == 'q': 
            working = False
            for thread in threads:
                if thread.isAlive():
                    try:
                        thread._Thread__stop()
                    except:
                        print str(thread.getName()), "could not be terminated"
         
