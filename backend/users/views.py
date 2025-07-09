from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer

# Create your views here.


class RegisterUserView(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # creates the user instance
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUserAuthTokenView(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        print(email, password)

        if not email or not password:
            return Response(
                "Email and Password are required", status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                "Invalid email or password", status=status.HTTP_400_BAD_REQUEST
            )
        token, created = Token.objects.get_or_create(user=user)

        return Response({"token": token.key})


class UserView(APIView):

    def get(self, request):
        # users = User.objects.filter(request.user)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
