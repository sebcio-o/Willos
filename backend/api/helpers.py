from rest_framework.exceptions import ParseError


def set_user_agent(request):
    agency = request.user.real_estate_agency
    if not agency:
        raise ParseError("This user isn't assigned to any agency")
    request.data._mutable = True
    request.data["agent"] = agency.id
    request.data._mutable = False
    return request
