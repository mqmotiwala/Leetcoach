import requests
import json
import os
import yaml

def printDivider(dividerText):
    print(f"\n{dividerText}")
    print(f"{'-'*len(dividerText)}\n")
    
def loadEnv():
    with open(f"{os.getcwd()}/.env", "r") as f:
        envs = f.readlines()
        
    return {envx.strip().split('=')[0]: envx.strip().split('=')[1] for envx in envs}

def getQuestions(companies, scrapeNew):
    fileName = '&'.join(companies)
    if len(fileName) == 0: fileName = 'all'
    fileName = os.getcwd() + '/questions/' + fileName
        
    if scrapeNew:
        env = loadEnv()
        sessionToken = env.get('LEETCODE_SESSION', None)
        
        if sessionToken is None:
            raise ValueError("No session token found. Ensure .env file is configured correctly.")
            
        cookies = {'LEETCODE_SESSION': sessionToken}
        query = """
            query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
              problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
              ) {
                total: totalNum
                questions: data {
                  acRate
                  difficulty
                  freqBar
                  frontendQuestionId: questionFrontendId
                  isFavor
                  paidOnly: isPaidOnly
                  status
                  title
                  titleSlug
                  topicTags {
                    name
                    id
                    slug
                  }
                  hasSolution
                  hasVideoSolution
                }
              }
            }
        """

        json_data = {
            'query': query, 
            'variables': {'categorySlug': 'all-code-essentials', 'skip': 0, 'limit': 10000, 'filters': {'companies': companies}},
        }

        response = requests.post('https://leetcode.com/graphql/', cookies=cookies, json=json_data)
        questions = response.json()['data']['problemsetQuestionList']['questions']

        # write questions to file
        with open(f"{fileName}.json", "w") as f:
            f.write(json.dumps(questions))

    else:
        try:
            with open(f"{fileName}.json", "r") as f:
                questions = json.loads(f.read())
        except FileNotFoundError:
            print(f"{fileName}.json not found in project directory.")
            return None
        
    return questions

def getTopicsOfInterest():
    configFile = os.getcwd() + '/config.yaml'
    with open(configFile, 'r') as f:
        topics = yaml.load(f)
        
    return set(topics['Interested Topics'])
        