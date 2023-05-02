from rest_framework import serializers

from posts.models import Group, Post, Comment, Follow, User


class GroupSerializer(serializers.ModelSerializer):
    """Serialize all fields Group model"""
    class Meta:
        model = Group
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    """Serialize all fields Post model"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ('author',)


class CommentSerializer(serializers.ModelSerializer):
    """Serialize all fields Comment model"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('author', 'post',)


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow model."""
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        required=False
    )
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        required=False
    )

    class Meta:
        model = Follow
        fields = ('id', 'user', 'following')
        read_only_fields = ('user',)

    def validate_following(self, value):
        """Validate following user."""
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                {'detail': 'Вы не можете быть подписаны на самого себя!'}
            )
        if self.instance and self.instance.following == value:
            return value
        if Follow.objects.filter(
            user=self.context['request'].user,
            following=value
        ).exists():
            raise serializers.ValidationError(
                {'detail': 'Вы уже подписаны на этого автора!'}
            )
        return value
