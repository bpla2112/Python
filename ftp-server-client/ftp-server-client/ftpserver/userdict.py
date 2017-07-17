#!/usr/bin/python3
# FTP User Class
# Bernardo Pla - 3885008
# CNT 4713 - Project 1
# User dictionary helper class

class userdict:
    isMatched = False

    def __init__(self):
        self.list = []

#handle new user creation
    def newUser(self, user):
        if user not in self.list:
            self.list.append(user)

    # retrieve the list contents
    def currentlist(self):
        return self.list

    def matchedUsers(self, username):
        global isMatched
        isMatched = False
        try:
            for user in self.list:
                isMatched = True
                return user
            if(isMatched == False):
                print("USER NOT FOUND")
        except KeyError:
            print("USER NOT FOUND")

