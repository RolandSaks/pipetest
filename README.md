# pipetest

1. Health endpoint http://localhost:8088/health
2. As GitHub API has limit for unauthorized requests. while configuring app it should be considered that amout of queried users * 60 / querying interval should not be more than 60, otherwise requests will start to fail 