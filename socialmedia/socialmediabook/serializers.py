from rest_framework import serializers
from .models import User, Post, Comment, Reaction, Event, UserProfile, Survey, Question, Choice, GroupPost, \
    CommunityGroup, GroupMembership, ChatRoom, ChatMessage


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'student_id', 'avatar', 'is_verified', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_verified': {'read_only': True},
            'role': {'read_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            student_id=validated_data.get('student_id'),
            avatar=validated_data.get('avatar'),
            is_verified=False,
            role='ALUMNI'
        )
        return user


# Serializer riêng cho response login
class UserLoginResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'student_id', 'avatar', 'is_verified', 'role']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    reactions_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'

    def get_reactions_count(self, obj):
        return obj.reactions.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'updated_at']


class ReactionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'post', 'author', 'reaction_type', 'created_at']


class EventSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'notification_sent': {'read_only': True}
        }


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'bio',
            'graduation_year',
            'company',
            'position',
            'location',
            'profileimg',
            'created_at',
            'updated_at'
        ]

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'avatar': obj.user.avatar.url if obj.user.avatar else None
        }


class SurveySerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = '__all__'

    def get_questions_count(self, obj):
        return obj.questions.count()


class ChoiceSerializer(serializers.ModelSerializer):
    """Serializer cho các lựa chọn trong câu hỏi"""
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer cho câu hỏi"""
    choices = ChoiceSerializer(many=True, read_only=True)  # Liên kết với các lựa chọn của câu hỏi

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'question_type', 'order', 'choices']


class GroupMembershipSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = GroupMembership
        fields = ['user_info', 'role', 'joined_at']

    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'avatar': obj.user.avatar.url if obj.user.avatar else None
        }


class GroupPostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = GroupPost
        fields = ['id', 'author', 'content', 'created_at', 'is_pinned', 'image']

    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'avatar': obj.author.avatar.url if obj.author.avatar else None
        }


class CommunityGroupSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    recent_posts = serializers.SerializerMethodField()

    class Meta:
        model = CommunityGroup
        fields = [
            'id', 'name', 'description',
            'privacy_type', 'created_at',
            'cover_image', 'members_count',
            'recent_posts'
        ]

    def get_members_count(self, obj):
        return obj.memberships.filter(is_active=True).count()

    def get_recent_posts(self, obj):
        return GroupPostSerializer(
            obj.posts.order_by('-created_at')[:5],
            many=True
        ).data


class ChatUserSerializer(serializers.ModelSerializer):
    """Serializer đơn giản cho thông tin user trong chat"""

    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'is_active']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = ChatUserSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'chat_room',
            'sender',
            'content',
            'created_at',
            'is_read'
        ]
        read_only_fields = ['created_at', 'sender']

    def create(self, validated_data):
        # Tự động thêm sender từ context
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = ChatUserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id',
            'participants',
            'created_at',
            'updated_at',
            'last_message',
            'last_message_time',
            'unread_count'
        ]

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'content': last_msg.content,
                'sender': ChatUserSerializer(last_msg.sender).data,
                'created_at': last_msg.created_at
            }
        return None

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()

    def create(self, validated_data):
        # Lấy participants từ context
        participants = self.context.get('participants', [])
        if not participants:
            raise serializers.ValidationError("Participants are required")

        chatroom = ChatRoom.objects.create(**validated_data)
        chatroom.participants.set(participants)
        return chatroom


class ChatRoomListSerializer(serializers.ModelSerializer):
    """Serializer nhẹ hơn cho danh sách chat rooms"""
    other_participant = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id',
            'other_participant',
            'last_message_preview',
            'last_message_time',
            'updated_at'
        ]

    def get_other_participant(self, obj):
        current_user = self.context['request'].user
        other_user = obj.participants.exclude(id=current_user.id).first()
        if other_user:
            return ChatUserSerializer(other_user).data
        return None

    def get_last_message_preview(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'content': last_msg.content[:50] + '...' if len(last_msg.content) > 50 else last_msg.content,
                'is_read': last_msg.is_read,
                'created_at': last_msg.created_at
            }
        return None