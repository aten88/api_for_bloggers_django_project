from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import mixins, viewsets
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters, serializers

from posts.models import Group, Post, Follow
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    GroupSerializer,
    PostSerializer,
    CommentSerializer,
    FollowSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet for Post"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        """Save serialized data"""
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Group"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        """Get comments with post id"""
        post = get_object_or_404(Post, id=self.kwargs.get('post_id', None))
        return post.comments.all()

    def perform_create(self, serializer):
        """Save post if user is author"""
        post = get_object_or_404(Post, id=self.kwargs.get('post_id', None))
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """ViewSet for Follow model."""
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['following__username']

    def get_queryset(self):
        """Get all follows for the requesting user."""
        if not self.request.user.is_authenticated:
            return Follow.objects.none()
        return self.request.user.following.all()

    def perform_create(self, serializer):
        """Save follows after validating."""
        following_username = serializer.validated_data.get('following')
        if not following_username:
            raise serializers.ValidationError(
                {'following': 'Поле обязательно!'}
            )
        following_user = get_object_or_404(User, username=following_username)
        if self.request.user == following_user:
            raise serializers.ValidationError(
                {'detail': 'Вы не можете быть подписаны на самого себя!'}
            )
        if self.request.user.following.filter(
            following=following_user
        ).exists():
            raise serializers.ValidationError(
                {'detail': 'Вы уже подписаны на этого автора!'}
            )
        serializer.save(user=self.request.user, following=following_user)

    def get_object(self):
        """Get follow object with primary key for the requesting user."""
        return get_object_or_404(
            self.request.user.following,
            pk=self.kwargs['pk']
        )
