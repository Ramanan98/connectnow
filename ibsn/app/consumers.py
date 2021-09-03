import time
import copy
import json
from . import redis_handle
from . import db_handle
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from rest_framework.authtoken.models import Token
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()


def get_user(token_key):
	try:
		token = Token.objects.get(key=token_key)
		return token.user
	except Exception as e:
		print("Error at get_user ", e)
		return None

def handle_ready(self,text_data_as_dict):
	if redis_handle.get_group_name(self.user.id):
		print(f"{self.user.id} already has a group_name.should EXIT before READY.can't READY\n")
		return -1
	# no need to call set_channel_name_in_hset coz channel name is already there since we're already connected
	redis_handle.set_profile_info_in_hset(self.user.id)
	redis_handle.add_user_to_bucket(self.user.id)
	print(f"READY {self.user.id} done")
	return 1

def send_message_to_group(self, text_data_as_dict):
	# print(text_data_as_dict)
	text_data_as_dict["sender_id"] = self.user.id
	text_data_as_dict["type"] = "handle_each_msg"
	group_name = redis_handle.get_group_name(self.user.id)
	# only self.send() needs str parameters.. everything else needs dict
	if group_name:
		# only self.send() needs str parameters.. everything else (group_send) needs dict
		async_to_sync(self.channel_layer.group_send)(
			group_name, text_data_as_dict)
		print(f"message has been sent to group {group_name} \n")
	else:
		# group_name None
		print(f"group name of {self.user} is {group_name}.So not sending the message\n")

def notify_opponent_left(user_id,opponent_id,opponent_channel_name):
	'''notify OPPONENT_LEFT if opponent exists'''
	if opponent_id:
		print(f"Since {user_id} has an opponent ,we need to notify the  opponent {opponent_id} ")
		# Since {self.user.id} has an opponent ,we need to notify the  opponent {opponent_id}
		async_to_sync(channel_layer.send)(opponent_channel_name, {
			"type": "receive_from_server_side",
			"CMD": "OPPONENT_LEFT",
			"info":"clients should disconnect now. connect again if you wanna get matched chat again"
		})
	else:
		print(f"{user_id} doesn't have an opponent")


def handle_exit(user_id):
	'''called when user wants to exit match mode or chat'''
	print(f"EXIT {user_id}")
	opponent_id, opponent_channel_name = redis_handle.exit_the_user(
				user_id)
	notify_opponent_left(user_id, opponent_id, opponent_channel_name)
	print(f"EXIT {user_id} done")

def handle_each_msg_clone(self,text_data_as_dict):
	'''handle_each_msg calls this.. Here for brevity'''
	# message sent directly from client will not have sender_id.Only the messages from group have sender_id
	text_data_as_dict = copy.deepcopy(text_data_as_dict)
	if "sender_id" in text_data_as_dict:
		# the below message is duplicate
		if text_data_as_dict["sender_id"] == self.user.id:
			print("@handle_each_msg: sender & receiver are same.Skipping\n")
			return
		else:
			#send message to actual client and return
			del text_data_as_dict["sender_id"]
			# Hide the type
			text_data_as_dict["type"] = "client"
			self.send(json.dumps(text_data_as_dict))
			print("Sent the message to actual client")
			return
	else:
		print("Warn: @handle_each_msg: there's no sender_id attached to the message.not supposed to happen")

def authenticate(self):
	token = self.scope["query_string"]
	if not token:
		print("Nothing was passed in query params")
		return None
	token = token.decode("utf-8")
	token = token.split("=")[1]
	user = get_user(token)
	if not user:
		#invalid token or malformed data
		print("get_user() failed.rejected")
		return None
	else:
		return user

def handle_connect(self):
	user = authenticate(self)
	if not user:
		self.close()
		return
	
	print("New authenticated connection ", user)
	self.user = user

	redis_handle.set_online(self.user.id, self.channel_name)
	db_handle.set_online(self.user.id)
	self.accept()
	print(f"{self.user} connected successfully")
	message=json.dumps({"CMD": "WAIT_FOR_OPPONENT"})
	self.send(message)
	print("sent WAIT_FOR_OPPONENT \n")

def cleanup_the_user(user_id):
	print(f"@cleanup_the_user: starting clean up of {user_id}")
	# if self.user.id has an opponent (say X),opponent's group_name and opponent_id will be deleted and  id of the X and channel_name will be returned so that we can notify X. 
	opponent_id, opponent_channel_name = redis_handle.exit_the_user(user_id)
	notify_opponent_left(user_id, opponent_id, opponent_channel_name)
	db_handle.set_offline(user_id)
	redis_handle.set_offline(user_id)
	print(f"clean up of {user_id} done.")	

def handle_real_disconnect(self,close_code):
	print(f"\nInitiating real disconnect of {self.user.id} ")
	
	cleanup_the_user(self.user.id)
	print(f"Disconnect complete.real disconnect; user_id: {self.user.id} close_code {close_code}")

class ChatConsumer(WebsocketConsumer):
	# We deal with groups for sending messages. # We deal with channels for sending commands
	def connect(self):
		handle_connect(self)
		
	def handle_each_msg(self,text_data_as_dict):
		handle_each_msg_clone(self,text_data_as_dict)

	def receive(self, text_data):
		if isinstance(text_data, str):
			text_data_as_dict = json.loads(text_data)

		if text_data_as_dict["CMD"] == "MSG":
			send_message_to_group(self,text_data_as_dict)
			return
		print(f"@receive: {text_data_as_dict} {self.user.id} {self.user} ")

	def receive_from_server_side(self, message):
		print("@receive_from_server_side \n ", message)
		message["type"] = "client"
		cmd = message["CMD"]
		if cmd == "OPPONENT_DETAILS":
			self.send(json.dumps(message))
			print(f"Sending {cmd} to client\n")
		# this gets called from disconnect()
		elif cmd == "OPPONENT_LEFT":
			print(f"Sending {cmd} to {self.user.id}")
			# send directly client OPPONENT_LEFT
			self.send(json.dumps(message))
			print(f"{cmd} sent to {self.user.id} \n")
		elif cmd == "ERROR":
			print(f"Sending {cmd} to {self.user.id}")
			# send directly client ERROR
			self.send(json.dumps(message))
			print(f"{cmd} sent to {self.user.id} \n")
		else:
			print("..place_holder...")

	def disconnect(self, close_code):
		# detection of disconnection of duplicate connection. # If self.channel_name exists in Redis ,exit+the-user and delete hash set.Coz real connection.else do nothing.Coz duplicate connection.
		# dont use "if not self.user"
		if not hasattr(self, 'user'):
			# unauthenticated connection. user.id doesn't exist
			print("warn: unauthenticated connection force disconnect")
			return

		# each connection has unique channel.We store channel of each connection.When stored channel and "current" channel are different,we conclude that this disconnect was caused by "duplicate connection" (Means user_id already existed in Redis with a diff channel_name)
		# if redis_handle.get_channel(self.user.id) == self.channel_name:
		handle_real_disconnect(self,close_code)
		# else:
		# 	print(f"duplicate connection disconnect {self.user.id}, close_code {close_code}\n")