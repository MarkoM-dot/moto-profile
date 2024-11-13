# Moto AWS Profile issues

If you happen to come accross the `botocore.exceptions.ProfileNotFound`
exception with moto here is yet another solution you may use in addition
to simply adding a fake credentials profile for testing. If you cannot
create fake credentials for use for some reason, and there could be a few,
you may choose to monkeypatch environment variables within your code.

Unfortunately, monkeypatching won't work smoothly because as soon as
`moto` is imported a `Session` object is created that looks for your
`AWS_PROFILE` if this environment variable is set to **anything**.

```
# AWS_PROFILE='' will raise
...
botocore.exceptions.ProfileNotFound: The config profile () could not be found

# AWS_PROFILE='example' will raise
...
botocore.exceptions.ProfileNotFound: The config profile (example) could not be found

# AWS_ACCESS_KEY_ID= AWS_SECRET_ACCESS_KEY= AWS_PROFILE= will still raise
botocore.exceptions.ProfileNotFound: The config profile () could not be found
```

## Setup

Install boto3 and moto in a virtual environment.

```sh
pip -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

## Exception on import

```py
# test_import.py
from moto import mock_aws
```

```sh
AWS_PROFILE= python -m unittest test_import.py  # result: ProfileNotFound

AWS_ACCESS_KEY_ID= AWS_SECRET_ACCESS_KEY= AWS_PROFILE= python -m unittest test_import.py  # result: ProfileNotFound
```


## Additional information

In particular, it is the `AccountSpecificBackend` class in `/moto/core/base_backend.py`
that is responsible for this behavior. Because once this module is imported the 
`session` class variable is evaluated and begins looking for your aws profile if
`AWS_PROFILE` exists among your environment variables.

```py
# moto/core/base_backend.py
class AccountSpecificBackend(Dict[str, SERVICE_BACKEND]):
    """
    Dictionary storing the data for a service in a specific account.
    Data access pattern:
      account_specific_backend[region: str] = backend: BaseBackend
    """

    session = Session() # <- this line
    ...
```

## Closing

The solution I provide is in `test_solution.py` whereby the `AWS_PROFILE` env
variable is removed first, and only then is `moto` imported. Below is a snippet
from the file available [here](./test_solution.py).

```py
modified_environ = {
    k: v for k, v in os.environ.items() if k not in "AWS_PROFILE"
}
with mock.patch.dict(os.environ, modified_environ, clear=True):
    mock_aws = import_module("moto").mock_aws
    self.mock_aws = mock_aws()
    self.mock_aws.start()
    self.s3_client = boto3.client("s3")
    self.s3_client.create_bucket(Bucket="Test-Bucket")
```

In my opinion a library used for mocking aws should avoid this undesirable
behavior and the solution should really involve calling this session
in a function and caching it for reuse. But, for the time being I
have a workaround in `test_solution.py`.
