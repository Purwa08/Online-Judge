from django.db import models

# Create your models here.
# judgeapp/models.py

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    # Additional fields as needed

class Problem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=50)
    # Additional fields as needed

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # Other fields as per your requirements

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()
    # Other fields as per your requirements

class Result(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    actual_output = models.TextField()
    is_passed = models.BooleanField()
    # Other fields as per your requirements


