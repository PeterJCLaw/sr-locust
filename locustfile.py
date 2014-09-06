from locust import HttpLocust, TaskSet
import uuid
import random
import json
import os

from localconfig import hostname, username, password

def index(l):
    l.client.get("/")
    l.client.get("/css/main.css")
    l.client.get("/css/home.css")
    l.client.get("/images/template/website_logo.png")
    l.client.get("/images/template/magnifier.png")
    l.client.get("/images/template/srobo_website_robot.png")

def ide_login(l):
    l.client.get("/ide/", verify=False)
    auth_json = json.dumps({"username":username, "password":password})
    with l.client.post("/ide/control.php/auth/authenticate", auth_json, catch_response=True, verify=False) as response:
        if "tester" not in response.content and "you are already authenticated" not in response.content:
            print response.content
            response.failure("Bad login response")

def ide_lint(l):
    print l.ide_project
    params = {
      "team"    : l.ide_team,
      "project" : "test-%d" % (l.ide_project,),
      "rev"          : "HEAD",
      "path"         : "robot.py",
      "autosave"     : False,
    }

    params_json = json.dumps(params)

    with l.client.post("/ide/control.php/file/lint", params_json, catch_response=True, verify=False) as response:
        if "errors" not in response.content:
            print response.content
            response.failure(response.content)

        if "failed to exist" in response.content:
            print response.content
            response.failure(response.content)

def ide_change_file_and_checkout(l):
    print l.ide_project
    put_params = {
        "team":l.ide_team,
        "project":"test-%d" % (l.ide_project,),
        "path":"robot.py",
        "data":"import os\nos.system(\"xterm\")\n#################################%s" % (str(uuid.uuid4()),)
    }

    put_json = json.dumps(put_params)

    with l.client.post("/ide/control.php/file/put", put_json, catch_response=True, verify=False) as response:
        if "debug" not in response.content:
            print response.content
            response.failure(response.content)

        if "failed to exist" in response.content:
            print response.content
            response.failure(response.content)


    commit_params = {
        "team":l.ide_team,
        "project":"test-%d" % (l.ide_project,),
        "paths":["robot.py"],
        "message":"Commit message"
    }

    print commit_params

    commit_json = json.dumps(commit_params)

    with l.client.post("/ide/control.php/proj/commit", commit_json, catch_response=True, verify=False) as response:
        if "merges" not in response.content:
            print response.content
            response.failure(response.content)

        if "failed to exist" in response.content:
            print response.content
            response.failure(response.content)

    ide_lint(l)

    co_params = {
        "team":l.ide_team,
        "project":"test-%d" % (l.ide_project,),
        "rev":"HEAD"
    }

    co_json = json.dumps(co_params)

    with l.client.post("/ide/control.php/proj/co", co_json, catch_response=True, verify=False) as response:
        if "url" not in response.content:
            print response.content
            response.failure(response.content)

        if "failed to exist" in response.content:
            print response.content
            response.failure(response.content)


def comp_api_poll(l):
    l.client.get("/comp-api/matches/B?numbers=previous%2Ccurrent%2Cnext%2Cnext%2B1", verify=False)
    l.client.get("/comp-api/matches/A?numbers=previous%2Ccurrent%2Cnext%2Cnext%2B1", verify=False)


def teams_data(l):
    l.client.get("/teams-data.php", verify=False)

class UserBehavior(TaskSet):
    tasks = {
            ide_change_file_and_checkout:7,
            comp_api_poll:74,
            teams_data:8,
            }

    def on_start(self):
        ide_login(self)
        self.ide_team = "SRZ"
        self.ide_project = random.randint(0,99)
        print self.ide_project

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    host = "https://" + hostname
    min_wait=5000
    max_wait=9000

