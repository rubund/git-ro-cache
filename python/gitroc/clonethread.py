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

import threading
import queue
import os
import git

class CloneThread(threading.Thread):

    def __init__(self, ws):
        threading.Thread.__init__(self)
        self.ws = ws
        self.running = True

    def run(self):
        while self.running:
            try:
                e = self.ws.rwqueue.get(block=False)
                self.clone_repo(e)
                self.ws.rwqueue.task_done()
            except queue.Empty:
                break

    def clone_repo(self, e):
        if os.path.islink("%s/%s/%s" % (self.ws.path, e.destsubdir, e.localname)):
            os.system("rm -f '%s/%s/%s'" % (self.ws.path, e.destsubdir, e.localname))
        if os.path.isdir("%s/%s/%s" % (self.ws.path, e.destsubdir, e.localname)):
            repo = git.Repo("%s/%s/%s" % (self.ws.path, e.destsubdir, e.localname))
            repo.remotes['origin'].fetch()
            origin = repo.remotes['origin']
            try:
                if not e.branch in repo.heads:
                    repo.create_head(e.branch, origin.refs[e.branch])
                    repo.heads[e.branch].set_tracking_branch(origin.refs[e.branch])
                repo.heads[e.branch].checkout()
                repo.git.merge("--ff-only")
            except git.exc.GitCommandError as e:
                print("Git error %s" % e)
        else:
            os.system("mkdir -p '%s/%s'" % (self.ws.path, e.destsubdir))
            repo = git.Repo.clone_from(e.url, "%s/%s/%s" % (self.ws.path, e.destsubdir, e.localname))
            origin = repo.remotes['origin']
            try:
                if not e.branch in repo.heads:
                    repo.create_head(e.branch, origin.refs[e.branch])
                    repo.heads[e.branch].set_tracking_branch(origin.refs[e.branch])
                repo.heads[e.branch].checkout()
            except git.exc.GitCommandError as e:
                print("Git error %s" % e)
        print("%s/%s/%s (RW)" % (self.ws.path, e.destsubdir, e.localname))
