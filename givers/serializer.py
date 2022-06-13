from rest_framework import serializers
from .models import Profile,OnDeliveryTransaction
import requests
from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class OnDeliveryTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model= OnDeliveryTransaction
        fields=(
            'id','ref','made_on','items_id','amount','delivery_address','delivered'
        )



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields='__all__'


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model=Token
        fields=('key','user')



def lendigo():
    url=' https://hacker-news.firebaseio.com/v0/topstories'
    response=requests.get(url)
    if response.status_code==200:
        print(response.status_code)
        response_data = response.json()
        return response_data['status'],response_data['data']
    response_data=response.json()
    return response_data['status'],response_data['message']
    