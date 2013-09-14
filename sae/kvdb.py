
import sae.const
import MySQLdb

from base62 import base62_encode, base62_decode
from sqlparams import SQLParams

class KVClient:
    '''
    saekv to mysql
    '''

    def get(self, k):
        code = base62_decode(k) 

        con = MySQLdb.connect(sae.const.MYSQL_HOST ,sae.const.MYSQL_USER , sae.const.MYSQL_PASS, sae.const.MYSQL_DB, int(sae.const.MYSQL_PORT));
        cur = con.cursor()

        sp = SQLParams('named', MySQLdb.paramstyle)
        sql = "SELECT url FROM taobb_urls WHERE id=:id LIMIT 1"
        sql, params = sp.format(sql, { 'id' : code, })

        cur.execute(sql, params)
        row = cur.fetchone()

        if row:
            return row[0]

        return None

    def set(self, *args):
        return True
