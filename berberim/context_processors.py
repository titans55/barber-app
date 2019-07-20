def get_user(request):
    if request.user:
        return {
            'user': request.user
        }
    else: 
        return {
            'user': 'guest'
        }
    
