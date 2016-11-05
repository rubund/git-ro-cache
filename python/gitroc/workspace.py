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
from gitroc import clonethread

import queue


class Workspace:
    def __init__(self, path="."):
        self.path = path
        self.cfg = configuration.Configuration(path+"/.gitrocworkspace")
        self.rwqueue = queue.Queue()
        self.nworkers = 8
        pass

    def checkout(self, fetch=True):
        c = client.GitrocClient(destdir=self.path, fetch=fetch)
        for e in self.cfg.elements:
            if e.rw:
                self.rwqueue.put(e)
            else:
                c.request_element(e)

        clone_threads = []
        for i in range(0, self.nworkers):
            tmp = clonethread.CloneThread(self)
            clone_threads.append(tmp)
            tmp.start()
        c.get_all()
        c.close()

        for t in clone_threads:
            t.join()
