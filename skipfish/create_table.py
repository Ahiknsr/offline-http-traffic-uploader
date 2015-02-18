import  sys , psycopg2

DATABASE = "testdb"
USER = "ahiknsr"


conn = psycopg2.connect(database = DATABASE , user = USER)


cur = conn.cursor()
cur.execute("select * from information_schema.tables where table_name=%s", ('transactions',))
if bool(cur.rowcount):
    if '--force' in sys.argv[1:]:
        cur.execute("DROP TABLE IF EXISTS transactions")
        cur.execute("CREATE TABLE transactions(target_id INT , id BIGSERIAL PRIMARY KEY , url TEXT , scope boolean, method TEXT,\
                     data TEXT, time REAL, time_human TEXT, raw_request TEXT, response_status TEXT, response_headers TEXT,\
                     response_body TEXT, binary_response boolean, session_tokens TEXT, login boolean, logout boolean)")
        conn.commit()
    else:
        conn.commit()
        print "table exits use --force to clear and recreate a new table"
else:
    cur.execute("CREATE TABLE transactions(target_id INT , id INT PRIMARY KEY , url TEXT , scope boolean, method TEXT,\
                data TEXT, time REAL, time_human TEXT, raw_request TEXT, response_status TEXT, response_headers TEXT,\
                response_body TEXT, binary_response boolean, session_tokens TEXT, login boolean, logout boolean)")

    conn.commit()

print 'created the table'

