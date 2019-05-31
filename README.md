# Password as a Service

## Usage

The idea of this challenge is to create a minimal HTTP service that exposes the user and group information on
a UNIX-like system that is usually locked away in the UNIX /etc/passwd and /etc/group files.

```json
{
    "data": "Could be a list of objects or objects themselves"
}
```

The data field will now be described in each of the http request's response

#### Resource 1: User

### List all Users

**Definition**

`GET /users`

**Response**

- `200 OK` on success

```json
[
    {
        “name”: “root”,
        “uid”: 0,
        “gid”: 0,
        “comment”: “root”,
        “home”: “/root”,
        “shell”: “/bin/bash”
    },
    {
        “name”: “dwoodlins”,
        “uid”: 1001,
        “gid”: 1001,
        “comment”: “”,
        “home”: “/home/dwoodlins”,
        “shell”: “/bin/false”
    }
]
```

### Get users matching one or more conditions

**Definition**

`GET /users/query[?name=<nq>][&uid=<uq>][&gid=<gq>][&comment=<cq>][&home=<hq>][&shell=<sq>]`

**Response**

- `200 OK` on success

```json
[
    {
        “name”: “dwoodlins”,
        “uid”: 1001,
        “gid”: 1001,
        “comment”: “”,
        “home”: “/home/dwoodlins”,
        “shell”: “/bin/false”
    }
]
```

### Get user with a particular UUID

**Definition**

`GET /users/<uid>`

**Response**

- `200 OK` on success
- `400 NOT FOUND` on failure

```json
{
        “name”: “root”,
        “uid”: 0,
        “gid”: 0,
        “comment”: “root”,
        “home”: “/root”,
        “shell”: “/bin/bash”
}
```
### Return all groups for a particular user

**Definition**

`GET /users/<uid>/groups`

**Response**

- `200 OK` on success

```json
[
    {
        “name”: “docker”,
        “gid”: 1002,
        “members”: [“dwoodlins”]
    }
]
```

#### Resource 2: Group

### List all Groups

**Definition**

`GET /groups`

**Response**

- `200 OK` on success

```json
[
    {
        “name”: “_analyticsusers”,
        “gid”: 250,
        “members”: [“_analyticsd’,”_networkd”,”_timed”]
    },
    {
        “name”: “docker”,
        “gid”: 1002,
        “members”: []
    }
]
```
### Get groups matching one or more conditions

**Definition**

`GET /groups/query[?name=<nq>][&gid=<gq>][&member=<mq1>[&member=<mq2>][&...]]`

**Response**

- `200 OK` on success

```json
[
    {
        “name”: “_analyticsusers”,
        “gid”: 250,
        “members”: [“_analyticsd’,”_networkd”,”_timed”]
    }
]
```
### Get a group with a particular GID

**Definition**

`GET /groups/<gid>`

**Response**

- `200 OK` on success
- `400 NOT FOUND` on failure

```json
{
        “name”: “docker”,
        “gid”: 1002,
        "members": ["dwoodlins"]
}
```