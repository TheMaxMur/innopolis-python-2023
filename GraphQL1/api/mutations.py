from ariadne import convert_kwargs_to_snake_case
from api import db
from api.models import Phone


@convert_kwargs_to_snake_case
def createPhone_resolver(obj, info, name, os, cpu, ram, disk):
    try:
        phone = Phone(
            name=name, os=os, cpu=cpu, ram=ram, disk=disk
        )
        db.session.add(phone)
        db.session.commit()
        payload = {
            "success": True,
            "phone": phone.to_dict()
        }
    except ValueError:
        payload = {
            "success": False,
            "errors": [f"Input data incorrect"]
        }
    return payload


@convert_kwargs_to_snake_case
def deletePhone_resolver(obj, info, id):
    try:
        phone = Phone.query.get(id)
        if phone:
            db.session.delete(phone)
            db.session.commit()
            payload = {
                "success": True,
                "message": f"Phone with id == {id} delete sucsessfully"
            }
        else:
            payload = {
                "success": False,
                "errors": [f"Phone with id == {id} not found"]
            }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload


@convert_kwargs_to_snake_case
def updatePhone_resolver(obj, info, id, new_phone_data=None):
    try:
        phone = Phone.query.get(id)
        if new_phone_data is not None:
            for key, value in new_phone_data.items():
                setattr(Phone, key, value)
            db.session.commit()
            payload = {
                "success": True,
                "phone": phone.to_dict(),
            }
        elif not phone:
            payload = {
                "success": False,
                "errors": [f"Phone with id == {id} not found"]
            }
        else:
            payload = {
                "success": False,
                "errors": ["No data for update"]
            }
    except Exception as error:
        db.session.rollback()
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload
