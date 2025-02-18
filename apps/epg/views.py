from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from .models import EPGSource
from .serializers import EPGSourceSerializer

class EPGDashboardView(View):
    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            sources = EPGSource.objects.all()
            serializer = EPGSourceSerializer(sources, many=True)
            return JsonResponse({'data': serializer.data}, safe=False)
        return render(request, 'epg/epg.html', {'epg_sources': EPGSource.objects.all()})

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = JSONParser().parse(request)
            serializer = EPGSourceSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'success': True, 'data': serializer.data}, status=201)
            return JsonResponse({'success': False, 'errors': serializer.errors}, status=400)
        return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)
