import json
import yaml

"""
Example schema of a Question's attributes

    {
        "acRate": 53.28040678700701,
        "difficulty": "Easy",
        "freqBar": 42.03560515655977,
        "frontendQuestionId": "1",
        "isFavor": false,
        "paidOnly": false,
        "status": "ac",
        "title": "Two Sum",
        "titleSlug": "two-sum",
        "topicTags": [
            {
                "name": "Array",
                "id": "VG9waWNUYWdOb2RlOjU=",
                "slug": "ar ray"
            },
            {
                "name": "Hash Table",
                "id": "VG9waWNUYWdOb2RlOjY=",
                "slug": "hash-table"
            }
        ],
        "hasSolution": true,
        "hasVideoSolution": true
    }
"""

class Question:

    def __init__(self, qAttributes):
        for qAttr, attrVal in qAttributes.items():
            if qAttr == 'frontendQuestionId':
                attrVal = int(attrVal)

            if qAttr == 'freqBar' and attrVal is None:
                attrVal = 0

            setattr(self, qAttr, attrVal)

        self.url = f"https://leetcode.com/problems/{self.titleSlug}/description"
        self.solved = False
        self.skipped = False
        self.skipReason = None
        self.topicsMatch = False

        self.defineTopicsSet()

    def defineTopicsSet(self):
        self.topics = set()
        if hasattr(self, 'topicTags'):
            for topicTag in self.topicTags:
                self.topics.add(topicTag['name'])

    def markSolved(self):
        # print(f"Question {self.frontendQuestionId} ({self.title}) has{' already ' if self.solved else ' '}been marked as solved.")
        self.solved = True
        self.skipped = False
        self.skipReason = None

    def markSkipped(self, skipReason):
        # print(f"Question {self.frontendQuestionId} ({self.title}) has{' already ' if self.skipped else ' '}been marked as skipped.")
        self.skipped = True
        self.skipReason = skipReason

    def printQuestion(self):
        print(f"{self.frontendQuestionId}. \t ({self.difficulty}) ({self.freqBar:.2f}%) \t {self.title} {self.url}")




class QuestionsManager:

    def __init__(self):
        self.questionsMap = {}
        self.solveProgressFileName = "solveProgress.yaml"
        self.loadSolveProgress()

    def getQuestion(self, questionID):
        return self.questionsMap.get(questionID, None)

    def getQuestionsByAttributes(self, difficulty=None, solved=None, skipped=False, topicsMatch=True):
        """
        Retrieves questions by filtering based on provided attributes.

        :param difficulty: A set of difficulties to include (e.g., {'Easy', 'Medium'}). Default behavior is to include all difficulties.
        :param solved: Whether to include only solved questions. Default behavior is to include regardless of Solved status.
        :param skipped: Whether to include skipped questions. Default behavior is to exclude skipped questions.
        :param topicsMatch: Whether to include only questions with topics of interest. Default behavior is do so.

        :return: A set of filtered questions.
        """

        filtered_set = set()
        for question in self.questionsMap.values():
            if difficulty is not None and question.difficulty not in difficulty:
                continue

            if solved is not None and question.solved != solved:
                continue

            if skipped is not None and question.skipped != skipped:
                continue

            if topicsMatch is not None and question.topicsMatch != topicsMatch:
                continue

            filtered_set.add(question)

        return filtered_set

    def addQuestions(self, inputQuestions):
        "accepts input as list of Question objects"
        if isinstance(inputQuestions, list):
            for q in inputQuestions:
                question = Question(q)
                self.questionsMap[question.frontendQuestionId] = question
        else:
            raise TypeError("addQuestions() expects input of type list.")

    @property
    def topicCounts(self):
        topicCounts = {}
        for question in self.questionsMap.values():
            for topic in question.topics:
                topicCounts[topic] = topicCounts.get(topic, 0) + 1

        return topicCounts

    def setTopicsMatchByInterestedTopics(self, interestedTopics):
        for question in self.questionsMap.values():
            question.topicsMatch = len(question.topics - interestedTopics) == 0

    @property
    def topicsMatchQuestions(self):
        return self.getQuestionsByAttributes(topicsMatch=True)

    @property
    def numTopicsMatchQuestions(self):
        return len(self.topicsMatchQuestions)

    @property
    def skippedQuestions(self):
        return self.getQuestionsByAttributes(skipped=True)

    @property
    def numSkippedQuestions(self):
        return len(self.getQuestionsByAttributes(skipped=True))

    @property
    def unsolvedQuestions(self):
        return self.getQuestionsByAttributes(solved=False)

    @property
    def numUnsolvedQuestions(self):
        return len(self.unsolvedQuestions)

    def loadSolveProgress(self):
        try:
            with open(self.solveProgressFileName, "r") as f:
                self.solveProgress = yaml.load(f, Loader=yaml.SafeLoader)
        except FileNotFoundError:
            print("Progress file not found, initializing with empty state.")
            self.solveProgress = {'solvedQuestions': [], 'skippedQuestions': {}}
            self.saveSolveProgress()

        for questionID in self.solveProgress['solvedQuestions']:
            self.markQuestionAsSolved(questionID)

        for skipReason, questionIDs in self.solveProgress['skippedQuestions'].items():
            for questionID in questionIDs:
                self.markQuestionAsSkipped(questionID, skipReason)

    def saveSolveProgress(self):
        with open(self.solveProgressFileName, "w") as f:
            yaml.dump(self.solveProgress, f, default_flow_style=False, indent=4)

    def markQuestionAsSolved(self, questionID=None):
        """
        sets the solved attribute of Question class instance as True.

        :param questionID: int representation of questionID
        """

        question = self.getQuestion(questionID)
        if question:
            question.markSolved()
            self.solveProgress['solvedQuestions'].append(questionID)
            self.solveProgress['solvedQuestions'] = list(set(self.solveProgress['solvedQuestions']))
            self.saveSolveProgress()

    def markQuestionAsSkipped(self, questionID=None, skipReason='skipReasonNotProvided'):
        """
        used to set the skipped and skipReason attributes of Question class.

        :param questionID: int representation of questionID
        :param skipReason: string
        """

        question = self.getQuestion(questionID)
        if question:
            question.markSkipped(skipReason)
            self.solveProgress['skippedQuestions'].setdefault(skipReason, [])
            self.solveProgress['skippedQuestions'][skipReason].append(questionID)
            self.solveProgress['skippedQuestions'][skipReason] = list(set(self.solveProgress['skippedQuestions'][skipReason]))
            self.saveSolveProgress()

    @property
    def numEasyQuestionsSolved(self):
        return len(self.getQuestionsByAttributes(difficulty='Easy', solved=True))

    @property
    def numMediumQuestionsSolved(self):
        return len(self.getQuestionsByAttributes(difficulty='Medium', solved=True))

    @property
    def numHardQuestionsSolved(self):
        return len(self.getQuestionsByAttributes(difficulty='Hard', solved=True))

    @property
    def numEasyQuestions(self):
        return len(self.getQuestionsByAttributes(difficulty='Easy'))

    @property
    def numMediumQuestions(self):
        return len(self.getQuestionsByAttributes(difficulty='Medium'))

    @property
    def numHardQuestions(self):
        return len(self.getQuestionsByAttributes(difficulty='Hard'))

    @property
    def numQuestionsSolved(self):
        return len(self.getQuestionsByAttributes(solved=True))

    @property
    def numQuestionsToBeSolved(self):
        return len(self.getQuestionsByAttributes())

    @property
    def numAllQuestions(self):
        return len(self.questionsMap)

    def printSolveStats(self):
        solvedStats = {
            'easy': (self.numEasyQuestionsSolved, self.numEasyQuestions),
            'medium': (self.numMediumQuestionsSolved, self.numMediumQuestions),
            'hard': (self.numHardQuestionsSolved, self.numHardQuestions),
            'total': (self.numQuestionsSolved, self.numQuestionsToBeSolved)
        }

        try:
            for difficulty, numQuestions in solvedStats.items():
                print(f"{numQuestions[0]}/{numQuestions[1]} ({100*numQuestions[0]/numQuestions[1]:.2f}%) {difficulty} questions solved.")
        except ZeroDivisionError:
            print(f"No questions were found. This can happen if your session token is invalid. Use cached questions or provide a valid token.")

    def getNextQuestions(self, numQuestions):
        """
        :param numQuestions: number of questions to return
        :return: numQuestions unsolved Question objects are returned; sorted by increasing order of difficulty and decreasing frequency
        """
        difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2}
        nextQuestion = sorted(self.getQuestionsByAttributes(solved=False), key=lambda q:(difficulty_order[q.difficulty], -q.freqBar if q.freqBar else 0))[0: numQuestions]

        return nextQuestion