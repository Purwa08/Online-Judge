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
        # setting docker-client
        docker_client = docker.from_env()
        Running = "running"

        problem = Problem.objects.get(id=problem_id)
        testcase = TestCase.objects.get(problem_id=problem_id)
        #replacing \r\n by \n in original output to compare it with the usercode output
        #testcase.expected_output = testcase.expected_output.replace('\r\n','\n').strip() 
        
        #Debugging
        print("Input:", testcase.input_data)
        print("Expected Output:", testcase.expected_output)
        # score of a problem
        if problem.difficulty=="Easy":
            score = 10
        elif problem.difficulty=="Medium":
            score = 30
        else:
            score = 50


        #setting verdict to wrong by default
        verdict = "Wrong Answer" 
        res = ""
        run_time = 0

        
        user = get_user_model().objects.get(username=request.user)
        
        # extract data from form
        form = CodeForm(request.POST)
        user_code = ''
        if form.is_valid():
            user_code = form.cleaned_data.get('user_code')
            #user_code = user_code.replace('\r\n','\n').strip()
            
        language = request.POST.get('language')
        submission = Submission(user=user, problem=problem, timestamp=datetime.now(), 
                                    language=language, user_code=user_code)
        submission.save()

        filename = str(submission.id)

        # if user code is in C++
        if language == "C++":
            extension = ".cpp"
            cont_name = "my-gcc"
            compile = f"g++ -o {filename}.exe {filename}.cpp"
            clean = f"{filename}.exe {filename}.cpp"
            docker_img = "gcc:latest"
            exe = f"{filename}.exe"
            
        elif language == "C":
            extension = ".c"
            cont_name = "oj-c"
            compile = f"gcc -o {filename} {filename}.c"
            clean = f"{filename} {filename}.c"
            docker_img = "gcc:latest"
            exe = f"./{filename}"

        #debugging
        print("User Code:", user_code)

        file = filename + extension
        filepath = os.path.join(BASE_DIR, 'usercodes', file)
        code = open(filepath,"w")
        code.write(user_code)
        code.close()

        print("Language:", language)
        print("Submission Filepath:", filepath)

        # checking if the docker container is running or not
        try:
            container = docker_client.containers.get(cont_name)
            container_state = container.attrs['State']
            container_is_running = (container_state['Status'] == Running)
            if not container_is_running:
                subprocess.run(f"docker start {cont_name}",shell=True)
        except docker.errors.NotFound:
            subprocess.run(f"docker run -dt --name {cont_name} {docker_img}",shell=True)


        # copy/paste the .cpp file in docker container 
        subprocess.run(f"docker cp {filepath} {cont_name}:/{file}",shell=True)

        # compiling the code
        cmp = subprocess.run(f"docker exec {cont_name} {compile}", capture_output=True, shell=True)
        print("Compilation Output:")
        print(cmp.stdout.decode('utf-8'))
        print(cmp.stderr.decode('utf-8'))
        if cmp.returncode != 0:
            verdict = "Compilation Error"
            subprocess.run(f"docker exec {cont_name} rm {file}",shell=True)
            print("Compilation Error occurred.")

        else:
            # running the code on given input and taking the output in a variable in bytes
            start = time()
            try:
                res = subprocess.run(f"docker exec {cont_name} sh -c 'echo \"{testcase.input_data}\" | {exe}'",
                                                capture_output=True, timeout=problem.time_limit, shell=True)
                run_time = time()-start
                subprocess.run(f"docker exec {cont_name} rm {clean}",shell=True)
                print("Execution Output:")
                print(res.stdout.decode('utf-8'))
                print(res.stderr.decode('utf-8'))
            except subprocess.TimeoutExpired:
                run_time = time()-start
                verdict = "Time Limit Exceeded"
                subprocess.run(f"docker container kill {cont_name}", shell=True)
                subprocess.run(f"docker start {cont_name}",shell=True)
                subprocess.run(f"docker exec {cont_name} rm {clean}",shell=True)
                print("Time Limit Exceeded.")


            if verdict != "Time Limit Exceeded" and res.returncode != 0:
                verdict = "Runtime Error"
                print("Runtime Error occurred.")
                

        user_stderr = ""
        user_stdout = ""
        if verdict == "Compilation Error":
            user_stderr = cmp.stderr.decode('utf-8')
        
        elif verdict == "Wrong Answer":
            user_stdout = res.stdout.decode('utf-8')
            if str(user_stdout)==str(testcase.expected_output):
                verdict = "Accepted"
            testcase.expected_output += '\n' # added extra line to compare user output having extra ling at the end of their output
            if str(user_stdout)==str(testcase.expected_output):
                verdict = "Accepted"

        print("User Output:", user_stdout)
        print("User Error:", user_stderr)
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
        submission.user_stdout = user_stdout
        submission.user_stderr = user_stderr
        submission.runtime = run_time
        submission.save()
        os.remove(filepath)
        context={'verdict':verdict}
        return render(request,'submit_code.html',context)




###############################################################################################################################

#leaderboard page displaying all users according to their score

# judgeapp/views.py

@login_required(login_url='login')
def leaderboard(request):
    coders = User.objects.all()
    return render(request, 'leaderboard.html', {'coders': coders})
    


###############################################################################################################################

