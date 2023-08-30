from coffeescraper.utils import get_env,get_secret,get_secret_file

import pathlib
import os

envvar = "TESTENVVAR"
novar = "THISENVIRONMENTVARDOESNOTEXIST"
secret = "verysecret"
text = f"{secret}\nadditional text that should be ignored\n\n"

class TestUtils:
    def test_get_env(self):
        os.environ[envvar] = "oink"
        assert get_env(envvar) == "oink"

    def test_get_env_empty(self):    
        os.environ[envvar] = ""
        assert get_env(envvar) is None
        assert get_env(envvar,"oink oink") == "oink oink"
        assert get_env(novar) is None
        assert get_env(novar,"oink oink") == "oink oink"
    
    def test_get_env_list(self):
        os.environ[envvar] = "oink,gnerk ,groink"  # trailing space on purpose, should be trimmed by get_env()
        envlist = get_env(envvar)
        assert type(envlist) is list
        assert len(envlist) == 3
        assert all(a == b for a,b in zip(["oink","gnerk","groink"],envlist))
    
    def test_get_secret(self):
        p = pathlib.Path('/tmp/testsecret')
        with open(p,"w") as file:
            file.write(text)
        assert get_secret(p) == secret
        p.unlink()
        assert get_secret(p) is None
                
    def test_get_secret_file(self):
        p = pathlib.Path('/tmp/testsecret')
        with open(p,"w") as file:
            file.write(text)
        assert get_secret_file(p) == text
        p.unlink()
        assert get_secret_file(p) is None