# https://iheanyi.com/journal/user-registration-authentication-with-django-django-rest-framework-react-and-redux/
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
	username = serializers.CharField(
			max_length=32,
			validators=[UniqueValidator(queryset=User.objects.all())]
			)
	password = serializers.CharField(min_length=8,write_only=True)

	def create(self, validated_data):
		# convert to lowecase in signup view
		user = User.objects.create_user(validated_data['username'])
		user.set_password(validated_data['password'])
		user.save()
		return user

	class Meta:
		model = User
		fields = ('username', 'password')
