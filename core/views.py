# core/views.py

from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Organisers, Stories, Senders, StorySenders,
    ImageContribution, VideoContribution, TextContribution
)
from .serializers import (
    OrganisersSerializer, StoriesSerializer, SendersSerializer,
    StorySendersSerializer, ImageContributionSerializer,
    VideoContributionSerializer, TextContributionSerializer
)

# A ViewSet for a single Story, including all its content.
class StoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A read-only API endpoint for Stories.
    Includes a custom action to get all contributions for a specific story.
    """
    queryset = Stories.objects.all()
    serializer_class = StoriesSerializer

    @action(detail=True, methods=['get'])
    def contributions(self, request, pk=None):
        """
        Retrieves all contributions (image, video, text) for a single story.
        """
        try:
            story = self.get_object()
        except Stories.DoesNotExist:
            return Response(status=404, data={"error": "Story not found."})

        story_senders = StorySenders.objects.filter(story=story)
        
        # Collect all contributions
        image_contributions = ImageContribution.objects.filter(story_sender__in=story_senders)
        video_contributions = VideoContribution.objects.filter(story_sender__in=story_senders)
        text_contributions = TextContribution.objects.filter(story_sender__in=story_senders)

        # Serialize the data
        image_data = ImageContributionSerializer(image_contributions, many=True).data
        video_data = VideoContributionSerializer(video_contributions, many=True).data
        text_data = TextContributionSerializer(text_contributions, many=True).data

        return Response({
            'story_details': StoriesSerializer(story).data,
            'image_contributions': image_data,
            'video_contributions': video_data,
            'text_contributions': text_data,
        })

# List and Retrieve views for individual models
class OrganisersListView(generics.ListAPIView):
    queryset = Organisers.objects.all()
    serializer_class = OrganisersSerializer

class StoriesListView(generics.ListAPIView):
    queryset = Stories.objects.all()
    serializer_class = StoriesSerializer

class SendersListView(generics.ListAPIView):
    queryset = Senders.objects.all()
    serializer_class = SendersSerializer

class StorySendersListView(generics.ListAPIView):
    queryset = StorySenders.objects.all()
    serializer_class = StorySendersSerializer
