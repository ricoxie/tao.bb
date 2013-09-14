#!/usr/bin/env python
#coding: utf-8
# vim: ai ts=4 sts=4 et sw=4 ft=python

import unittest
import sys
sys.path.append("..")

from url_normalize import url_normalize

'''
cases from 
http://en.wikipedia.org/wiki/URL_normalization
and
https://github.com/rbaier/urltools/blob/master/urltools/tests/test_urltools.py
'''
class TestUrlNormalize(unittest.TestCase):

    def t(self, in_url, ex_url):
        self.assertEqual(url_normalize(in_url), ex_url)
    
    def test_normalized(self):
        self.t('http://www.example.com' , 'http://www.example.com')

    def test_trim(self):
        self.t('   http://www.example.com    ' , 'http://www.example.com')
        self.t('   http://www.example.com/#' , 'http://www.example.com')
        self.t('   http://www.example.com/?' , 'http://www.example.com')
        self.t('   http://www.example.com./' , 'http://www.example.com')
        self.t('   http://www.example.com.:/' , 'http://www.example.com')
        self.t('   http://www.example.com:/' , 'http://www.example.com')

    def test_not_url(self):
        self.t('   *.*.*   ' , None)

    def test_idna(self):
        self.t('你好.cn' , 'http://xn--6qq79v.cn')
        
    def test_no_scheme(self):
        self.t('www.Example.com/' , 'http://www.example.com')

    def test_long_ip(self):
        self.t('2130706433', 'http://127.0.0.1')

    def test_scheme_lower_case(self):
        self.t('HTTP://www.Example.com/' , 'http://www.example.com')

    def test_url_upper_case(self):
        self.t('http://www.example.com/a%c2%b1b' , 'http://www.example.com/a%C2%B1b')

    def test_decode_unreserved(self):
        self.t('http://www.example.com/%7Eusername/' , 'http://www.example.com/~username')

    def test_default_port(self):
        self.t('http://www.example.com:80/bar.html' , 'http://www.example.com/bar.html')
        self.t('https://www.example.com:443/bar.html' , 'https://www.example.com/bar.html')

    # no tail / , this is difference from wikipedia
    def test_remove_tail_slashes(self):
        self.t('http://www.example.com///' , 'http://www.example.com')

    def test_remove_dot_seg(self):
        self.t('http://www.example.com/../a/b/../c/./d.html' , 'http://www.example.com/a/c/d.html')
        self.t('http://example.com/%25%32%35', 'http://example.com/%25')

    def test_remove_duplicate_slashes(self):
        self.t('http://www.example.com/foo//bar.html' , 'http://www.example.com/foo/bar.html')

    def test_sort_query(self):
        self.t('http://www.example.com/display?lang=en&article=fred' , 'http://www.example.com/display?article=fred&lang=en')

    # Removing default query parameters , this is difference from wikipedia
    # add = to empty param as some prog treat them differ
    def test_add_equal_sign(self):
        self.t('http://www.example.com/display?id&sort=ascending' , 'http://www.example.com/display?id=&sort=ascending')

    def test_remove_unsed_q_mark(self):
        self.t('http://www.example.com/?' , 'http://www.example.com')

    def test_query_encode(self):
        self.t('http://www.example.com/?q=你好' , 'http://www.example.com/?q=%E4%BD%A0%E5%A5%BD')
        
    def test_user_name(self):
        self.t('http://foo:bar@example.com' , 'http://foo:bar@example.com')
        self.t('http://foo:bar@EXAMPLE.com' , 'http://foo:bar@example.com')
        self.t('http://foo@EXAMPLE.com' , 'http://foo@example.com')
        self.t('http://foo:@EXAMPLE.com' , 'http://foo@example.com')
        self.t('http://:@EXAMPLE.com' , 'http://example.com')
        self.t('http://@EXAMPLE.com' , 'http://example.com')
        

if __name__ == '__main__':
    unittest.main()
