from django.shortcuts import render

# Create your views here.
# judgeapp/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .forms import RegistrationForm
from .models import User

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Create a new User instance
            user = User(username=username, email=email, password=make_password(password))

            # Save the user to the database
            user.save()

            # Redirect to a success page or login page
            return redirect('success')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

# judgeapp/views.py

from django.shortcuts import render
from .models import Problem

def problem_list(request):
    # Retrieve all problems from the database
    problems = Problem.objects.all()

    return render(request, 'problem_list.html', {'problems': problems})

# judgeapp/views.py

from django.shortcuts import render, get_object_or_404
from .models import Problem

#def problem_detail(request, problem_id):
#    # Retrieve the problem with the specified ID or return a 404 error
#    problem = get_object_or_404(Problem, id=problem_id)
#
#    return render(request, 'problem_detail.html', {'problem': problem})

# views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Problem, Submission

def problem_detail(request, problem_id):
    # Retrieve the problem with the specified ID or return a 404 error
    problem = get_object_or_404(Problem, id=problem_id)

    if request.method == 'POST':
        code = request.POST['code']

        # Save the code submission to the database
        submission = Submission(problem=problem, code=code)
        submission.save()

        # Redirect to a success page or another relevant view
        return redirect('success')

    return render(request, 'problem_detail.html', {'problem': problem})


import subprocess

from django.shortcuts import render, redirect, get_object_or_404
from .models import Problem, Submission, Testcase

def submit_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    
    if request.method == 'POST':
        code = request.POST['code']

        # Get test cases for the problem from the database
        test_cases = Testcase.objects.filter(problem=problem)

        # Compile and evaluate the submission code
        compiler_output = subprocess.run(['python', '-c', code], capture_output=True, text=True)
        submission_output = compiler_output.stdout.strip()

        # Compare the outputs with test cases and save the verdict
        verdict = True
        for test_case in test_cases:
            if test_case.output.strip() != submission_output:
                verdict = False
                break

        # Save the submission and verdict in the database
        submission = Submission(user=request.user, problem=problem, code=code, verdict=verdict)
        submission.save()

        # Redirect to the leaderboard page
        return redirect('leaderboard')

    return render(request, 'problem_detail.html', {'problem': problem})

# judgeapp/views.py

from django.shortcuts import render
from .models import Submission

def leaderboard(request):
    # Retrieve the last 10 submissions from the database
    submissions = Submission.objects.order_by('-id')[:10]

    return render(request, 'leaderboard.html', {'submissions': submissions})

# views.py

from django.shortcuts import render

def success(request):
    return render(request, 'success.html')
