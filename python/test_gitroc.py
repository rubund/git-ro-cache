#!/usr/bin/env python3



import gitroc

c = gitroc.GitrocClient()

c.request_one("gitolite3@localhost:", "gitolite-admin")

c.get_all()

c.close()
