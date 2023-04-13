from django.core import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dr_buster.core import main as dr_buster_scan
from webapp.models import Scan, Wordlist


@api_view(['POST'])
def dr_buster_start_scan(request):
    '''
        Starts a new scan, returns id of a saved scan that you can use in get_result
        parameters:
        - wordlist_id: wordlist id that you got after uploading new wordlist
        - url: url that you want to scan
    '''
    # Get the parameters from the request
    wordlist_id = request.data.get('wordlist_id')
    target_url = request.data.get('url')
    
    wordlist = Wordlist.objects.get(id=wordlist_id)
    # create wordlist on path start stan rm from path
    wordlist_path = "" 
    # Run dr_buster with the given parameters
    report_path = dr_buster_scan(wordlist_path, target_url, cli_run=False)
    lines = open(report_path).readlines()
    count = len(lines)

    scan = Scan()
    if count > 0:
        scan.result = {
            'count': count,
            'urls': lines
        }
    saved_scan = scan.save()

    return Response({'id': saved_scan.id})



@api_view(['POST'])
def upload_wordlist(request):
    '''
        Upload a new wordlist to service
        CLI usage: curl -X POST -F "file=@/path/to/wordlist.txt" http://localhost:8000/upload_wordlist/
        parameters:
        - file: file
        description: file that you want to upload
        required: true
        type: file
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
    data = serializers.serialize('json', wordlists)
    return Response(data)


@api_view(['GET'])
def get_result(request):
    '''
        Fetch results of a scan 
        - scan_id: scan_id
        description: UUID of a scan that you want to fetch for
        required: true
        type: UUID
    '''
    scan_id = request.data.get('scan_id')
    scan = Scan.objects.query(id=scan_id)
    if scan:
        data = serializers.serialize('json', scan.result)
        return Response(data)
    return Response('Scan not found', 404)
