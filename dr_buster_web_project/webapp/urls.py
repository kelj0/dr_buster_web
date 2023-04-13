from django.urls import path
from .views import dr_buster_start_scan, upload_wordlist, get_available_wordlists, get_result

urlpatterns = [
    path('start_scan/', dr_buster_start_scan),
    path('upload_wordlist', upload_wordlist),
    path('get_wordlists/', get_available_wordlists),
    path('get_results/', get_result),
]