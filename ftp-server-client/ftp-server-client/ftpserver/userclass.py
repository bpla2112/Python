#!/usr/bin/python3
# FTP User Class
# Bernardo Pla - 3885008
# CNT 4713 - Project 1
# User helper class

class userclass:
    def __init__(self, uname, upass, urole):
        self.username = uname
        self.password = upass
        self.role = urole

    def __str__(self):
        return '[user: {0}, pass: {1}, role: {2}]'.format(self.username, self.password, self.role)

    def getuname(self):
        return self.username

    def getupass(self):
        return self.password

    def geturole(self):
        return self.role

    def setuser(self, newuname):
        self.username = newuname

    def setpass(self, newupass):
        self.password = newupass

    def setrole(self, newurole):
        self.role = newurole