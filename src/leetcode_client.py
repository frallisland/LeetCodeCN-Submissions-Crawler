import time
import requests
import json

class LeetcodeClient:
    LOGIN_PATH = 'accounts/login/'
    GRAPHQL_PATH = 'graphql/'

    def __init__(
            self,
            login_id,
            password,
            sleep_time=5,
            base_url='https://leetcode.cn/',
            logger=None) -> None:
        self.login_id = login_id
        self.password = password
        self.sleep_time = sleep_time
        self.endpoint = base_url
        self.logger = logger
        self.client = requests.session()
        self.client.encoding = "utf-8"

        self.headers = {
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'
        }

    def login(self) -> None:
        ATTEMPT = 3
        for try_cnt in range(ATTEMPT):
            login_url = self.endpoint + self.LOGIN_PATH
            self.client.get(login_url)
            login_data = {
                'login': self.login_id,
                'password': self.password
            }
            result = self.client.post(
                login_url, data=login_data, headers={
                    'Referer': login_url})

            # result.url 判断是否真正登录成功
            if result.ok and result.url == self.endpoint:
                self.logger.info("Login successfully!")
                return
            self.logger.warning("Login failed, Wait till next round!")
            if try_cnt != ATTEMPT - 1:
                time.sleep(self.sleep_time)

        self.logger.error(
            "LoginError: Login failed, ensure your username and password is correct!"
        )

        raise Exception(
            "LoginError: Login failed, ensure your username and password is correct!")

    def downloadCode(self, submission) -> str:
        with open('query/query_download_submission', 'r') as f:
            query_string = f.read()

        data = {
            'query': query_string,
            'operationName': "mySubmissionDetail",
            "variables": {
                "id": submission["id"]
            }
        }

        response = self.client.post(
            self.endpoint +
            self.GRAPHQL_PATH,
            json=data,
            headers=self.headers)
        submission_details = response.json()["data"]["submissionDetail"]
        return submission_details

    def getSubmissionList(self, page_num):
            self.logger.info(
                'Now scraping submissions list for page:{page_num}'.format(
                    page_num=page_num
                )
            )
            submissions_url = "https://leetcode.cn/api/submissions/?offset={page_num}&limit=40".format(
                page_num=page_num
            )
            submissions_list = self.client.get(submissions_url)
            return json.loads(submissions_list.text)
