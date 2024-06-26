from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters

from posts.models import Group, Post
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
    permission_classes = [AllowAny]


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
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """ViewSet for Follow model."""
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['following__username']

    def get_queryset(self):
        """Get all follows for the requesting user."""
        return self.request.user.following.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
