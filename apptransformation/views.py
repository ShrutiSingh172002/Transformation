from django.shortcuts import render
from rest_framework import generics
from .serializers import RegisterSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic import TemplateView
from django.http import HttpResponse
from .mdlProcess.mdlMain import process_transformation
from .mdlProcess.logger import Logger
import time
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,FileResponse, Http404
from .mdlProcess.mdlMain import *
import os
from rest_framework import status
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(user_email):
    subject = "Welcome to Our Service"
    message = "Thank you for registering with us!"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)

taskcompleted = False
runcnt = 1

logger = Logger.get_logger()

# Create your views here.

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()  # Create the user using the custom `create` method in the serializer
            return Response({'detail': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello {request.user.username}, you're authenticated!"})

def index_page(request):
    return render(request, "index.html")
   
def contact_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # You can store it in DB or send an email — example below sends email
        try:
            full_message = f"Message from {name} <{email}>:\n\n{message}"
            send_mail(subject, full_message, settings.DEFAULT_FROM_EMAIL, ['contact@cloudnest.com'])
            return render(request, 'contact.html', {'success': True})
        except Exception as e:
            return render(request, 'contact.html', {'error': str(e)})

    return render(request, "contact.html")

   
def services_page(request):
    return render(request, "services.html")
   
def about_page(request):
    return render(request, "about.html")

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_conditions(request):
    return render(request, 'terms_conditions.html')

def services(request):
    return render(request, 'services.html')



def upload_template(request):
    dictProcessTransformation = {}
    server = '158.69.236.25'
    database = 'INNOVAPTE'
    username = 'RINKU'
    password = 'Welcome@123'
    saptepmversion = "2023"
    # templatename = "FI - GL Accounts"
    sapuser = 'SANDIP'
    sappass= 'Welcome@123456789'
    sapashost= '11.11.11.13'
    sapclient= '100'
    # strOutPutPath = r'D:\Innovapte\Python\Transformation\Blank Template\OutPut'
    clientid = '1'
    global taskcompleted
    global runcnt
    runcnt += 1
    print(str(taskcompleted))
    print(str(runcnt))


    if taskcompleted == False:
        taskcompleted = True
        try:
            if request.method == "POST":
                try:
                    data = json.loads(request.body)
                    templatename = data.get('template')
                    # strOutPutPath = data.get('folder')
                    strOutPutPath = r'C:\DataVapte\OutPut'

                    if not strOutPutPath:
                        return JsonResponse({"message": "Folder path is required."}, status=400)

                    # Now call your model function
                    # Example: 
                    
                    t = time.time()

                    dictProcessTransformation = process_transformation(server,database,username,password,saptepmversion,templatename,sapuser,sappass,sapashost,sapclient,strOutPutPath,clientid)
                    if dictProcessTransformation['iserror'] == True:
                        logger.error(f"Error Process Transformation: {dictProcessTransformation}")
                        taskcompleted = False
                        return HttpResponse(f"Error Process Transformation: {dictProcessTransformation}")
                    else:
                        totaltime = time.time() - t
                        strZipPath = dictProcessTransformation['value']
                        logger.info(f"Files Save on Path: {strZipPath}")
                        logger.info(f"Process Completed in Total Time: {totaltime}")
                        taskcompleted = False
                        filename = os.path.basename(strZipPath)
                        return JsonResponse({"filename": filename})

                except Exception as e:
                    taskcompleted = False
                    return JsonResponse({"message": f"Error: {str(e)}"}, status=500)
            else:
                taskcompleted = False
                return JsonResponse({"message": "Invalid request method."}, status=405)
        except Exception as e:
            taskcompleted = False
            return HttpResponse(f"Error Process Transformation: {str(e)}")
        
    else:
        taskcompleted = False
        
def download_file(request,filename):
    file_path = os.path.join('C:/DataVapte/OutPut', filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    else:
        raise Http404("File not found")

def download_view(request, filename):
    file_path = os.path.join('C:/DataVapte/OutPut', filename)
    
    # If the file exists, show the download button, else raise 404 error
    if os.path.exists(file_path):
        return render(request, 'download.html', {'filename': filename})
    else:
        raise Http404("File not found")

def transformation_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        license_id = request.POST['license_id']

        user = authenticate(request, username=username, password=password)
        if user is not None and user.profile.license_id == license_id:
            login(request, user)
            return redirect('transformation_dashboard')  # Protected transformation view
        else:
            error = "Invalid credentials or license ID"
            return render(request, 'transformation_login.html', {'error': error})
    return render(request, 'transformation_login.html')