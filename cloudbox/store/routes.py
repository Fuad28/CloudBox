from flask import Blueprint
from flask_restful import Api
from .resources import Folder, FolderContent, File, AssetEditors, AssetViewers, GeneralAccess

store= Blueprint('store', __name__, url_prefix='/api/v1/store/')
store_api= Api(store)


store_api.add_resource(Folder, "/folders/", "/folders/<string:id>/")
store_api.add_resource(FolderContent, "/folders/content/", "/folders/<string:id>/content/")
store_api.add_resource(File, "/files/<string:id>/")
store_api.add_resource(AssetEditors, "/assets/<string:id>/editors/")
store_api.add_resource(AssetViewers, "/assets/<string:id>/viewers/")
store_api.add_resource(GeneralAccess, "/assets/<string:id>/access-type/")


"""
add_resource can take multiple endpoints=> api.add_resource(HelloWorld, '/','/hello')

reqparse => incoming requests

args = parser.parse_args(strict=True) => Calling parse_args with strict=True ensures that an error is thrown if the request includes arguments your parser does not define.

marshall_wit and fields => more like serializers

utility func=>
def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


structure=> args => fields => Resource => add_resource (at the end)
"""