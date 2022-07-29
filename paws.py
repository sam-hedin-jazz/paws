import json
import subprocess
import pprint



def getTrimmedJson(coll, valid_keys, coll_key=None):
  """
  coll - A collection representing some JSON that has been read into python. coll should be either a dictionary or a list.
  valid_keys - A list of string, representing JSON keys. Will search the JSON for occurrances of any valid keys and preserve those branches.

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
        val_trimmed = getTrimmedJson(val, valid_keys, coll_key=key)
        if val_trimmed is not None:
          trimmed[key] = val_trimmed

  elif type(coll) == list:
    trimmed = []
    for item in coll:
      if type(item) == str and (coll_key in valid_keys or item in valid_keys):
        trimmed.append(item)
      elif type(item) == dict or type(item) == list:
        item_trimmed = getTrimmedJson(item, valid_keys)
        if item_trimmed is not None:
          trimmed.append(item_trimmed)

  else:
    print(type(coll))
    raise TypeError("getTrimmedJson: Passed invalid type")

  if len(trimmed) > 0:
    return trimmed
  else:
    return None


class AwsResponse:
  def __init__(self, request):
    self.sent_request = False
    self.request_succeeded = None
    self._request = request
    self._json = "test"
    self._attributes = ["json", "resp", "j"]

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


  @property
  def json(self):
    self.assertResp()
    return self._json

  @property
  def resp(self):
    self.assertResp()
    return self._resp

  # Nicely formatted JSON
  @property
  def fjson(self):
    return json.dumps(self.json, indent=2, sort_keys=True)

  def trim(self, valid_keys):
    return getTrimmedJson(self.json, valid_keys)
  
  def ftrim(self, validKeys):
    return json.dumps(self.trim(validKeys), indent=2, sort_keys=True)



print("==== Welcome to SAWS ====")
print(
"""\
Here is a summary of what we have queried so far
Here is a message describing what variables exist and stuff
Here is a description of provided functions
""")

pp = pprint.PrettyPrinter(indent=3)


ec2_w1 = AwsResponse(["aws", "--region", "us-west-1", "ec2", "describe-instances"])
ec2_w2 = AwsResponse(["aws", "--region", "us-west-2", "ec2", "describe-instances"])
ec2_e1 = AwsResponse(["aws", "--region", "us-east-1", "ec2", "describe-instances"])
ec2_e2 = AwsResponse(["aws", "--region", "us-east-2", "ec2", "describe-instances"])



