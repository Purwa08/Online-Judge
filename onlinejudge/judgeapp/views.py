###############################################################################################################################

#Registration page for new user

from .models import User 
from django.shortcuts import render, redirect
from .forms import CreateUserForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            if User.objects.filter(email=user_email).exists():
                messages.error(request, 'Email already exists!')
                context = {'form': form}
                return render(request, 'register.html', context)

            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account created successfully for {}'.format(username))
            return redirect('login')
    else:
        form = CreateUserForm()
    
    context = {'form': form}
    return render(request, 'register.html', context)

###############################################################################################################################

#login page

from django.contrib.auth import authenticate, login , logout

def loginpage(request):
    if request.user.is_authenticated:
        return redirect('problem_list')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('problem_list')
            else:
                messages.info(request, 'Username/Password is incorrect')

        context = {}
        return render(request, 'login.html', context)
    

###############################################################################################################################

# To logout a registered user
def logoutPage(request):
    logout(request)
    return redirect('login')

###############################################################################################################################

# To view all the submissions made by current logged-in user

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def allSubmissionPage(request):
    submissions = Submission.objects.filter(user=request.user.id)
    return render(request, 'submission.html', {'submissions': submissions})

###############################################################################################################################

#Problem list page displaying list of all problems on start but login required

from django.shortcuts import render
from .models import Problem,Submission,User
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def problem_list(request):
    # Retrieve all problems from the database
    problems = Problem.objects.all()

    return render(request, 'problem_list.html', {'problems': problems})


###############################################################################################################################

#Problem description page of a particular problem along with text editor on a side and submit button

from django.shortcuts import render,redirect, get_object_or_404
from .forms import CodeForm

@login_required(login_url='login')
def problem_detail(request, problem_id):
    user_id=request.user.id
    problem = get_object_or_404(Problem, id=problem_id)
    user=User.objects.get(id=user_id)
    form = CodeForm()
    context = {'problem': problem, 'user': user, 'user_id': user_id, 'code_form': form}
    return render(request, 'problem_detail.html', context)


###############################################################################################################################

#Page after code submission - verdict page

#@login_required(login_url='login')
#def submit_code(request,problem_id):




###############################################################################################################################

#leaderboard page displaying all users according to their score

# judgeapp/views.py

@login_required(login_url='login')
def leaderboard(request):
    coders = User.objects.all()
    return render(request, 'leaderboard.html', {'coders': coders})
    


###############################################################################################################################







#problem detail and submit need to see in deep

# judgeapp/views.py


#def problem_detail(request, problem_id):
#    # Retrieve the problem with the specified ID or return a 404 error
#    problem = get_object_or_404(Problem, id=problem_id)
#
#    return render(request, 'problem_detail.html', {'problem': problem})

# views.py


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


# def problem_detail(request, problem_id):
#     # Retrieve the problem with the specified ID or return a 404 error
#     problem = get_object_or_404(Problem, id=problem_id)

#     if request.method == 'POST':
#         code = request.POST['code']

#         # Redirect to the submit code page with the code as a URL parameter
#         return redirect('submit_code', problem_id=problem_id, code=code)

#     return render(request, 'problem_detail.html', {'problem': problem})

# import subprocess

# def submit_code(request, problem_id, code):
#     # Retrieve the problem with the specified ID or return a 404 error
#     problem = get_object_or_404(Problem, id=problem_id)

#     if request.method == 'POST':
#         # Save the code submission to the database
#         submission = Submission(problem=problem, code=code)
#         submission.save()

#         # Get the test cases for the problem from the database
#         test_cases = TestCase.objects.filter(problem=problem)

#         # Evaluate the submission code using a local compiler
#         compiler_result = subprocess.run(['python', '-c', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

#         # Compare the compiler output with the expected test case outputs
#         verdict = 'Passed'  # Assume the submission passes initially
#         for test_case in test_cases:
#             expected_output = test_case.output.strip()
#             if compiler_result.stdout.strip() != expected_output:
#                 verdict = 'Failed'
#                 break

#         # Save the verdict for the submission in the database
#         submission.verdict = verdict
#         submission.save()

#         # Redirect to the leaderboard page or any other relevant page
#         return redirect('leaderboard')

#     return render(request, 'submit_code.html', {'problem': problem})






# #earlier chatgpt code
# def problem_detail(request, problem_id):
#     # Retrieve the problem with the specified ID or return a 404 error
#     problem = get_object_or_404(Problem, id=problem_id)

#     if request.method == 'POST':
#         code = request.POST['code']

#         # Save the code submission to the database
#         submission = Submission(problem=problem, code=code)
#         submission.save()

#         # Redirect to a success page or another relevant view
#         return redirect('success')

#     return render(request, 'problem_detail.html', {'problem': problem})


# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Problem, Submission, TestCase

# def submit_code(request, problem_id):
#     problem = get_object_or_404(Problem, id=problem_id)
    
#     if request.method == 'POST':
#         code = request.POST['code']

#         # Get test cases for the problem from the database
#         test_cases = TestCase.objects.filter(problem=problem)

#         # Compile and evaluate the submission code
#         compiler_output = subprocess.run(['python', '-c', code], capture_output=True, text=True)
#         submission_output = compiler_output.stdout.strip()

#         # Compare the outputs with test cases and save the verdict
#         verdict = True
#         for test_case in test_cases:
#             if test_case.output.strip() != submission_output:
#                 verdict = False
#                 break

#         # Save the submission and verdict in the database
#         submission = Submission(user=request.user, problem=problem, code=code, verdict=verdict)
#         submission.save()

#         # Redirect to the leaderboard page
#         return redirect('leaderboard')

#     return render(request, 'problem_detail.html', {'problem': problem})




###############################################################################################################################

#leaderboard page

# judgeapp/views.py

# from django.shortcuts import render
# from .models import Submission

# def leaderboard(request):
#     # Retrieve the last 10 submissions from the database
#     submissions = Submission.objects.order_by('-id')[:10]

#     return render(request, 'leaderboard.html', {'submissions': submissions})

# # views.py

# from django.shortcuts import render

# def success(request):
#     return render(request, 'success.html')
