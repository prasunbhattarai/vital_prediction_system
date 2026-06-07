from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Vitals
from .serializers import VitalsSerializer


@api_view(['GET', 'POST'])
def vitals_list(request):
    if request.method == 'GET':
        queryset = Vitals.objects.all()[:100]
        serializer = VitalsSerializer(queryset, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = VitalsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def vitals_detail(request, pk):
    try:
        instance = Vitals.objects.get(pk=pk)
    except Vitals.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = VitalsSerializer(instance)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = VitalsSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH':
        serializer = VitalsSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def vitals_recent(request):
    instance = Vitals.objects.order_by('-id').first()
    if not instance:
        return Response({'error': 'No data'}, status=status.HTTP_404_NOT_FOUND)
    serializer = VitalsSerializer(instance)
    return Response(serializer.data)
