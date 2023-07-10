# Full Stack Calorie Tracking API

This application allows users to log their daily calories, check whether they've met their daily requirement and fetch calories for food items which don't come with nutritional information. The main tasks were to create a Flask RESTful API, essential database models, and a test suite for implementing the following functionality:

1. Users can create new accounts and log in to existing accounts
2. All API calls are authenticated
3. There are three user privellege levels: `user`, `manager` and `admin`
4. The API provides filter capabilities and supports pagination when fetching user details and calorie records
5. In case number of calories is not supplied in a request, a call is made to the Nutritionix API get the number of calories in the entered meal

# Getting Started

## Installating Dependancies
Developers using this project must have [python3](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installation/) installed.

Once your virtual environment is ready, run:

```
pip install -r requirements.txt
```

## Setting up Environment Variables
Create `.env` in your the project directory and fill in the values:
```
SECRET_KEY="..."
NUTRITIONIX_API_KEY="..."
```
For instructions of generating your own SECRET_KEY, [click here](https://stackoverflow.com/questions/34902378/where-do-i-get-secret-key-for-flask).

## Running the server

Before proceeding ensure that your virtual environment has been activated. Not doing so can lead to messy module import errors. To run the app, open yor terminal and run:

```
python app.py
```

## Testing Suite

To run tests, add the following line to `.env`

```
FLASK_ENV="test"
```

Then run either of the following commands:

```
python test_models.py
python test_app.py
```

or

```
python -m unittest test_models.py
python -m unittest test_app.py
```

> Note: Running test_app.py might take longer than expected (depending on your internet speed) as it also tests data-fetching functionalities from Nutritionix's API

# API Reference

### Overview
* Base URL: The backend is assumed to be hosted at `http://127.0.0.1:5000`.
* Authentication: Authentication is handled by the Flask-Login library
* All responses from the API have a `success` key which has a boolean value

### Error Handling
Errors are returned as JSON and are formatted in the following manner:

```
{
    "success": False,
    "error": 404,
    "message": "Resource not found"
}
```

## Endpoints

### `POST /login`
- Accepts JSON formatted request containing user credentials
    - Returns success/failure message depending on credentials supplied
- Sample request:
```
{
    "username": "sample_user_name",
    "password": "sample_password"
}
```
- Successful response:
```
{
    "success": true,
    "username": username,
    "message": "Logged in successfully"
}
```

### `POST /signup`
- Accepts JSON formatted request containing user information for signup
- Creates a new user with the provided username, password, and expected calories

Sample request:
```
{
    "username": "sample_user_name",
    "password": "sample_password",
    "expected_calories": 2000
}
```
Successful response:
```
{
    "success": true,
    "username": "sample_user_name",
    "message": "User created successfully"
}
```
Error response:
```
{
    "success": false,
    "error": 422,
    "message": "User sample_user_name already exists"
}
```
- The API checks if the username is already taken and returns an error message if it is.
- Upon successful signup, a new user is created with the provided information and stored in the database.

### `GET /users`
- Requires authentication with a valid token
- Retrieves a list of users from the database based on the provided query parameters
- Supports filtering by `username`, `user_id`, and `role`
- Supports pagination with `page` and `limit` parameters
- Returns the list of users along with `total_count`, `page`, and `limit` information

Sample request:
```
{
    "username": "sample_user_name",
    "role": "admin",
    "page": 1,
    "limit": 10
}
```

Successful response:
```
{
    "success": true,
    "users": {
        "admins": [
            {
                "user_id": 1,
                "username": "sample_admin",
                "expected_calories": 2000
            }
        ],
        "managers": [],
        "users": []
    },
    "total_count": 1,
    "page": 1,
    "limit": 10
}
```
Error response:
```
{
    "success": false,
    "error": 403,
    "message": "Access forbidden"
}
```

### `PUT /users`
- Requires authentication with a valid token
- Allows updating user information such as `expected_calories` and `role`
- Supports updating `expected_calories` for the authenticated user or a specific user (if the authenticated user is a manager)
- Supports changing the role of a user if the authenticated user is a `manager` or `admin`
- Accepts JSON formatted request containing user information to be updated
- Returns success/failure message depending on the update operation

Sample request to update `expected_calories` for the authenticated user:
```
{
    "expected_calories": 2500
}
```
Successful response:
```
{
    "success": true,
    "message": "Expected calories updated"
}
```
Sample request to update the role of a user (only allowed for managers and admins):
```
{
    "username": "sample_user",
    "role": "admin"
}
```
Successful response:
```
{
    "success": true,
    "username": "sample_user",
    "previous_role": "user",
    "new_role": "admin",
    "message": "Role successfully updated"
}
```
Error response:
```
{
    "success": false,
    "error": 403,
    "message": "Access forbidden"
}
```
- The API checks the role of the authenticated user and performs the appropriate update operation.
- If the authenticated user's role is `user` or `manager`, they can update their own `expected_calories`.
- If the authenticated user is a `manager`, they can also update the `expected_calories` of a specific user by providing the `user_id` in the request.
- If the authenticated user is a `manager` or `admin`, they can change the role of a user by providing the `username` and `role` in the request.
- The request should include the Content-Type: application/json header to specify the JSON format.

### `DELETE /users`
- Requires authentication with a valid token
- Allows deleting user accounts
- Supports deleting the authenticated user's own account or a specific user's account (if the authenticated user is a manager or admin)
- Accepts JSON formatted request containing the username of the user to be deleted
- Returns success/failure message depending on the delete operation

Sample request to delete the authenticated user's own account:
```
{
    "username": "current_user"
}
```
Successful response:
```
{
    "success": true,
    "message": "Successfully deleted"
}
```
Sample request to delete a specific user's account (only allowed for managers and admins):
```
{
    "username": "sample_user"
}
```
Successful response:
```
{
    "success": true,
    "username": "sample_user",
    "message": "User sample_user successfully deleted"
}
```
Error response:
```
{
    "success": false,
    "error": 403,
    "message": "Access forbidden"
}
```
- The API checks the role and permissions of the authenticated user to perform the delete operation.
- If the authenticated user is a manager or admin, they can delete a specific user's account by providing the `username` in the request.
- If the authenticated user's role is `user` and they provide their own username in the request, their account will be deleted.
- Deleting an account will log out the user and remove all associated data from the database.
- The request should include the Content-Type: application/json header to specify the JSON format.

### `POST /logout`
- Requires authentication with a valid token
- Allows users to log out and end their session
- Accepts no request, any POST request to this endpoint will trigger functionality
- Returns success/failure message depending on the logout operation

Successful response:
```
{
    "success": true,
    "username": "current_user",
    "message": "Logged out successfully"
}
```
- The API will log out the authenticated user, invalidate the token, and end the session.
- After successful logout, the user will no longer have access to protected routes.

### `POST /session`
- Requires authentication with a valid token
- Retrieves the session information of the authenticated user
- Accepts no request, any POST request to this endpoint will trigger functionality
- Returns the username and role of the current user

Successful response:
```
{
    "success": true,
    "username": "current_user",
    "role": "user"
}
```
- The API will return the session information including the username and role of the currently authenticated user.
- This route is useful for clients to verify the session status and retrieve user information without performing any modifications to the session or user data.
- The request should include the Content-Type: application/json header to specify the JSON format.

### `GET /records`
- Requires authentication with a valid token
- Retrieves the records based on the specified filters and pagination parameters
- Returns a list of records or a single record if the `id` parameter is provided

Sample request:
```
{
    "date": "2023-06-15",
    "text": "example",
    "calories_min": 1000,
    "calories_max": 1500,
    "page": 1,
    "limit": 10
}
```
Successful response:
```
{
    "success": true,
    "records": [
        {
            "id": 1,
            "text": "example",
            "date": "2023-06-15",
            "time": "12:00:00",
            "calories": 1200,
            "is_below_expected": false
        },
        {
            "id": 2,
            "text": "example",
            "date": "2023-06-15",
            "time": "15:30:00",
            "calories": 1400,
            "is_below_expected": false
        }
    ],
    "total_count": 2,
    "page": 1,
    "limit": 10
}
```
- The API retrieves records based on the specified filters and pagination parameters.
- The request should include the Content-Type: application/json header to specify the JSON format.
- The available filters include:
  - date: Retrieves records for a specific date (format: "YYYY-MM-DD").
  - text: Retrieves records containing the specified text in the description.
  - calories_min: Retrieves records with calories greater than or equal to the specified value.
  - calories_max: Retrieves records with calories less than or equal to the specified value.
  - The pagination parameters include:
  - page: Specifies the page number for pagination (default is 1).
  - limit: Specifies the maximum number of records per page (default is 10).
- If the user has the role `user`, only their own records are retrieved.
- If the user has the role `admin`, they can retrieve records for all users.
- The response includes the list of records with their corresponding details such as ID, description, date, time, calories, and whether the calorie count is below the expected value.
- If the `id` parameter is provided, the API returns a single record matching the specified ID.
- If the user's role is unauthorized, a 403 Forbidden error is returned.

### `POST /records`
- Requires authentication with a valid token
- Adds a new record to the database
- If the user has the role `user` or `admin`, they can add a record
- If the user does not provide the calories parameter, the API will fetch the calorie data from the Nutritionix API based on the provided text parameter. If the food item does not exist in the Nutritionix database, an error response will be returned.

Sample request:
```
{
    "text": "Apple",
    "calories": 52
}
```
Successful response:
```
{
    "success": true,
    "message": "Added record"
}
```
- The API endpoint /records allows users to add a new record to the database.
- The request should include the Content-Type: application/json header to specify the JSON format.
- The request body should include the following parameters:
    - text: The description or name of the food item for the record.
    - calories: The number of calories for the food item.
- The user_id is determined based on the user's role:
    - If the user has the role `user`, their own user ID is used.
    - If the user has the role `admin`, they can specify the `user_id` in the request body to add a record for a specific user.
- The API automatically sets the date and time fields to the current date and time.
- If the record is added successfully, a success response with the message "Added record" is returned.
- If the user's role is unauthorized, a 403 Forbidden error is returned.

### `DELETE /records`
- Requires authentication with a valid token
- Removes a record from the database
- If the user has the role `user` or `admin`, they can delete a record

Sample request:
```
{
    "id": 12345
}
```
Successful response:
```
{
    "success": true,
    "message": "Successfully removed"
}
```
- The API endpoint `/records` allows users to delete a record from the database.
- The request should include the Content-Type: application/json header to specify the JSON format.
- The request body should include the following parameters:
    - id: The ID of the record to be deleted.
- If the user has the role `user`, they can only delete their own records. If the user has the role `admin`, they can delete any record.
- If the specified record does not exist, an error response will be returned.
- If the record is deleted successfully, a success response with the message "Successfully removed" is returned.
- If the user's role is unauthorized, a 403 Forbidden error is returned.

### `PUT /records`
- Requires authentication with a valid token
- Modifies an existing record in the database
- If the user has the role `user` or `admin`, they can modify a record

Sample request:
```
{
    "id": 12345,
    "text": "Updated text",
    "calories": 500
}
```
Successful response:
```
{
    "success": true,
    "message": "Successfully modified"
}
```
- The API endpoint `/records` allows users to modify an existing record in the database.
- The request should include the Content-Type: application/json header to specify the JSON format.
- The request body should include the following parameters:
    - id: The ID of the record to be modified.
    - text (optional): The updated text for the record.
    - calories (optional): The updated calorie value for the record.
- If the specified record does not exist, an error response will be returned.
- If the user has the role `user`, they can only modify their own records. If the user has the role `admin`, they can modify any record.
- If the `text` parameter is provided, the record's text will be updated with the new value.
- If the `calories` parameter is provided, the record's calorie value will be updated with the new value.
- If the record is modified successfully, a success response with the message "Successfully modified" is returned.
- If the user's role is unauthorized, a 403 Forbidden error is returned.

## Assumptions/Choices

1. I had two options for sending data to the API - URL queries or JSON. Although URL queries are widely used, I had security concerns about them appearing in Apache logs and compromising sensitive information, and therefore decided to go with JSON.

1. The requirement document says "a regular user would only be able to CRUD on their owned records, a user manager would be able to CRUD only users, and an admin would be able to CRUD all records and users." It's slightly ambiguous as to whether a manager can CRUD another manager or not, but for the purpose of this project I have assumed they can't.

1. Once a user has logged in, should access to the login page be blocked? While it makes sense from a UX perspective, here I decided to override the current session and log the new user in, in case a session was already active when a request was sent to `/login`, just for convenience.

1. Should a user be allowed to delete their own account? For the purposes of this project, I assumed all users and managers (but not the super user with username 'admin') can delete their own accounts.

## Citations and References
Here is a (non-exhaustive) list of online resources I referred to while working on this project.

- REST API Best Practices: REST Endpoint Design Examples - [https://www.freecodecamp.org/news/rest-api-best-practices-rest-endpoint-design-examples/](https://www.freecodecamp.org/news/rest-api-best-practices-rest-endpoint-design-examples/)
- Flask Documentation (v2.3.x) - [https://flask.palletsprojects.com/en/2.3.x/](https://flask.palletsprojects.com/en/2.3.x/)
- SQLAlchemy 2.0 Documentation - [https://docs.sqlalchemy.org/en/20/](https://docs.sqlalchemy.org/en/20/)
- Role-based Access Control (RBAC) in REST APIs - [https://medium.com/@BastianRob/rbac-in-rest-api-b6ed65d1f4d8](https://medium.com/@BastianRob/rbac-in-rest-api-b6ed65d1f4d8)
