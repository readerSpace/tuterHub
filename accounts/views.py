from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from accounts.serializers import CurrentUserSerializer


class CurrentUserAPIView(RetrieveAPIView):
    serializer_class = CurrentUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
