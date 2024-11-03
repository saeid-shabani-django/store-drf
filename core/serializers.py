from djoser.serializers import UserCreateSerializer as Djosercreateserializer
from djoser.serializers import UserSerializer

class MyUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ['id','username','first_name']


class UserCreateSerializer(Djosercreateserializer):
    class Meta(Djosercreateserializer.Meta):
        fields =['id','email','username','password','first_name','last_name']










