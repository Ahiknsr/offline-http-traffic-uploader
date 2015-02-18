First create a user account in postgresql using 
    sudo -u postgres createuser yourname 

Next create a database using
    sudo -u postgres createdb testdb -O yourname

Usage:

Change the DATABASE and USER in create_table.py and skipfish_uploader.py to your database name and user name

1) Create a table in database by using

python2 create_table.py 

2)Upload data to table by running

python2 skipfish_uploader.py -p /pathto/skipfishoutput/directory  

Incase you messed up the table clear the table by running python2 create_table.py --force

This is supposed to be integrated with Owtf database so few fields in table like targetid may be  redundant for you , session analysis is not supported as of now 
