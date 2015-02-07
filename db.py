import datetime
from flask import url_for
from pymongo import MongoClient
from flask import Flask

client = MongoClient('mongodb://ec2-52-0-171-169.compute-1.amazonaws.com:27017/')
db = client['test_database']
collection = db['test-collection']

#given username, check if this user exists
def check_user_exist(a):
	return collection.find_one({'username':a})!=None

def check_user_password_right(a,b):
	return collection.find_one({'username':a,'password':b})!=None

def add_user(a,b,c):
	if check_user_exist(a):
		return False
	collection.insert({'username':a,'password':b,'name':c,'friends':[],'movies':[]})
	return True

def get_user_name(a):
	if not check_user_exist(a):
		return False
	tmp_user=collection.find_one({'username':a})
	return tmp_user['name']

def get_friends(a):
	if not check_user_exist(a):
		return False
	tmp_user=collection.find_one({'username':a})
	return tmp_user['friends']

def friend_exist(a,b):
	return b in collection.find_one({'username':a})['friends']


def add_friend(a,b):
	if not check_user_exist(a) or not check_user_exist(b) or friend_exist(a,b):
		return False
	collection.update({'username':a},{'$push':{'friends':b} } )
	return True


def remove_friend(a,b):
	if not check_user_exist(a) or not friend_exist(a,b):
		return False
	collection.update({'username':a},{'$pull':{'friends':b} } )
	return True

def movie_exist(a,b):
	return b in collection.find_one({'username':a})['movies']

def get_movies(a):
	if not check_user_exist(a):
		return False
	tmp_user=collection.find_one({'username':a})
	return tmp_user['movies']


def add_movie(a,b):
	if not check_user_exist(a) or movie_exist(a,b):
		return False
	collection.update({'username':a},{'$push':{'movies':b} } )
	return True


def remove_movie(a,b):
	if not check_user_exist(a) or not movie_exist(a,b):
		return False
	collection.update({'username':a},{'$pull':{'movies':b} } )
	return True


