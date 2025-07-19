from django.urls import path
from .views import UserView, RegisterUserView, GetUserAuthTokenView


urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("get_auth_token/", GetUserAuthTokenView.as_view(), name="get_auth_token"),
    path("get_user/", UserView.as_view(), name="get_user"),
    # path('logout/', logout, name='logout'),
]
