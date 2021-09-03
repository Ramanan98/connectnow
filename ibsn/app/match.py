import redis
import knn_mod
import db_handle
from django.conf import settings
settings.configure(
	CHANNEL_LAYERS = {
		'default': {
			'BACKEND': 'channels_redis.core.RedisChannelLayer',
			'CONFIG': {
				"hosts": [('127.0.0.1', 6379)],
			},
		},
	}
	)
print("@ match.py Run this as a separate process. Don't import")
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_channel_(user_id):
	channel_name=redis_client.hget(user_id,"channel_name")
	# You can't decode "None"
	if not channel_name:
		print("Warning: user_id :",user_id," doesn't have a channel_name")
		return None
	return channel_name.decode('utf-8')

def pop_one_user():
	user_id=redis_client.spop('online')
	if user_id:
		return user_id.decode('utf-8')
	return None

def match_finder():
	user1 = pop_one_user()
	if user1:
		user2 = knn_mod.get_a_match(user1)
		if user2:
			# Make this user unavailable for matching
			redis_client.srem('online',user2)
			db_handle.set_offline(user2)
			return str(user1), str(user2)
		else:
			redis_client.sadd('online',user1)
			return None, None
	else:
		return None, None



def create_group_for_given_users(user1,user2):
	# At least one of the receievd users will always be not None
	print("Group received ",user1,user2)
	if user1:
		user1_channel=get_channel_(user1)
	if user2:
		user2_channel=get_channel_(user2)
	# no need to check if user2 is None in the below line.Coz one of them is always not None
	if user1==None:
		#do not notify user1 OPPONENT_NOT_FOUND.Timeout in client instead
		return

	if user2==None:
		#do not notify user1 OPPONENT_NOT_FOUND.Timeout in client instead
		return

	#user1 < user2
	if int(user1)>int(user2):
		user1,user2=user2,user1
		# swap the channels too
		user1_channel,user2_channel=user2_channel,user1_channel

	print(user1,user2)
	# create group & add channels
	group_name=''.join(["g_",user1,"_",user2])
	async_to_sync(channel_layer.group_add)(group_name,user1_channel)
	async_to_sync(channel_layer.group_add)(group_name,user2_channel)
	# store the group_name & opponent_id to redis
	redis_client.hset(user1,mapping={"group_name":group_name,"opponent_id":user2})
	redis_client.hset(user2,mapping={"group_name":group_name,"opponent_id":user1})

	async_to_sync(channel_layer.send)(user1_channel, {
		"type": "receive_from_server_side",
		"CMD": "OPPONENT_DETAILS",
		"id":user2
	})
	async_to_sync(channel_layer.send)(user2_channel, {
		"type": "receive_from_server_side",
		"CMD": "OPPONENT_DETAILS",
		"id":user1
	})

while True:
	# break
	# user1 is popped from redis. user2 is found based on isOnline flag in DB
	# print("Running...")
	user1,user2=match_finder()
	if user1!=None:
		if user2!=None:
			print(f" Match found: {user1} , {user2}")
			create_group_for_given_users(user1,user2)
		else:
			# put the user1 back to Redis so that match can be found for them again.If we dont put user1 back, user1 can be found as a match for someone (due to isOnline flag in DB) but user1 will never be returned from pop_one_user()
			redis_client.sadd('online',user1)
			print("no match...")
	# if there's no match, nothng is done..client can disconnect after a while or keep waiting for the user