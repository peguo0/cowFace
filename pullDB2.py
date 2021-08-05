# import sqlite3 #Importing the module

# # conn = sqlite3.connect("jdbc:db2://pcon04:50000/LICTP", 'randsgp1', 'lsF10Zgp')

# conn = sqlite3.connect("jdbc:db2://pcon04:50000/LICTP")

# conn = sqlite3.connect("database.db")
# curr = conn.cursor()

# createTableCommand = """CREATE TABLE NSA_DATA (
# username VARCHAR(50),
# phonenumber VARCHAR(15),
# password VARCHAR(50),
# baddeedcount INT,
# secrets VARCHAR(250)
# );"""

# curr.execute(createTableCommand)
# conn.commit()

import ibm_db
import ibm_db_dbi
import csv

dbname="LICTP"
dbhost="pcon04"
dbport=50000
dbprotocol="TCPIP"
username="randsgp1"
password="lsF10Zgp"

dsn = "DATABASE=%s;HOSTNAME=%s;PORT=%s;PROTOCOL=%s;UID=%s;PWD=%s" % (
    dbname,
    dbhost,
    dbport,
    dbprotocol,
    username,
    password,
)
conn = ibm_db_dbi.Connection(ibm_db.connect(dsn, '', ''))
curr = conn.cursor()

# fetchData = '''SELECT * from tp.cross_brd where 
#             anml_key in (22865384,23893633,23916772,23969065,24252638,24821778,25003179,25214638,25248354,26029897,26046466,26367701,26753287,26865417,27281297,27297322,27301529,27318696,27496537,27716809,27822669,28550613,28571430,28571861,28576770,28785835,28877464,28926812,28944412,28944415,28955181,29057307,29066111,29169762,29466618,29839895,29883890,30293956,30350203,30494314,30584214,31174795,31292782,31318884,31340283,32659965,32704907,32865206,33581370,33581371,33646688,33660394,33846708,33895735,34330793,34331496,34331498,34335422,34339544,34344164,34344165,34344173,34344180,34347091,34359212,34366910,34370433,34374710,35127865,35155546,35204315,35774853,35779696,35779698,35781566,35781745,35783562,35783813,35791693,35791694,35791695,35792348,35794106,35796276,35796532,35797989,35798005,35798010,35798015,35800265,35800266,36480707,37144495,37146089,37148093,37149711,37149713,37150418,37150754,37154944,37154951,37156276,37158001,37159736,37159738,37160852,37162546,37164927,37169616,37169617,37169628,37169636,37169637,37170871,37172666,37175587,37871250,38464108,38464909,38470584,38470587,38472584,38473130,38473542,38473547,38477267,38479238,38480763,38480771,38480999,38481429,38481432,38481436,38481440,38486675,38487918,38487922,38493610,38493611,38493616,38495333,38497531,38497540,38502669,38502717,38513375,38767505,38767507,38805167,38805168,38840722,38840733,38872637,38943450,39038095,39074676)
#             '''

fetchData = '''select t1.*, t3.eid, t3.st_date, t3.end_date, t4.ae_brd_cd
                from tp.herd_anml t1
                left join tp.electronic_id t3
                on t1.anml_key = t3.anml_key
                left join tp.animal t4
                on t1.anml_key = t4.anml_key
                where t1.map_ref = 'N066164478'
                and t1.herd_num = '2'
                and (t1.xfer_out_time > '2020-04-01' or t1.xfer_out_time is null)
                '''

curr.execute(fetchData)
# We use fetchall() method to store all our data in the 'answer' variable
answer = curr.fetchall()
column_names = [i[0] for i in curr.description]

with open('aaa.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(column_names)   # write header; 
    writer.writerows(answer)

f.close()
