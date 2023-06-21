from django.shortcuts import render

# Create your views here.

#Register and login views incomplete
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




#Problem list page mostly correct and done

# judgeapp/views.py

from django.shortcuts import render
from .models import Problem

def problem_list(request):
    # Retrieve all problems from the database
    problems = Problem.objects.all()

    return render(request, 'problem_list.html', {'problems': problems})





#problem detail and submit need to see in deep

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

from django.shortcuts import render, redirect

#def problem_detail(request, problem_id):
#    # Retrieve the problem with the specified ID or return a 404 error
#    problem = get_object_or_404(Problem, id=problem_id)
#
#    if request.method == 'POST':
#        code = request.POST['code']
#
#        # Save the code submission to the session
#        request.session['code_submission'] = code
#
#        # Redirect to the submit code page
#        return redirect('submit_code', problem_id=problem_id)
#
#    return render(request, 'problem_detail.html', {'problem': problem})




#this is better one...i.e new code
from django.shortcuts import render, redirect

def problem_detail(request, problem_id):
    # Retrieve the problem with the specified ID or return a 404 error
    problem = get_object_or_404(Problem, id=problem_id)

    if request.method == 'POST':
        code = request.POST['code']

        # Redirect to the submit code page with the code as a URL parameter
        return redirect('submit_code', problem_id=problem_id, code=code)

    return render(request, 'problem_detail.html', {'problem': problem})

import subprocess

def submit_code(request, problem_id, code):
    # Retrieve the problem with the specified ID or return a 404 error
    problem = get_object_or_404(Problem, id=problem_id)

    if request.method == 'POST':
        # Save the code submission to the database
        submission = Submission(problem=problem, code=code)
        submission.save()

        # Get the test cases for the problem from the database
        test_cases = TestCase.objects.filter(problem=problem)

        # Evaluate the submission code using a local compiler
        compiler_result = subprocess.run(['python', '-c', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Compare the compiler output with the expected test case outputs
        verdict = 'Passed'  # Assume the submission passes initially
        for test_case in test_cases:
            expected_output = test_case.output.strip()
            if compiler_result.stdout.strip() != expected_output:
                verdict = 'Failed'
                break

        # Save the verdict for the submission in the database
        submission.verdict = verdict
        submission.save()

        # Redirect to the leaderboard page or any other relevant page
        return redirect('leaderboard')

    return render(request, 'submit_code.html', {'problem': problem})






#earlier chatgpt code
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


from django.shortcuts import render, redirect, get_object_or_404
from .models import Problem, Submission, TestCase

def submit_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    
    if request.method == 'POST':
        code = request.POST['code']

        # Get test cases for the problem from the database
        test_cases = TestCase.objects.filter(problem=problem)

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






#leaderboard page

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
