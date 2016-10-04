#!/usr/bin/env python3



import gitroc

c = gitroc.GitrocClient(destdir=".")

c.request_one("gitolite3@localhost:", "gitolite-admin", destsubdir="")

c.get_all()

c.close()
