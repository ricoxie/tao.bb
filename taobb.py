#!/usr/bin/env python
#coding: utf-8
# vim: ai ts=4 sts=4 et sw=4 ft=python

import sys
import sae.const

from bottle import route, run, static_file, request, abort, redirect, response, error
from base62 import base62_encode, base62_decode
from hashlib import md5
from url_normalize import url_normalize
from qrcode import make as makeqrcode
from StringIO import StringIO
from bottle_mysql import Plugin as MySQLPlugin
from urlparse import urlsplit
from sqlparams import SQLParams
from untinyurl import untiny

BLACKLIST = ()
try:
    import blacklist

    BLACKLIST = tuple(blacklist.BLACKLIST)
except:
    pass

WHITELIST = ()
try:
    import whitelist

    WHITELIST = tuple(['.' + d for d in whitelist.WHITELIST])
except:
    pass


#MAX = 62 ** 5
MAX = 916132832

mysql_plugin = MySQLPlugin(dbuser=sae.const.MYSQL_USER, dbpass=sae.const.MYSQL_PASS, dbname=sae.const.MYSQL_DB,
                           dbhost=sae.const.MYSQL_HOST, dbport=int(sae.const.MYSQL_PORT))


def hashto62(url):
    m = md5()
    m.update(url)
    return int(m.hexdigest(), 16) % MAX


@error(404)
@route('/')
def index(error=None):
    return static_file('taobb.html', root='.')


@route('/favicon.ico')
def notfound():
    redirect('http://www.taobao.com/favicon.ico', 302)


def code_to_url(code, db):
    sp = SQLParams('named', 'format')
    sql = "SELECT `url` FROM taobb_urls WHERE id=:id LIMIT 1"
    sql, params = sp.format(sql, {'id': code, })

    db.execute(sql, params)
    row = db.fetchone()

    if row:
        url = row['url']
        if url:
            return url

    return None


def key_to_url(request, key, db):
    key = key.strip('/')
    if len(request.query) == 0 and len(key) == 5:
        code = base62_decode(key)
        url = code_to_url(code, db)
        if url:
            try:
                sp = SQLParams('named', 'format')
                sql = "UPDATE taobb_urls SET access_time = now(), gmt_modified = now() , access_count = access_count + 1 WHERE id=:id LIMIT 1"
                sql, params = sp.format(sql, {'id': code, })
                db.execute(sql, params)
            except:
                pass

            return url

    return None


@route('/<key>', apply=[mysql_plugin])
def url(key, db):
    url = key_to_url(request, key, db)
    if url:
        redirect(url)

    abort(404, "NOT FOUND")


@route('/<key>/real', apply=[mysql_plugin])
def qrcode(key, db):
    url = key_to_url(request, key, db)
    if url:
        return url + "\n"

    abort(404, "NOT FOUND")


@route('/<key>/qrcode', apply=[mysql_plugin])
@route('/<key>/qrcode.png', apply=[mysql_plugin])
def qrcode(key, db):
    url = key_to_url(request, key, db)
    if url:
        response.content_type = 'image/png'
        img = makeqrcode(url)
        output = StringIO()
        img.save(output, 'PNG')
        contents = output.getvalue()
        output.close()
        return contents

    abort(404, "NOT FOUND")


def insert(db, code, url):
    key = base62_encode(code)

    # remove unused
    sql = """
    DELETE FROM `taobb_urls` WHERE id = :id and `access_time` + INTERVAL `access_count` + :ttl  DAY < NOW()
    """
    sp = SQLParams('named', 'format')
    sql, params = sp.format(sql, {
        'id': code,
        'ttl': 30
    })

    db.execute(sql, params)

    sql = """
    INSERT IGNORE INTO taobb_urls(  `id` ,  `key` ,  `url` , `access_time` ,  `gmt_create` ,  `gmt_modified` ) 
    VALUES (:id, :key, :url, now(),now(), now())
    """

    sp = SQLParams('named', 'format')
    sql, params = sp.format(sql, {
        'id': code,
        'key': key,
        'url': url,
    })

    if db.execute(sql, params):
        return key
    else:
        old_url = code_to_url(code, db)
        if old_url == url:
            return key
        else:
            return insert(db, code + 1, url)


@route('/d/save', method='POST', apply=[mysql_plugin])
def save(db):
    url = request.forms['url']
    if not url:
        return {'err': '请输入URL'}

    url = url_normalize(url)
    if not url:
        return {'err': '请输入有效的 URL'}

    surl = urlsplit(url)
    hostname = surl.hostname
    if hostname.endswith(BLACKLIST):
        return {'err': '不支持的域名'}

    if len(WHITELIST) > 0 and not ('.' + hostname).endswith(WHITELIST):
        return {'err': '仅支持阿里巴巴旗下网站域名'}

    code = hashto62(url)

    try:
        key = insert(db, code, url)
        return {'key': key, 'err': None}
    except:
        pass

    return {'err': '内部错误'}


@route('/d/long', method='POST')
def longurl():
    wanted = request.forms['url']
    longurl = None
    if wanted and len(wanted) < 25:
        if not wanted.startswith('http://'):
            wanted = 'http://' + wanted

    longurl = untiny(wanted)

    return {'wanted': wanted, 'long': longurl}


if __name__ == '__main__':
    debug = False
    if len(sys.argv) > 0:
        debug = True
    run(host='localhost', port=8008, debug=debug)
