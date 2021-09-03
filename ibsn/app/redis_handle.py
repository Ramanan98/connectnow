from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
channel_layer = get_channel_layer()
from . import db_handle
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)
print("****warning :using flushdb for logging out users in redis_handle.py .disable me in prod*** \n")
redis_client.flushdb()

def is_online(user_id):
	# check whether the key exists.This key has a "hash-set" as value
	if redis_client.exists(user_id) == 1:
		# already connected
		return True
		# not connected
	return False

def set_channel_name_in_hset(user_id, channel_name):
	'''load channel_name into redis'''
	redis_client.hset(user_id, mapping={"channel_name": channel_name})

def set_profile_info_in_hset(user_id):
	'''load profile info from db into Redis'''
	print(f"@set_profile_info_in_hset setting profile of {user_id}")
	username, gender, age, bio, gender_preference = db_handle.get_profile_and_preferences(user_id)
	if not username:
		print("No profile for user ", user_id)
		return -1
	print(username, gender, age, bio, gender_preference)
	profile_info = {"username": username, "gender": gender, "age": age, "bio": bio,"gender_preference": gender_preference}
	redis_client.hset(user_id, mapping=profile_info)
	print("profile has been set")
	return 1

def delete_user_hash_set(user_id):
	print(f"Deleting hash set of {user_id}")
	redis_client.delete(user_id)

def set_online(user_id, channel_name):
	set_channel_name_in_hset(user_id, channel_name)
	redis_client.sadd('online',user_id)
	print(redis_client.smembers('online'))

def set_offline(user_id):
	redis_client.srem('online',user_id)
	delete_user_hash_set(user_id)

def get_channel(user_id):
	channel_name = redis_client.hget(user_id, "channel_name")
	#cannot decode None
	if not channel_name:
		print(
			f"Warning: user_id :{user_id} doesn't have a channel_name.Redis might not have been flushed well")
		return None
	return channel_name.decode('utf-8')

def get_group_name(user_id):
	group_name = redis_client.hget(user_id, "group_name")
	#cannot decode None
	if not group_name:
		print(f"user_id :{user_id} doesn't have a group_name")
		return None
	return group_name.decode('utf-8')

def discard_group(group_name, channel_name):
	print(f"discarding group_name {group_name}")
	async_to_sync(channel_layer.group_discard)(group_name, channel_name)

def flush_group_and_return_opponent(user_id):
	if redis_client.hexists(user_id, "group_name"):
		group_name = get_group_name(user_id)
		print(f"user {user_id} has a group")
		# get the opponent_id
		opponent_id = redis_client.hget(user_id, "opponent_id")
		# remove opponent from group
		discard_group(group_name,get_channel(opponent_id))
		# remove group_name of opponent
		redis_client.hdel(opponent_id, "group_name")
		# remove opponent_id of opponent
		#-------------#
		redis_client.hdel(opponent_id, "opponent_id")
		# remove user from group
		discard_group(group_name,get_channel(user_id))
		# remove group_name of user
		redis_client.hdel(user_id, "group_name")
		# remove opponent_id of user
		redis_client.hdel(user_id, "opponent_id")
		return opponent_id
	else:
		print(f"user {user_id} doesn't have a group")
		return None

def exit_the_user(user_id):
	print(f"Exiting the user {user_id}")
	opponent_id = flush_group_and_return_opponent(user_id)
	if opponent_id:
		# return the opponent_id so that they can be notified OPPONENT_LEFT
		return opponent_id, get_channel(opponent_id)
	else:
		# user_id doesn't have an opponent.So we have no one to notify
		return None, None