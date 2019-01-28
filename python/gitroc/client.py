#!/usr/bin/env python3
#
#
#  Copyright (C) 2015,2016 Ruben Undheim <ruben.undheim@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import os
import sys
import socket
import time
import json
import struct



def recv_msg(sock):
    raw_msglen = sock.recv(4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    return recvall(sock, msglen)


def recvall(sock, n):
    data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet.decode('utf-8')
    return data

def send_msg(sock, msg):
    msg = struct.pack('>I', len(msg)) + msg
    partsize = 1000
    n = 0
    while len(msg) > n:
        if len(msg) > n + partsize:
            thissize = partsize
        else:
            thissize = len(msg) - n
        part = msg[n:n + thissize]
        n = n + thissize
        sock.send(part)


class GitrocClient:
    def __init__(self, destdir=".", gitroc_server=None, fetch=True):
        self.basedir = destdir
        if not gitroc_server: # If no server is given, use the local server
            gitroc_server = "localhost"
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((gitroc_server, 19999))
        self.number = 0
        self.destsubdir = {}
        self.localname = {}
        self.fetch = fetch

    def request_url(self, fullurl, localname=None, branch="master", destsubdir=""):
        url = ""
        reponame = ""
        suffix = ".git"
        self.request_one(url, reponame, localname=localname, suffix=suffix, branch=branch, destsubdir=destsubdir)

    def request_one(self, url, reponame, localname=None, suffix=".git", branch="master", destsubdir=""):
        data = {}
        data['command'] = 'checkout'
        data['reponame'] = reponame+""+suffix
        data['url'] = url
        data['commit'] = branch
        if self.fetch:
            data['mode'] = 0
        else:
            data['mode'] = 1
        data['number'] = self.number
        data['version'] = 2
        jsondata = json.dumps(data)
        send_msg(self.s, jsondata.encode('utf-8'))
        resp = recv_msg(self.s)
        self.destsubdir[self.number] = destsubdir
        if not localname:
            self.localname[self.number] = reponame
        else:
            self.localname[self.number] = localname
        self.number = self.number + 1

    def request_element(self, element):
        url = element.urlshort
        reponame = element.reponame
        suffix = element.suffix
        localname = element.localname
        destsubdir = element.destsubdir
        branch = element.branch
        self.request_one(url, reponame, localname=localname, suffix=suffix, branch=branch, destsubdir=destsubdir)

    def get_all(self):
        status = False
        while status == False:
            time.sleep(0.2)
            status = self.get_symlinks('status', path=self.basedir)

    def get_symlinks(self, command, path="."):
        data = {}
        data['command'] = command
        jsondata = json.dumps(data)
        send_msg(self.s, jsondata.encode('utf-8'))

        resp = recv_msg(self.s)
        recv_jsondata = json.loads(resp)
        if 'symlinks' in recv_jsondata:
            for symlink in recv_jsondata['symlinks']:
                if 'symlink' in symlink:
                    if 'number' in symlink and self.destsubdir[symlink['number']] != "":
                        destsubdir = self.destsubdir[symlink['number']]+"/"
                    else:
                        destsubdir = ""
                    localpath = "%s/%s%s" % (path, destsubdir, self.localname[symlink['number']])
                    print(localpath)
                    os.system("""
mkdir -p %s
cd %s
ln -sfT %s %s
    """ % (os.path.dirname(localpath), os.path.dirname(localpath), symlink['symlink'], os.path.basename(localpath)))
        return recv_jsondata['complete']

    def close(self):
        self.s.close()
        self.number = 0

    def __del__(self):
        pass
