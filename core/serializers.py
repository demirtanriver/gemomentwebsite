
from rest_framework import serializers
from .models import (
    Organisers, Stories, Senders, StorySenders,
    ImageContribution, VideoContribution, TextContribution
)

class OrganisersSerializer(serializers.ModelSerializer):
    """
    Serializer for the Organisers model.
    Includes only essential information to avoid exposing sensitive data.
    """
    class Meta:
        model = Organisers
        fields = ['first_name', 'last_name', 'email', 'date_joined']

class StoriesSerializer(serializers.ModelSerializer):
    """
    Serializer for the Stories model.
    Includes all fields for now.
    """
    class Meta:
        model = Stories
        fields = '__all__'

class SendersSerializer(serializers.ModelSerializer):
    """
    Serializer for the Senders model.
    """
    class Meta:
        model = Senders
        fields = ['email', 'name']

class StorySendersSerializer(serializers.ModelSerializer):
    """
    Serializer for the StorySenders model.
    This serializer is nested, so it also includes the sender's details.
    """
    sender = SendersSerializer()

    class Meta:
        model = StorySenders
        fields = ['story', 'sender', 'invitation_status', 'invited_at']

class ImageContributionSerializer(serializers.ModelSerializer):
    """
    Serializer for Image Contributions.
    Note: The 'image' field will automatically handle the URL to the S3 bucket.
    """
    class Meta:
        model = ImageContribution
        fields = '__all__'

class VideoContributionSerializer(serializers.ModelSerializer):
    """
    Serializer for Video Contributions.
    Includes a YouTube video ID if one is present.
    """
    class Meta:
        model = VideoContribution
        fields = '__all__'

class TextContributionSerializer(serializers.ModelSerializer):
    """
    Serializer for Text Contributions.
    """
    class Meta:
        model = TextContribution
        fields = '__all__'
