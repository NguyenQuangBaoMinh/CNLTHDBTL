from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserProfileViewSet, EventViewSet, SurveyViewSet, PostViewSet, CommunityGroupViewSet, \
    ChatRoomViewSet, ChatMessageViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user') #test API

router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'events', EventViewSet, basename='event')
router.register(r'surveys', SurveyViewSet, basename='survey')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'communities', CommunityGroupViewSet, basename='community')
router.register(r'rooms', ChatRoomViewSet, basename='chatroom')
router.register(r'messages', ChatMessageViewSet, basename='chatmessage')
router.register(r'comments', CommentViewSet, basename='comment')




urlpatterns = [
    path('api/', include(router.urls)),
    # Các URL khác
]