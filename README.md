# Boilerplate REST Server in Flask


## Quickstart
1. `git clone git@github.com:kvnn/flask-rest-starter.git`
2. `cd flask-rest-starter`
3. `python3 -m venv venv`
4. `source venv/bin/activate`
5. `pip3 install -r requirements.txt`
6. `python3 -m unittest discover -s tests -p 'test_*.py'`


# Running the server, playing around
1. `flask run --debug --host=0.0.0.0 --port 3000`
2. Register
```
curl --location --request POST '0.0.0.0:3000/api/v1/auth/register/' \
--header 'Content-Type: application/json' \
--data-raw '{
            "email": "john@example.com",
            "password": "catcat!",
            "password2": "catcat!"
        }'
```
3. Login
```
curl --location --request POST '0.0.0.0:3000/api/v1/auth/login/' \
--header 'Content-Type: application/json' \
--data-raw '{
            "email": "john@example.com",
            "password": "catcat!"
}'
```
4. Create a Tweet ( YOU NEED THE "token" value from the previous response)
```
curl --location --request POST '0.0.0.0:3000/api/v1/tweet/' \
--header 'Authorization: Bearer {TOKEN_VALUE}' \
--header 'Content-Type: application/json' \
--data-raw '{
            "body": "This is my tweet"
        }'
```
5. Reply to Tweet #1
```
curl --location --request POST '0.0.0.0:3000/api/v1/tweet/' \
--header 'Authorization: Bearer {TOKEN_VALUE}' \
--header 'Content-Type: application/json' \
--data-raw '{
            "body": "This is my tweet",
            "parent_id": 1
        }'
```
6. Like Tweet #1
```
curl --location --request GET '0.0.0.0:3000/api/v1/tweets/'
```
