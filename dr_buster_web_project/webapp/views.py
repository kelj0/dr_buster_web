from django.core import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dr_buster.core import main as dr_buster_scan
from webapp.models import Scan, Wordlist
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.exceptions import ObjectDoesNotExist
import os

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'wordlist_id': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='ID of the wordlist to use',
            ),
            'url': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='url of the targeted server'
            ),
        },
        required=['wordlist_id', 'url'],
    ),
)
@api_view(['POST'])
def dr_buster_start_scan(request):
    '''
        Starts a new scan, returns id of a saved scan that you can use in get_result
    '''
    # Get the parameters from the request
    wordlist_id = request.data.get('wordlist_id')
    target_url = request.data.get('url')
    
    wordlist = Wordlist.objects.get(id=wordlist_id).file.decode("UTF-8")
    dirpath = os.path.dirname(os.path.realpath(__file__))
    wordlist_path = os.path.join(dirpath, 'temp_wordlists', f"{wordlist_id.replace('-', '')}.txt")
    with open(wordlist_path, 'w') as f:
        f.write(wordlist)

    report_path = dr_buster_scan(
        url=target_url,
        wordlist_path=wordlist_path,
        cli_run=False
    )

    scan = Scan()
    if not os.path.exists(report_path):
        scan.result = {
            'count': 0,
            'urls': ''
        }
    else:
        with open(report_path) as f:
            lines = f.readlines()
            scan.result = {
                'count': len(lines),
                'urls': lines
            }
    
    scan.save()

    return Response({'id': scan.id})


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['file'],
        properties={
            'file': openapi.Schema(
                type=openapi.TYPE_FILE,
                description='Wordlist file'
            )
        },
    ),
    responses={
        200: openapi.Response(description='ID of the saved wordlist', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID of the saved wordlist'
                )
            },
        )),
        400: openapi.Response(description='No file was provided', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Error message'
                )
            },
        ))
    }
)
@api_view(['POST'])
def upload_wordlist(request):
    '''
        Upload a new wordlist to service
        CLI usage: curl -X POST -F "file=@/path/to/wordlist.txt" http://localhost:8000/upload_wordlist/
    '''

    file = request.FILES.get('file')
    if file:
        wordlist = Wordlist.objects.create(file=file.read())

        # return the ID of the saved wordlist
        return Response({'id': wordlist.id})

    return Response({'error': 'No file was provided.'}, status=400)


@api_view(['GET'])
def get_available_wordlists(request):
    '''
        Fetch all used wordlists
    '''
    wordlists = Wordlist.objects.all()
    wordlists = [
            {
                'id': wordlist.id,
                'file': wordlist.file.decode('UTF-8')
            } 
        for wordlist in wordlists
    ]
    return Response(wordlists)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='scan_id',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='ID of the scan',
        )
    ]
)
@api_view(['GET'])
def get_result(request):
    '''
        Fetch results of a scan 
    '''
    scan_id = request.query_params.get('scan_id')
    try:
        scan = Scan.objects.get(id=scan_id)
        return Response(scan.result)
    except ObjectDoesNotExist:
        return Response('Scan not found', 404)
