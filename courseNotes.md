1. 5 Http verbs:
   GET, POST,
   PUT (updates whole resource),
   PATCH (updates partially resource),
   DELETE (delete reource)
   KISS - each API should do 1 thing
   Requests include:

- HTTP Version type 1.1 or 2
- url
- method, headers,
  body?

1xx informational msgs
2xx successful responses
3xx redirection info
4xx client error responses
5xx server error codes

401 (unauthorized) you didn't provide credentials

vs 403 (forbidden) - I know who you are but you're not authorized for this particular thing

REST architecture is always stateless and should be cacheable.

REST APIs are all about layering of architecture. A cache is a layer that can be added/remove each time.
A firewall load balancer, a web server and a database.

Uniform Resource Identifier. The part after the domain for the API path.
use lowercase and hyphens are good. camel case for variables (/orders/{orderId})
/customer/{customerId}/orders/

getAllBooks/ thats a bad endpoint!
Never add a trailing slash at the end of the endpoint sports/basketball/teams/ <-- bad!!!
hierarchical relationships w. forward slash
query parameters for data types
nouns for resource names

### API Security

SSL Secure Socket Layer - Encyrpt data sent from server via SSL certificates
Signed Urls - Give client app limited access to specific resource for brief period of time (send a token or something), HMAC is a system of signing via a cryptography technique.

Token-based authentication- user gets it from signin and can send it with all other requests. JWT.
CORS - Cross origin resource sharing. You only accept requests from certain domains.

from django.Forms.models import model_to_dict
from django.http import JsonResponse
from django.http import QueryDict <-- parses raw json from client to object (python dictionary)

Seperate resource folders for each of the apps

- split settings into relevant files
- place business logic in models, not views

The meta course advocates a development pattern wherein API developers stand up mock API endpoints to represent 'under-construction' endpoints and show what data back will look like.

The course recommends https://www.mockaroo.com/ for mocking the back-end API and testing. mockaroo allows you to generate fake data.
The tool mockapi.io allows you to create mock API endpoints for free, accessible via mockapi.io/

Stuff that DRF provides that is handy:

- handy status code lookups
- serializers for converting between models and from non-ORM data. Basically python native data types can be converted to JSON/XML. Serializers
  also do deserialization, which validates and converts requested data back into existing python models.
- DRF makes it easy to integrate authentication systems

For creating new API models, views and serializers there are several ways.
We want to start with easiest (most generic) then move down to harder and more specific approaches as we need.

Easiest:

1. view as viewsets.ModelViewSet or ReadOnlyModelViewSet. Add special
   methods via @action decorated function like set_password
2. urls as DefaultRouter registering what we need
3. serializers as serializers.ModelSerializer
4. models as class models.model

A bit more Custom:

1. view as generics (RetrieveUpdateAPIView, DestroyAPIView). Handle seperate actions
2. view as APIView. you can set your own authorization, permission classes. You handle each http method (def get, def post) etc.

View Type Code Control Router Needed? Use When…
ModelViewSet 🟢 Low 🔴 Low ✅ Yes Full CRUD, minimal setup
Generic + Mixins 🟡 Med 🟡 Med ❌ No Partial CRUD, flexible
ListCreateAPIView 🟢 Low 🟡 Med ❌ No Common cases, simple syntax
APIView 🔴 High 🟢 High ❌ No Custom logic or non-standard APIs
@api_view (FBVs) 🟢 Low 🟡 Med ❌ No Small, quick APIs
