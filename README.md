# CloudBox

CloudBox was an attempt to practice a newly learnt framework , flask by picking up a sufficently complex project. CloudBox is a cloud storage API built with flask. 
[Read the documentation here.](https://documenter.getpostman.com/view/20100124/2s83mgGMr3)

### Features 
Here I'll list features (or part) of the API
 - Auth - Handles user authentication and authorization.
 - Store - Handles all logics partaining to storing and retrieving users files and folders (collectively referred to as assets).
 - Payment - Handles logic for users to buy more storage space.

### Technologies 
 - Flask
 - Databases
	 - PostgreSQL
 - ORM / ODM
	 - Flask SQL ALchemy ORM
	 - Flask Mongoengine ODM(MongoDB)
 - Storage services
	 - Cloudinary
	 - AWS S3 bucket
 - Payment services
	 - Paystack
 - Celery
 - Redis
 - Deployment
	 - Docker
	 - Github actions (CI/ CD)
	 - AWS EC2 
	 - Nginx

### Setup Locally

 1. Clone the project and navigate to the cloudbox directory.
 2. Run docker-compose -f docker-compose.dev.yml up -d —build

### Detailed specification.
The API enforces security on actions performed on an asset. 
For example, only the owner and editors of a file can delete an asset, update an asset and upload to an asset (folder asset).
Also, every asset has a any_one_access attribute that can be set initially by an asset owner and subsequently by the asset's editors. This feature controls who can view an asset and what actions they can perform on an asset. 
Refer to the documentation for more information on how the API works.

#### Entity relationship diagram.

<img width="1017" alt="Screen Shot 2022-09-29 at 1 55 10 PM" src="https://user-images.githubusercontent.com/63596779/193046805-5e0fce34-5e72-4071-aab2-d597ba6b4193.png">

#### Resources

 1. [Flask tutorial playlist](https://www.youtube.com/watch?v=MwZwr5Tvyxo&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH)
 2. [Mongoengine docs](https://docs.mongoengine.org/)
 3. [Flask Mongoengine docs](https://docs.mongoengine.org/projects/flask-mongoengine/en/latest/)
 4. [Flask SQLAlchemy docs](https://flask-sqlalchemy.palletsprojects.com/en/latest/)
 5. [Flask Mail Sendgrid](https://pypi.org/project/Flask-Mail-SendGrid/)
 6. [Flask Migrate](https://www.youtube.com/watch?v=ca-Vj6kwK7M&t=709s)
 7. [Flask Signals](https://flask.palletsprojects.com/en/2.2.x/signals/)
 8. [Celery with flask](https://flask.palletsprojects.com/en/1.1.x/patterns/celery/)
 9. [Github actions](https://www.youtube.com/watch?v=R8_veQiYBjI)
 10. [Publishing docker Images](https://docs.github.com/en/actions/publishing-packages/publishing-docker-images)
 11. [SSH for github actions](https://github.com/appleboy/ssh-action) 
 12. [Deploy Flask Application on EC2 with docker](https://www.youtube.com/watch?v=2tQ_Yn6O3f4&list=PL5KTLzN85O4K3zhnNPNCgE_Lt-pUsY7YO)
 
