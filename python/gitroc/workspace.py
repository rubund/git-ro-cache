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

from gitroc import client
from gitroc import configuration



class Workspace:
    def __init__(self, path="."):
        self.path = path
        self.cfg = configuration.Configuration(path+"/.gitrocworkspace")
        pass

    def checkout(self):
        c = client.GitrocClient(destdir=self.path)
        for e in self.cfg.elements:
            c.request_element(e)
        c.get_all()
        c.close()
