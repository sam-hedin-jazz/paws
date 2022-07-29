import json
import subprocess
import pprint



def trim_json(coll, valid_keys, coll_key=None):
  """
  Return a trimmed version of coll which only preserves branches with keys in valid_keys

  coll - A collection representing some JSON that has been read into python. coll should be either a dictionary or a list.
  valid_keys - A list of string, representing JSON keys. Will search the JSON for occurrances of any valid keys and preserve those branches.
  coll_key - The key corresponding to this collection in the JSON. Not relevent for items in an array, or the root item

  The recursive algorithm looks more or less like:
  For each key-value pair in coll, if [key in valid_keys]:
    * If value is a string, preserve this key-value pair
    * If value is a collection, preserve this key-value pair AND each key-value in the collection's immediate children where value is a string
  """
  if type(coll) == dict:
    trimmed = {}
    for key,val in coll.items():
      # Include string if its key is valid. If this dict's key is valid, include EVERY one of its strings
      if type(key) == str and (coll_key in valid_keys or key in valid_keys):
        trimmed[key] = val
      elif type(val) == dict or type(val) == list:
        val_trimmed = trim_json(val, valid_keys, coll_key=key)
        if val_trimmed is not None:
          trimmed[key] = val_trimmed

  elif type(coll) == list:
    trimmed = []
    for item in coll:
      if type(item) == str and (coll_key in valid_keys or item in valid_keys):
        trimmed.append(item)
      elif type(item) == dict or type(item) == list:
        item_trimmed = trim_json(item, valid_keys)
        if item_trimmed is not None:
          trimmed.append(item_trimmed)

  else:
    print(type(coll))
    raise TypeError("trim_json: Passed invalid type")

  if len(trimmed) > 0:
    return trimmed
  else:
    return None


def query(q):
  return AwsResponse(q.split(" "))

pp_instance = pprint.PrettyPrinter(indent=3)
def pp(*args, **kwargs):
  return pp_instance.pprint(*args, **kwargs)


def list_tags(j):
  """
  Given a JSON collection, return a list of all string keys used.
  """
  tags = set()
  if type(j) == dict:
    for k,v in j.items():
      if type(v) == str:
        tags.add(k)
      else:
        tags |= list_tags(v)
  elif type(j) == list:
    for item in j:
        tags |= list_tags(item)
  return tags


class AwsResponse:
  def __init__(self, request):
    self.sent_request = False
    self.request_succeeded = None
    self._request = request
    self._json = None
    self._resp = None

  def send_request(self):
    print("Sending request...")
    sp = subprocess.run(self._request, capture_output=True)
    self.sent_request = True
    if sp.returncode != 0:
      self.request_succeeded = False
      self._resp = ""
      self._json = ""
    else:
      self.request_succeeded = True
      self._resp = sp.stdout
      self._json = json.loads(self._resp.decode("utf-8"))


  def assertResp(self):
    if not self.sent_request:
      self.send_request()
    if not self.request_succeeded:
      # Note: Could mmamke custom exception class here
      raise Exception("Failed to make query")

  # Format JSON, You can pass the result to print(...)
  def f(self, j):
    return json.dumps(j, indent=2, sort_keys=True)


  @property
  def json(self):
    self.assertResp()
    return self._json

  @property
  def resp(self):
    self.assertResp()
    return self._resp

  
  @property
  def fjson(self):
    return self.f(self.json)

  def trim(self, valid_keys):
    return trim_json(self.json, valid_keys)
  def ftrim(self, valid_keys):
    return self.f(self.trim(valid_keys))




print("==== Welcome to SAWS ====")
#TODO: examples, help command/function
print(
"""\
This module provides the class AwsResponse which acts as a wrapper around the response. The "trim" method will trim down branches, per the trim_json function

Existing queries:
  * ec2_w1, ec2_w2, ec2_e1, ec2_e2  - These all correspond to describe-instanecs in the different regions

Functions:
  * query("aws ...") - Return an AwsResponse from the given query
  * pp(json)  - pretty-print the JSON
""")


ec2_w1 = AwsResponse(["aws", "--region", "us-west-1", "ec2", "describe-instances"])
ec2_w2 = AwsResponse(["aws", "--region", "us-west-2", "ec2", "describe-instances"])
ec2_e1 = AwsResponse(["aws", "--region", "us-east-1", "ec2", "describe-instances"])
ec2_e2 = AwsResponse(["aws", "--region", "us-east-2", "ec2", "describe-instances"])
