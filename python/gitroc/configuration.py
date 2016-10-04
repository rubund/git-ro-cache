#!/usr/bin/env python3
#
#
#  Copyright (C) 2016 Ruben Undheim <ruben.undheim@gmail.com>
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

import re

class Element:
    def __init__(self, localpath, url, branch, rwro):
        self.updated = False
        self.matchurlslash = re.compile("^(.*/)([^/].*?)$")
        self.matchurlcolon = re.compile("^(.*:)([^:].*?)$")
        self.matchgit = re.compile("^(.*)(\.git)$")
        self.matchlocal = re.compile("^(.*)/([^/].*?)$")
        self.localpath = localpath
        self.url = url
        self._branch = branch
        self.rwro = rwro
        self.update_fields()

    def check_fields(self):
        if not self.updated:
            self.update_fields()

    def update_fields(self):
        m1 = self.matchurlslash.match(self.url)
        m2 = self.matchurlcolon.match(self.url)
        fullrepoandsuffix = ""
        if m1 != None and len(m1.groups()) >= 2:
            self._urlshort = m1.group(1)
            fullrepoandsuffix = m1.group(2)
        elif m2 != None and len(m2.groups()) >= 2:
            self._urlshort = m2.group(1)
            fullrepoandsuffix = m2.group(2)
        if fullrepoandsuffix == "":
            sys.stderr.write("Couldn't parse\n")
            return
        m3 = self.matchgit.match(fullrepoandsuffix)
        if m3 != None and len(m3.groups()) >= 2:
            self._reponame = m3.group(1)
            self._suffix = m3.group(2)
        else:
            self._reponame = fullrepoandsuffix
            self._suffix = ""
        m4 = self.matchlocal.match(self.localpath)
        if m4 != None and len(m4.groups()) >= 2:
            self._destsubdir = m4.group(1)
            self._localname = m4.group(2)
        else:
            self._destsubdir = ""
            self._localname = self.localpath

    @property
    def urlshort(self):
        self.check_fields()
        return self._urlshort

    @property
    def reponame(self):
        self.check_fields()
        return self._reponame

    @property
    def suffix(self):
        self.check_fields()
        return self._suffix

    @property
    def localname(self):
        self.check_fields()
        return self._localname

    @property
    def destsubdir(self):
        self.check_fields()
        return self._destsubdir

    @property
    def branch(self):
        self.check_fields()
        return self._branch

class Configuration:
    template = ""

    def __init__(self, path=".gitrocworkspace"):
        self.elements = []
        self.parse_file(path)

    def parse_file(self, path):
        fp = open(path, "r")
        content = fp.read()
        lines = content.split("\n")
        for l in lines:
            columns = l.split()
            if len(columns) >= 3:
                localpath = columns[0]
                url = columns[1]
                branch = columns[2]
                if len(columns) == 4:
                    rwro = columns[3]
                else:
                    rwro = 'ro'
                self.elements.append(Element(localpath, url, branch, rwro))
        fp.close()

    def __str__(self):
        s = ""
        for e in self.elements:
            s = s + e.localpath+" "+e.url+" "+e.branch+" "+e.rwro+"\n"
        return s

