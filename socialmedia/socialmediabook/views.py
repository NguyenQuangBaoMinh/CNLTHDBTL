from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views import View
from drf_yasg.utils import swagger_auto_schema
from oauth2_provider.models import RefreshToken
from rest_framework import viewsets, status, permissions, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import authenticate, update_session_auth_hash
from django.core.mail import send_mail
from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Event, UserProfile, Survey, Question, Answer, Post, Reaction, CommunityGroup, GroupMembership, \
    ChatRoom, ChatMessage, Comment
from .paginators import get_pagination_class
from .serializers import UserSerializer, EventSerializer, UserProfileSerializer, SurveySerializer, PostSerializer, \
    ReactionSerializer, CommentSerializer, QuestionSerializer, CommunityGroupSerializer, GroupMembershipSerializer, \
    GroupPostSerializer, UserLoginResponseSerializer, ChatMessageSerializer, ChatRoomListSerializer, ChatRoomSerializer


def home(request):
    return render(request, 'index.html')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser]

    @action(detail=False, methods=['POST'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Thêm role mặc định khi đăng ký
        request.data['role'] = request.data.get('role', 'ALUMNI')
        user = serializer.save()

        return Response({
            'message': 'Đăng ký thành công. Vui lòng chờ quản trị viên xác nhận.',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            # Kiểm tra điều kiện xác thực dựa trên vai trò
            if user.role == 'FACULTY' and not user.is_verified:
                return Response({
                    'error': 'Tài khoản chưa được xác nhận'
                }, status=status.HTTP_403_FORBIDDEN)

            return Response({
                'message': 'Đăng nhập thành công',
                'user_id': user.id,
                'role': user.role
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Sai thông tin đăng nhập'
        }, status=status.HTTP_401_UNAUTHORIZED)

    class LoginView(APIView):
        def post(self, request):
            username = request.data.get('username')
            password = request.data.get('password')

            if not username or not password:
                return Response({
                    'error': 'Please provide both username and password'
                }, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(username=username, password=password)

            if user:
                refresh = RefreshToken.for_user(user)

                # Sử dụng serializer mới để lấy user data
                user_data = UserLoginResponseSerializer(user).data

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': user_data  # Trả về user data bao gồm is_verified
                }, status=status.HTTP_200_OK)

            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    pagination_class = get_pagination_class('Event')
    def create(self, request):
        # Kiểm tra quyền tạo sự kiện
        if request.user.role not in ['ADMIN', 'FACULTY']:
            return Response({
                'error': 'Chỉ quản trị viên và giảng viên mới được tạo sự kiện'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save(created_by=request.user)

        # Gửi thông báo về sự kiện (nếu cần)
        self.send_event_notifications(event)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def send_event_notifications(self, event):
        # Triển khai logic gửi thông báo sự kiện
        try:
            # Ví dụ: Gửi email cho các thành viên
            send_mail(
                f'Sự kiện mới: {event.title}',
                f'Sự kiện {event.title} đã được tạo. Chi tiết: {event.description}',
                'admin@example.com',
                # Thêm danh sách email người nhận
                fail_silently=False,
            )
        except Exception as e:
            # Ghi log lỗi nếu việc gửi email thất bại
            print(f"Lỗi gửi thông báo sự kiện: {e}")


class PasswordChangeView(View):
    def get(self, request):
        # Chỉ cho phép giảng viên truy cập
        if request.user.role != 'FACULTY':
            return redirect('home')
        return render(request, 'force_password_change.html')

    def post(self, request):
        user = request.user
        new_password = request.POST.get('new_password')

        user.set_password(new_password)
        user.password_change_required = False  # Cập nhật trạng thái đổi mật khẩu
        user.save()

        # Cập nhật phiên đăng nhập
        update_session_auth_hash(request, user)
        return redirect('home')


class AdminUserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['POST'])
    def verify_user(self, request, pk=None):
        user = self.get_object()

        # Chỉ xác nhận cho alumni hoặc faculty
        if user.role in ['ALUMNI', 'FACULTY']:
            user.is_verified = True
            user.save()

            # Gửi email thông báo
            send_mail(
                'Tài khoản đã được xác nhận',
                'Tài khoản của bạn đã được quản trị viên xác nhận.',
                'admin@example.com',
                [user.email],
                fail_silently=False,
            )

            # Nếu là faculty, gửi email với mật khẩu mặc định
            if user.role == 'FACULTY':
                default_password = 'ou@123'
                user.set_password(default_password)
                user.password_change_required = True
                user.save()

                send_mail(
                    'Thông Tin Tài Khoản Giảng Viên',
                    f'Mật khẩu mặc định của bạn là: {default_password}\n'
                    'Vui lòng đổi mật khẩu trong vòng 24h.',
                    'admin@example.com',
                    [user.email],
                    fail_silently=False,
                )

            return Response({'status': 'Người dùng đã được xác nhận'}, status=status.HTTP_200_OK)

        return Response({'error': 'Không thể xác nhận người dùng này'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def reject_user(self, request, pk=None):
        user = self.get_object()
        reject_reason = request.data.get('reason', 'Không đủ điều kiện')

        # Gửi email thông báo từ chối
        send_mail(
            'Tài Khoản Bị Từ Chối',
            f'Tài khoản của bạn đã bị từ chối. Lý do: {reject_reason}',
            'admin@example.com',
            [user.email],
            fail_silently=False,
        )

        # Xóa tài khoản hoặc đánh dấu
        user.is_active = False
        user.save()

        return Response({'status': 'Người dùng đã bị từ chối'}, status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_pagination_class('UserProfile')

    @action(detail=False, methods=['GET'])
    def my_profile(self, request):
        # Lấy profile của user hiện tại
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Người dùng chưa có thông tin profile'
            }, status=404)

    @action(detail=False, methods=['PUT', 'PATCH'])
    def update_profile(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            serializer = self.get_serializer(
                profile,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(
                serializer.errors,
                status=400
            )
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Người dùng chưa có thông tin profile'
            }, status=404)


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_pagination_class('Survey')
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['GET'])
    def get_questions(self, request, pk=None):
        """Lấy danh sách câu hỏi của khảo sát"""
        survey = self.get_object()
        questions = survey.questions.all().order_by('order')
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def submit_response(self, request, pk=None):
        """Nộp câu trả lời khảo sát"""
        survey = self.get_object()
        answers = request.data.get('answers', [])

        # Tạo response
        response = Response.objects.create(
            survey=survey,
            user=request.user
        )

        # Lưu từng câu trả lời
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            question = Question.objects.get(id=question_id)

            Answer.objects.create(
                response=response,
                question=question,
                answer_text=answer_data.get('answer_text', ''),
                selected_choice_id=answer_data.get('selected_choice_id'),
                rating_value=answer_data.get('rating_value')
            )

        return Response({
            'status': 'Nộp khảo sát thành công',
            'response_id': response.id
        })


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = get_pagination_class('Post')

    def get_queryset(self):
        # Lấy bài viết của người dùng hiện tại hoặc bài viết công khai
        return Post.objects.filter(
            Q(author=self.request.user) | Q(is_public=True)
        )

    @action(detail=True, methods=['POST'])
    def react(self, request, pk=None):
        """Thêm/cập nhật reaction cho bài viết"""
        post = self.get_object()
        reaction_type = request.data.get('reaction_type')

        reaction, created = Reaction.objects.get_or_create(
            user=request.user,
            post=post,
            defaults={'reaction_type': reaction_type}
        )

        if not created:
            reaction.reaction_type = reaction_type
            reaction.save()

        return Response({
            'status': 'Đã thêm reaction',
            'reaction': ReactionSerializer(reaction).data
        })

    @action(detail=True, methods=['POST'])
    def comment(self, request, pk=None):
        """Thêm bình luận vào bài viết"""
        post = self.get_object()

        if post.is_comments_locked:
            return Response({
                'error': 'Bình luận đã bị khóa'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(data={
            'post': post.id,
            'author': request.user.id,
            'content': request.data.get('content')
        })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityGroupViewSet(viewsets.ModelViewSet):
    queryset = CommunityGroup.objects.all()
    serializer_class = CommunityGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['POST'])
    def join_group(self, request, pk=None):
        group = self.get_object()

        # Kiểm tra điều kiện gia nhập nhóm
        if group.privacy_type == 'PRIVATE':
            return Response({
                'error': 'Nhóm này yêu cầu phê duyệt'
            }, status=403)

        membership, created = GroupMembership.objects.get_or_create(
            user=request.user,
            group=group
        )

        return Response({
            'status': 'Đã tham gia nhóm' if created else 'Đã là thành viên'
        })

    @action(detail=True, methods=['GET'])
    def members(self, request, pk=None):
        group = self.get_object()
        members = group.memberships.filter(is_active=True)

        serializer = GroupMembershipSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def create_post(self, request, pk=None):
        group = self.get_object()

        # Kiểm tra quyền đăng bài
        try:
            membership = GroupMembership.objects.get(
                user=request.user,
                group=group,
                is_active=True
            )
        except GroupMembership.DoesNotExist:
            return Response({
                'error': 'Bạn không có quyền đăng bài'
            }, status=403)

        serializer = GroupPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(group=group, author=request.user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class ChatRoomViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(
            participants=self.request.user
        ).order_by('-updated_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatRoomListSerializer
        return ChatRoomSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == 'create':
            # Lấy participant_id từ request data
            participant_id = self.request.data.get('participant_id')
            if participant_id:
                context['participants'] = [self.request.user.id, participant_id]
        return context

    @action(detail=True, methods=['POST'])
    def mark_read(self, request, pk=None):
        """Đánh dấu tất cả tin nhắn trong room là đã đọc"""
        chatroom = self.get_object()
        ChatMessage.objects.filter(
            chat_room=chatroom,
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def with_user(self, request):
        """Lấy hoặc tạo chat room với một user cụ thể"""
        other_user_id = request.query_params.get('user_id')
        if not other_user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Tìm chat room hiện có
        chat_room = ChatRoom.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user_id
        ).first()

        # Nếu không có, tạo mới
        if not chat_room:
            chat_room = ChatRoom.objects.create()
            chat_room.participants.set([request.user.id, other_user_id])

        serializer = self.get_serializer(chat_room)
        return Response(serializer.data)


class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(
            chat_room__participants=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        # Kiểm tra quyền truy cập chat room
        chat_room = serializer.validated_data['chat_room']
        if self.request.user not in chat_room.participants.all():
            raise permissions.PermissionDenied(
                "You are not a participant of this chat room"
            )

        serializer.save(sender=self.request.user)

        # Cập nhật last_message và last_message_time của chat room
        chat_room.last_message = serializer.validated_data['content']
        chat_room.last_message_time = serializer.instance.created_at
        chat_room.save()



class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Lọc comment theo post nếu có tham số
        post_id = self.request.query_params.get('post_id', None)
        if post_id:
            return Comment.objects.filter(post_id=post_id)
        return Comment.objects.all()

    def perform_create(self, serializer):
        # Lấy post_id từ request
        post_id = self.request.data.get('post_id')
        try:
            post = Post.objects.get(id=post_id)
            # Kiểm tra xem post có bị khóa comment không
            if post.is_comments_locked:
                return Response(
                    {'detail': 'Comments are locked for this post.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Tự động gán người dùng hiện tại làm tác giả
            serializer.save(author=self.request.user, post=post)
        except Post.DoesNotExist:
            return Response(
                {'detail': 'Invalid post ID.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        # Chỉ cho phép tác giả sửa comment
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': 'You do not have permission to edit this comment.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Chỉ cho phép tác giả xóa comment
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': 'You do not have permission to delete this comment.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)