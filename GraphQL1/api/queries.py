from ariadne import convert_kwargs_to_snake_case


def listPhones_revolver(obj, info):
    from .models import Phone
    try:
        phones = [Phone.to_dict() for Phone in Phone.query.all()]
        print(phones)
        payload = {
            "success": True,
            "phones": phones
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload


@convert_kwargs_to_snake_case
def getPhone_resolver(obj, info, id):
    from .models import Phone
    try:
        Phone = Phone.query.get(id)
        payload = {
            "success": True,
            "Phone": Phone.to_dict()
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Phone with id == {id} not found"]
        }
    return payload
