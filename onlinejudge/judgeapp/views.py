###############################################################################################################################

#Registration page for new user
from django.contrib.auth import get_user_model

from django.shortcuts import render, redirect
from .forms import CreateUserForm
from django.contrib import messages

def register(request):
    User = get_user_model()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            if User.objects.all().filter(email=user_email).exists():
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

# from django.contrib.auth.decorators import login_required

# @login_required(login_url='login')
# def allSubmissionPage(request):
#     submissions = Submission.objects.filter(user=request.user.id)
#     return render(request, 'submission.html', {'submissions': submissions})

###############################################################################################################################

#Problem list page displaying list of all problems on start but login required

from django.shortcuts import render
from .models import Problem,Submission,User,TestCase
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
    User = get_user_model()
    user_id=request.user.id
    problem = get_object_or_404(Problem, id=problem_id)
    user=User.objects.get(id=user_id)
    form = CodeForm()
    context = {'problem': problem, 'user': user, 'user_id': user_id, 'code_form': form}
    return render(request, 'problem_detail.html', context)


###############################################################################################################################

#Page after code submission - verdict page

import os
import signal
import subprocess
import os.path
import docker
from django.conf import settings
from datetime import datetime
from time import time
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from judgeapp.models import User
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent


@login_required(login_url='login')
def submit_code(request,problem_id):
    User=get_user_model()
    if request.method == 'POST':

        # Configure Docker client
        docker_client = docker.from_env()

        user = get_user_model().objects.get(username=request.user)
        problem = Problem.objects.get(id=problem_id)
        
        #replacing \r\n by \n in original output to compare it with the usercode output
        #testcase.expected_output = testcase.expected_output.replace('\r\n','\n').strip() 
        
        #Debugging
        #print("Input:", testcase.input_data)
        #print("Expected Output:", testcase.expected_output)
        # score of a problem
        if problem.difficulty=="Easy":
            score = 10
        elif problem.difficulty=="Medium":
            score = 30
        else:
            score = 50

        # extract data from form
        form = CodeForm(request.POST)
        user_code = ''
        if form.is_valid():
            user_code = form.cleaned_data.get('user_code')
            print(user_code)
            #user_code = user_code.replace('\r\n','\n').strip()
        else:
            print(form.errors)   

        language = request.POST.get('language')
        submission = Submission(user=user, problem=problem, timestamp=datetime.now(), 
                                language=language, user_code=user_code)
        submission.save()
        print(submission.user)  # Verify user object
        print(submission.problem)  # Verify problem object

        filename = str(submission.id)

        # # User code and file information
        
        # if user code is in C++
        if language == "C++":
            extension = ".cpp"
            cont_name = "my-gcc"
            compile_cmd = f"g++ -o {filename}.exe {filename}.cpp"
            clean = f"{filename}.exe {filename}.cpp"
            docker_img = "gcc:latest"
            exe_cmd = f"./{filename}.exe"
            
        elif language == "C":
            extension = ".c"
            cont_name = "my-gcc"
            compile_cmd = f"gcc -o {filename} {filename}.c"
            clean = f"{filename} {filename}.c"
            docker_img = "gcc:latest"
            exe_cmd = f"./{filename}"

        elif language == "Python3":
            extension = ".py"
            cont_name = "oj-py3"
            compile_cmd = "python3"
            clean = f"{filename}.py"
            docker_img = "python:latest"
            exe_cmd = f"python {filename}.py"

        elif language == "Java":
            filename = "Main"
            extension = ".java"
            cont_name = "oj-java"
            compile_cmd = f"javac {filename}.java"
            clean = f"{filename}.java {filename}.class"
            docker_img = "openjdk:latest"
            exe_cmd = f"java {filename}"

        file = filename + extension

        # Set file paths
        usercode_filepath = os.path.join(BASE_DIR, 'usercodes', file)
        container_filepath = f'/{file}'
        num_passed = 0
        num_failed = 0
        verdict_details = [] 

        # Save user code to file
        with open(usercode_filepath, 'w') as code_file:
            code_file.write(user_code)
    
        # Check if the Docker container is running
        try:
            container = docker_client.containers.get(cont_name)
            container_state = container.attrs['State']
            container_is_running = container_state['Status'] == 'running'
            if not container_is_running:
                container.start()
        except docker.errors.NotFound:
            container = docker_client.containers.run(docker_img, detach=True, name=cont_name)

        # Copy the user code file to the Docker container
        subprocess.run(f'docker cp {usercode_filepath} {cont_name}:{container_filepath}', shell=True)

        # Compile the code inside the Docker container
        compile_result = subprocess.run(f'docker exec {cont_name} {compile_cmd}', capture_output=True, shell=True)
        compile_stdout = compile_result.stdout.decode('utf-8')
        compile_stderr = compile_result.stderr.decode('utf-8')
        execute_stdout=''
        execute_stderr=''

        if compile_result.returncode != 0:
            # Compilation failed
            verdict = 'Compilation Error'
            print('Compilation Output:')
            print(compile_stdout)
            print(compile_stderr)
        else:
            # Compilation successful, execute the code
            verdict = 'Accepted'
            print('Execution Output:')

            # Retrieve test cases for the problem
            test_cases = TestCase.objects.filter(problem_id=problem_id)
            
            # Iterate over the test cases
            for test_case in test_cases:
                input_data = test_case.input_data.strip()
                expected_output = test_case.expected_output.strip()

                # Execute the code with the current test case input
                start = time()
                timeout=problem.time_limit
                input_data = input_data.replace('\n', '\\n')  
                #execute_result = subprocess.run(f'docker exec {cont_name} {exe_cmd} "{input_data}"', capture_output=True, shell=True)
                execute_result = subprocess.run(f'docker exec {cont_name} sh -c "echo \'{input_data}\' | {exe_cmd}"', capture_output=True, shell=True)
                execute_stdout = execute_result.stdout.decode('utf-8').strip()
                execute_stderr = execute_result.stderr.decode('utf-8').strip()

                if execute_result.returncode != 0:
                    # Runtime error occurred
                    verdict = 'Runtime Error'
                    num_failed+=1
                    verdict_details.append({'test_case_id': test_case.id, 'verdict': 'Runtime Error', 'error_message': execute_stderr})
                    print(execute_stderr)
                    

                elif execute_result.returncode == 124:
                    # Time limit exceeded
                    verdict = 'Time Limit Exceeded'
                    num_failed+=1
                    verdict_details.append({'test_case_id': test_case.id, 'verdict': 'Time limit Exceeded', 'error_message': execute_stderr})
                    print(f'Test Case {test_case.id}: Time Limit Exceeded')
                    
                
                elif execute_stdout != expected_output:
                    # Wrong answer
                    verdict = 'Wrong Answer'
                    num_failed+=1
                    verdict_details.append({'test_case_id': test_case.id, 'verdict': 'Wrong Answer', 'expected_output': expected_output, 'actual_output': execute_stdout})
                    print(f'Test Case {test_case.id}: Failed')
                    print(f'Expected Output: {expected_output}')
                    print(f'Actual Output: {execute_stdout}')
                    
                else:
                    if verdict=='Accepted':
                        num_passed+=1
                        verdict_details.append({'test_case_id': test_case.id, 'verdict': 'Accepted'})
                    
                # Print the output for the current test case
                print(f'Test Case {test_case.id}: Passed')
                print(f'Output: {execute_stdout}')

        
        print("User Output:", execute_stdout)
        print("User Error:", execute_stderr)
        print("Verdict:", verdict)
        # creating Solution class objects and showing it on leaderboard
        #user = get_user(request)
        
        user = get_user_model().objects.get(username=request.user)
        previous_verdict = Submission.objects.filter(user=user.id, problem=problem, verdict="Accepted")
        if len(previous_verdict)==0 and verdict=="Accepted":
            user.score += score
            user.num_problems_solved += 1
            user.save()

        submission.verdict = verdict
        submission.user_stdout = execute_stdout
        submission.user_stderr = execute_stderr
        #submission.runtime = run_time
        submission.save()

        # Cleanup: remove the user code file and stop the Docker container if it was started here
        os.remove(usercode_filepath)
        context = {
            'verdict': verdict,
            'num_passed': num_passed,
            'num_failed': num_failed,
            'verdict_details': verdict_details,
                    }
       
        return render(request,'submit_code.html',context)




###############################################################################################################################

#leaderboard page displaying all users according to their score

# judgeapp/views.py

@login_required(login_url='login')
def leaderboard(request):
    coders = User.objects.all()
    return render(request, 'leaderboard.html', {'coders': coders})
    


###############################################################################################################################

