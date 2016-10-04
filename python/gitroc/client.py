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




class GitrocClient:
    def __init__(self, destdir=".", gitroc_server=None):
        self.basedir = destdir
        if not gitroc_server: # If no server is given, use the local server
            getipsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            getipsock.connect(("gmail.com", 80))
            gitroc_server = str(getipsock.getsockname()[0])
            getipsock.close()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((gitroc_server, 19999))
        self.number = 0
        self.destsubdir = {}

    def request_url(self, fullurl, branch="master"):
        url = ""
        reponame = ""
        self.request_one(url, reponame, branch=branch)

    def request_one(self, url, reponame, branch="master", destsubdir=""):
        data = {}
        data['command'] = 'checkout'
        data['reponame'] = reponame
        data['url'] = url
        data['commit'] = branch
        data['mode'] = 0
        data['number'] = self.number
        jsondata = json.dumps(data)
        self.s.send(jsondata.encode('utf-8'))
        resp = recv_msg(self.s)
        self.destsubdir[self.number] = destsubdir
        self.number = self.number + 1

    def get_all(self):
        status = False
        while status == False:
            time.sleep(0.2)
            status = self.get_symlinks('status', path=self.basedir)

    def get_symlinks(self, command, path="."):
        data = {}
        data['command'] = command
        jsondata = json.dumps(data)
        self.s.send(jsondata.encode('utf-8'))

        resp = recv_msg(self.s)
        recv_jsondata = json.loads(resp)
        if 'symlinks' in recv_jsondata:
            for symlink in recv_jsondata['symlinks']:
                if 'symlink' in symlink:
                    if 'number' in symlink and self.destsubdir[symlink['number']] != "":
                        destsubdir = self.destsubdir[symlink['number']]+"/"
                    else:
                        destsubdir = ""
                    localpath = "%s/%s%s" % (path, destsubdir, symlink['reponame'])
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
