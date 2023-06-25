from django.db import models

# Create your models here.
# judgeapp/models.py

###############################################################################################################################

class User(models.Model):
    first_name = models.CharField(max_length=50,default="")
    last_name = models.CharField(max_length=50,default="")
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    num_problems_solved = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    # Additional fields as needed

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return self.username

###############################################################################################################################

class Problem(models.Model):
    TOUGHNESS = (("Easy", "Easy"), ("Medium", "Medium"), ("Tough", "Tough"))
    #problemid=models.CharField(("ID"), max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=50,choices=TOUGHNESS)
    # Additional fields as needed

    def __str__(self):
        return self.title
    
###############################################################################################################################

class Submission(models.Model):
    LANGUAGES = (("C++", "C++"), ("C", "C"), ("Python3", "Python3"), ("Python2", "Python2"), ("Java", "Java"))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    verdict=models.CharField(max_length=50,default="")
    runtime = models.IntegerField(default=0)
    language = models.CharField( 
        max_length=10, choices=LANGUAGES, default="C++")
    # Other fields as per your requirements

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return str(self.timestamp) + " : @" + str(self.user) + " : " + self.problem.title + " : " + self.verdict + " : " + self.language

###############################################################################################################################

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()
    # Other fields as per your requirements

    def __str__(self):
        return ("TC: " + str(self.id) + " for Problem: " + str(self.problem))

###############################################################################################################################

class Result(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    actual_output = models.TextField()
    is_passed = models.BooleanField()
    # Other fields as per your requirements

###############################################################################################################################
