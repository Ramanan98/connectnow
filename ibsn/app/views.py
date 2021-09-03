from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import permission_classes,api_view,authentication_classes,renderer_classes
from .serializers import UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from . import db_handle
from . import knn_mod
import redis

r = redis.Redis(host=u'localhost', port=6379)

class UserCreate(APIView):
    def post(self, request, format='json'):
        temp_data=request.data.dict()
        temp_data['username']=temp_data['username'].lower()
        serializer = UserSerializer(data=temp_data)
        if serializer.is_valid():
            user = serializer.save()
            if user:		
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                db_handle.add_user(temp_data['username'],temp_data['birthday'],temp_data['state'],temp_data['age_min'],temp_data['age_max'],temp_data['pref_state'],temp_data['interests'])
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                       context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
        })

# @api_view(['POST'])
# @renderer_classes([JSONRenderer])
#Authorization: Token abcde..
@permission_classes([IsAuthenticated])
class Logout(APIView):
    def post(self, request, format=None):
        try:
            request.user.auth_token.delete()
        except Exception as e:
            print("Error at logout ", e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def set_preferences(request):
    result=db_handle.set_preferences(request.user.id,request.data["age_min"],request.data["age_max"],request.data["pref_state"])
    if result!=0:
        return Response(result,status=status.HTTP_200_OK)
    return Response(0,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def set_interests(request):
    result=db_handle.set_interests(request.user.id, request.data['interests'])
    if result!=0:
        return Response(result,status=status.HTTP_200_OK)
    return Response(0,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def get_preferences_and_interests(request):
    result=db_handle.get_preferences_and_interests(request.user.id)
    if result!=0:
        return Response(result,status=status.HTTP_200_OK)
    return Response(0,status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@renderer_classes([JSONRenderer]) 
@permission_classes([IsAuthenticated])
def get_profile(request):
    result=db_handle.get_profile(request.data['id'])
    if result!=0:
        return Response(result,status=status.HTTP_200_OK)
    return Response(0,status=status.HTTP_400_BAD_REQUEST)