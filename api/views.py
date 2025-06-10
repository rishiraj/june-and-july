# api/views.py

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Profile, Swipe, Match, User
from .serializers import ProfileSerializer

class ProfileListView(generics.ListAPIView):
    """
    API endpoint to get a "deck" of potential matches.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Exclude users we've already swiped on and ourself
        swiped_user_ids = Swipe.objects.filter(swiper=user).values_list('swiped_id', flat=True)
        return Profile.objects.exclude(user=user).exclude(user_id__in=swiped_user_ids)


class SwipeView(views.APIView):
    """
    API endpoint to record a swipe and check for a match.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        swiper = request.user
        swiped_id = request.data.get('swiped_id')
        direction = request.data.get('direction')

        if direction not in ['left', 'right']:
            return Response({'error': 'Invalid direction'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            swiped_user = User.objects.get(id=swiped_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create the swipe
        swipe, created = Swipe.objects.get_or_create(
            swiper=swiper,
            swiped=swiped_user,
            defaults={'direction': direction}
        )

        if not created: # If swipe already existed
            return Response({'message': 'Already swiped on this user'}, status=status.HTTP_200_OK)

        # Check for a match if the swipe was 'right'
        match_made = False
        if direction == 'right':
            # Check if the other user has swiped right on us
            if Swipe.objects.filter(swiper=swiped_user, swiped=swiper, direction='right').exists():
                Match.objects.create(user1=swiper, user2=swiped_user)
                match_made = True

        return Response({
            'status': 'swipe recorded',
            'match_made': match_made
        }, status=status.HTTP_201_CREATED)
