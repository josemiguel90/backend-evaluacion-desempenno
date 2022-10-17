from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from apps.evaluation_in_area.models import MeliaAspect
from apps.evaluation_in_area.serializers.melia_aspect import MeliaAspectSerializer


class MeliaAspectEditionDeletionView(DestroyAPIView, UpdateAPIView):

    queryset = MeliaAspect.objects.all()
    serializer_class = MeliaAspectSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class MeliaAspectCreationView(CreateAPIView):

    queryset = MeliaAspect.objects.all()
    serializer_class = MeliaAspectSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class MeliaAspectListView(ListAPIView):

    queryset = MeliaAspect.objects.all()
    serializer_class = MeliaAspectSerializer
    permission_classes = [IsAuthenticated]


class MeliaAspectRetrieveView(RetrieveAPIView):

    queryset = MeliaAspect.objects.all()
    serializer_class = MeliaAspectSerializer
    permission_classes = [IsAuthenticated]
