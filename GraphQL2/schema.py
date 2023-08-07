from models import (
    Users as UserModel,
    Wishlists as WishlistsModel,
    session
)
from graphql import GraphQLError
import graphene
from extensions import bcrypt
from graphene_sqlalchemy import (
    SQLAlchemyConnectionField,
    SQLAlchemyObjectType
)
from flask_jwt_extended import (
    create_access_token,
    # jwt_unauthorized_handler,
    create_refresh_token,
    get_jwt_identity,
    jwt_required, verify_jwt_in_request
)
from typing import Optional


test = str(
        bcrypt.generate_password_hash("test"),
        'utf-8'
    )
print(test)


# class Users(SQLAlchemyObjectType):
#     class Meta:
#         model = UserModel


class Users(SQLAlchemyObjectType):
	class Meta:
		model = UserModel
		interfaces = (graphene.relay.Node, )


class UserConn(graphene.relay.Connection):
	class Meta:
		node = Users


class Wishlists(SQLAlchemyObjectType):
    class Meta:
        model = WishlistsModel


class CreateUser(graphene.Mutation):
    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        password = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(Users)

    def mutate(root, info, first_name, last_name, email, password):
        new_user = UserModel(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password = str(
                bcrypt.generate_password_hash(password),
                'utf-8'
            )
        )
        session.add(new_user)
        session.commit()
        ok = True
        return CreateUser(ok=ok, user=new_user)


class LoginUser(graphene.Mutation):
    access_token = graphene.String()
    refresh_token = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, password):
        user = UserModel.query.filter_by(email=email).first()

        if user is None:
            raise GraphQLError('Incorrect email and/or password')
        
        if not bcrypt.check_password_hash(user.password, password):
            raise GraphQLError('Incorrect email and/or password')

        access_token = bcrypt.create_access_token(identity=email)
        refresh_token = bcrypt.create_refresh_token(identity=email)
        return LoginUser(access_token=access_token, refresh_token=refresh_token)    


class AddWishlist(graphene.Mutation): 
    class Arguments:
        title = graphene.String() 
        price = graphene.Int()
    ok = graphene.Boolean()
    wishlist = graphene.Field(Wishlists) 

    def mutate(root, info, title, price):
        uid = info.context['uid']
        user = session.query(UserModel).filter_by(email=uid).first()
        new_wishlist = WishlistsModel(
            title=title, 
            price=price,
            user=user
        )
        session.add(new_wishlist)
        session.commit()
        ok = True
        return AddWishlist(ok=ok, wishlist=new_wishlist)
    

class UpdateWishlist(graphene.Mutation):
    class Arguments:
        wishlist_id = graphene.Int()
        title = graphene.String()
        price = graphene.Int()
    ok = graphene.Boolean()
    wishlist = graphene.Field(Wishlists)

    def mutate(root, info, wishlist_id, title: Optional[str] = None, price: Optional[int] = None):
        wishlist = session.query(WishlistsModel).filter_by(id=wishlist_id).first()
        if title is not None:
            wishlist.title = title
        if price is not None:
            wishlist.price = price
        session.commit()
        ok = True
        return UpdateWishlist(ok=ok, wishlist=wishlist)
    

class DeleteWishlist(graphene.Mutation):
    class Arguments:
        wishlist_id = graphene.Int()
    ok = graphene.Boolean()
    wishlist = graphene.Field(Wishlists)

    def mutate(root, info, wishlist_id):
        wishlist = session.query(WishlistsModel).filter_by(id=wishlist_id).first()
        session.delete(wishlist)
        ok = True
        session.commit()
        return DeleteWishlist(ok=ok, wishlist=wishlist)
    

class PostAuthMutation(graphene.ObjectType):
    add_wishlist = AddWishlist.Field()
    update_wishlist = UpdateWishlist.Field()
    delete_wishlist = DeleteWishlist.Field()


class PreAuthMutation(graphene.ObjectType):
    create_user = CreateUser.Field()


class WishlistsQuery(graphene.ObjectType):
    find_wishlist = graphene.Field(Wishlists, id=graphene.Int())
    user_wishlists = graphene.List(Wishlists)

    def resolve_find_wishlist(root, info, id):
        return session.query(WishlistsModel).filter_by(id=id).first()
    
    def resolve_user_wishlists(root, info):
        uid = info.context['uid']
        user = session.query(UserModel).filter_by(email=uid).first()
        return user.Wishlists


class PreAuthQuery(graphene.ObjectType):
    all_users = graphene.List(Users)

    def resolve_all_users(root, info):
        return session.query(UserModel).all()


class UserMutation():
    create_user = CreateUser.Field()
    login_user = LoginUser.Field()


class UserQuery():
	# Allows sorting over multiple columns, by default over the primary key
    all_users = SQLAlchemyConnectionField(UserConn)
    user = graphene.relay.Node.Field(Users)
    user_by_email = graphene.List(Users, email=graphene.String())

    @jwt_required
    def resolve_user_by_email(self, info, **args):
        email = args.get("email")
        user_query = Users.get_query(info)
        users = user_query.filter_by(email=email).all()

        return users


class Mutation(UserMutation, AddWishlist, DeleteWishlist, UpdateWishlist, graphene.ObjectType):
	pass


class Query(UserQuery, WishlistsQuery, graphene.ObjectType):
	node = graphene.relay.Node.Field()


auth_required_schema = graphene.Schema(query=Query, mutation=PostAuthMutation)
schema = graphene.Schema(query=PreAuthQuery, mutation=PreAuthMutation)
