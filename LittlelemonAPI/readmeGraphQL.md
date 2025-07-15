## Python Graphene Testing

I use [Python Graphene](https://docs.graphene-python.org) to convert my Django models to GraphQL Schema Objects. See the `schema.py` file for details.

#### Notes

While this works, I've [tested](https://docs.graphene-python.org/projects/django/en/latest/debug/) and found that reducing fields and making GraphQL requests doesn't reduce the query with the database and the app server. For example, this graphQL query:

```
{
  orders {
    id
    status
    total
    date
    deliveryCrew {
      id
      username
      firstName
      lastName
      email
    }
	}
  _debug {
    sql {
      rawSql
    }
  }
}
```

Results in a SQL statement like this (tested sqlite):

```
SELECT
  LittlelemonAPI_order.id,
  LittlelemonAPI_order.user_id,
  LittlelemonAPI_order.delivery_crew_id,
  LittlelemonAPI_order.status,
  LittlelemonAPI_order.total,
  LittlelemonAPI_order.date,

  auth_user.id,
  auth_user.password,
  auth_user.last_login,
  auth_user.is_superuser,
  auth_user.username,
  auth_user.first_name,
  auth_user.last_name,
  auth_user.email,
  auth_user.is_staff,
  auth_user.is_active,
  auth_user.date_joined,

  T3.id,
  T3.password,
  T3.last_login,
  T3.is_superuser,
  T3.username,
  T3.first_name,
  T3.last_name,
  T3.email,
  T3.is_staff,
  T3.is_active,
  T3.date_joined

FROM LittlelemonAPI_order
INNER JOIN auth_user
  ON LittlelemonAPI_order.user_id = auth_user.id
LEFT OUTER JOIN auth_user AS T3
  ON LittlelemonAPI_order.delivery_crew_id = T3.id;

```

Note all fields from both the User and Order tables are fetched?
