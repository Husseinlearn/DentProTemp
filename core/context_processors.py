def user_initials_processor(request):
    if request.user.is_authenticated:
        user = request.user
        initials = ""
        if user.first_name:
            initials += user.first_name[0]
        if user.last_name:
            initials += user.last_name[0]
        if not initials:
            initials = user.username[0] if user.username else "م"
        return {'user_initials': initials}
    return {'user_initials': "م"}
