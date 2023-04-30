from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import viewsets, status
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
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
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id', None))
        queryset = post.comments.all()

        return queryset

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id', None))
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['following__username']

    def get_queryset(self):
        return self.request.user.following.all()

    def perform_create(self, serializer):
        following_user = get_object_or_404(
            User, username=serializer.validated_data['following']
        )
        if self.request.user == following_user:
            raise serializer.ValidationError(
                {'detail': 'Вы не можете быть подписаны на самого себя!'}
            )
        serializer.save(user=self.request.user, following=following_user)
        response_serializer = self.get_serializer(instance=serializer.instance)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def get_object(self):
        return get_object_or_404(
            self.request.user.following,
            pk=self.kwargs['pk']
        )
