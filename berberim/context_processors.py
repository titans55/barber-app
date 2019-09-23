import os

def get_user(request):
    if request.user:
        return {
            'user': request.user
        }
    else: 
        return {
            'user': 'guest'
        }
    
def get_google_maps_api_key():

    return {
        'GOOGLE_MAPS_API_KEY' : os.environ['GOOGLE_MAPS_API_KEY']
    }