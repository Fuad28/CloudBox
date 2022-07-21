from flask.signals import Namespace

from cloudbox.models import FolderAsset, User

#Create signals
my_signals= Namespace()
user_registered= my_signals.signal('user_registered')



# signals functions
@user_registered.connect
def create_root_folder(app, user: User):
    # create FolderAsset for user

    root_folder= FolderAsset(
        user_id= str(user.id),
        parent= "root",
        name= f"{user.first_name} root"
        )

    root_folder.save()
