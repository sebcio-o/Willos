from rest_framework.exceptions import ParseError


class GetSerializerBasedOnAuthType:
    auth_type_serializers = {"email": None, "socials": None}

    def get_serializer_class(self):
        auth_type = self.request.data.get("auth_type")
        if not auth_type:
            raise ParseError("Please provide auth_type")
        elif auth_type == "email":
            return self.auth_type_serializers["email"]
        elif auth_type == "socials":
            return self.auth_type_serializers["socials"]
