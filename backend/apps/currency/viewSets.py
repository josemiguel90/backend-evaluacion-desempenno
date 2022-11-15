from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.extraPermissions import IsEvaluatorFromArea
from .serializers import Currency, CurrencySerializer, CurrencyMiniSerializer


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated, IsEvaluatorFromArea]

    @action(detail=False, methods=['GET'])
    def getActiveCoins(self, request):
        try:
            coins = Currency.objects.filter(active=True)
            return Response(CurrencySerializer(coins, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def getActiveCoin(self, request):
        try:
            coins = Currency.objects.filter(active=True)[0]
            return Response(CurrencyMiniSerializer(coins, many=False).data, status=status.HTTP_200_OK)
        except IndexError:
            message = "Por favor, sincronize la MONEDA BASE con el ZUN"
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def rebuildCoins(self, request):
        try:
            newCoin = request.data.get('coins')[0]
            if Currency.objects.filter(id=newCoin['id']).exists():
                coin = Currency.objects.get(id=newCoin['id'])
                coin.acronym = newCoin['acronym']
                coin.description = newCoin['description']
                coin.active = True
                coin.save()
            else:
                Currency.objects.create(
                    id=newCoin['id'],
                    acronym=newCoin['acronym'],
                    description=newCoin['description'],
                    active=True
                )
            for coin in Currency.objects.all():
                if coin.id != newCoin['id']:
                    coin.active = False
                    coin.save()
            return Response({'Coin list Rebuilded successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
