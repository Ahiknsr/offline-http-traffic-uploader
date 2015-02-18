import os 
import sys
import hashlib
import argparse

import  psycopg2

from rawrequestparser import HTTPRequest

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", help="increase verbosity",
                   action="store_true" )
parser.add_argument("-p", "--path", action="store" , dest="path", 
                    help="path for the skipfish output file")

args = parser.parse_args()


PATH = '.'
verbose = 0
DATABASE = "testdb"
USER = "ahiknsr"


if args.path:
    PATH = args.path
    # user may not ended path with /
    if PATH[-1] != '/':
        PATH = PATH + '/'

if args.verbosity:
    verbose = 1

#skipfish output contains transactions in directory which is inside the ouput directory
#User will input the top directory path, we will need the list of sub directories 
#sub_dirs will contain all sub directories of parent recursively
sub_dirs=[x[0] for x in os.walk(PATH)]
#A few requests are repeated as we don't requests repeated twice
#we remove same requests , file are differentiated based on check sum
file_dict= {}
#dirs will contain list of directories having transactions (no repeated transactions)
dirs = []
for dir in sub_dirs:
    #the directory may not contain any transaction 
    try:
        file_path = dir + '/request.dat'
        f = open(file_path)
        f.close()
        file_hash = hashlib.md5(open(file_path , 'rb').read()).hexdigest()
        file_dict [ file_hash ] = dir
    except:
        pass


for file in file_dict:
    dirs.append(file_dict[file])


if verbose:
    print str(len(dirs))+"  directories contain transactions "


def raw_data(data_dir):
    """
    This function takes a dirctory as input and returns a 
    list containg raw_request and raw_response as strings 
    """
    try:
        request = data_dir + '/request.dat'
        response = data_dir + '/response.dat'
        with open (request, 'r') as req_file_handler:
            raw_request = req_file_handler.readlines()
            request_str = ''
            for line in raw_request:
                request_str = request_str + line
                
        with open(response, 'r') as res_file_handler:
            raw_response = res_file_handler.readlines()
            response_str = ''
            for line in raw_response:
                response_str = response_str + line 

        return [request_str , response_str]

    except:
        #sometimes there will be no response to a request
        if verbose:
            print "Exception occured in directory " , data_dir
        return [request_str , ' ']


def get_data_for_db(request_str, response):
    """
    This function takes raw_request and raw_response as input and return list which 
    is later used for passing data to database
    """
    request = HTTPRequest(request_str)
    method = request.command
    url = 'http://' + request.headers['host'] + request.path
    raw_request = request_str
    try:
        if method == 'POST':
            request.handle()
            data = request.requestline
        else:
            data = ''
    except:
        data = ''

    if response != '':

        status , res_headers = response[:response.find('\n')] , response[response.find('\n')+1:]
        status_code = status[status.find(' ')+1:]
        res_headers, res_body = res_headers[:res_headers.find('\n\n')] , res_headers[res_headers.find('\n\n')+1:]
    
        #print '\n\n'
        #print "method: "+method
        #print "url: "+url
        #print "data: "+data
        #print "raw_request: "+raw_request
        #print "status: "+status
        #print "res_headers: "+res_headers
        #print "status_code: "+status_code
        try:
            res_body = unicode( res_body , "utf-8")
        except:
            res_body = ''

        return (url ,method ,data ,raw_request ,status_code ,res_headers ,res_body)


conn = psycopg2.connect(database = DATABASE , user = USER)
cur = conn.cursor()
query = "INSERT INTO transactions (url ,method ,data ,raw_request ,response_status ,response_headers ,response_body)\
         VALUES( %s, %s, %s, %s, %s, %s, %s)"


for dir in dirs:
    req_str, res_str = raw_data(dir)
    if req_str != '':
        db_data = get_data_for_db(req_str, res_str)
        try:
            cur.execute(query, db_data)
        except:
            print dir
            print db_data
        conn.commit()
    else:
        if verbose:
            print dir +" :  doesn't contain any transactions" 
        pass

conn.close()
