from os import times
from typing import NewType
from django.forms import utils
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import SignupForm,GiveForm,ContactUsForm,Profileform,VendorForm,PickupPointForm
from .models import Profile,Give,ContactUs,Vendor,Charge,OnDeliveryTransaction,Subscription,Location,OnPickup,PickupCentre,State,Transaction,GiveawayCap,DestinationCharge
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
import random
from django.contrib import messages
import os
from django.contrib.auth.models import User
from Giveaway.settings import STATIC_ROOT
from django.db.models import Sum
from time import sleep
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import send_mail,BadHeaderError
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django import template
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
import requests 
from .decorators import check_recaptcha
from decouple import config
from datetime import datetime,timedelta
from email.mime.image import MIMEImage
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .fields import final_checkout
from rest_framework.authtoken.models import Token

UserModel = get_user_model()



def home(request):
    return render(request,'givers/home.html')

def about(request):
    return render(request,'givers/about.html')

def signupuser(request):
    
    if request.method == 'POST':
        form = SignupForm()
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request,'Username Already Taken')
                return redirect('signupuser')
                
            elif User.objects.filter(email=email).exists():
                messages.error(request,'Email Already Exist')
                return redirect('signupuser')
    
            else:
                form = SignupForm(request.POST)
                if form.is_valid():
                    user = form.save()
                    user.refresh_from_db()
                    token=Token.objects.create(user=user)
                    # user.first_name=form.cleaned_data.get('firstname')
                    # user.last_name=form.cleaned_data.get('lastname')
                    #user.profile.firstname=form.cleaned_data.get('first_name')
                    #user.profile.lastname=form.cleaned_data.get('last_name')
                    #user.profile.email=form.cleaned_data.get('email')
                    user.profile.phone_number=  form.cleaned_data.get('phone_number')
                    if not len(str(user.profile.phone_number)) == 10:
                        messages.error(request,'invalid phone number')
                        return redirect('signupuser')
                    user.save()
                    current_site = get_current_site(request)
                    subject = 'Activate your account.'
                    plaintext = template.loader.get_template('password/acc_activate_email.txt')
                    htmltemp = template.loader.get_template('password/acc_activate_email.html')
                    c = { 
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Giveawaynow',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
                    text_content = plaintext.render(c)
                    html_content = htmltemp.render(c)
                    try:
                        msg = EmailMultiAlternatives(subject, text_content, 'Giveaway <admin@example.com>', [user.email], headers = {'Reply-To': 'admin@example.com'})
                        msg.attach_alternative(html_content, "text/html")
                        msg.send()
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    messages.info(request, "A verification mail has been sent to your email, kindly complete registration from there. ")
                    return redirect ("home")
                    '''username = form.cleaned_data.get('username')
                    password = form.cleaned_data.get('password1')
                    user= authenticate(username=username,password=password)
                    login(request,user)
                    return redirect('account_update')'''
                else:
                    form = SignupForm()
                    messages.error(request,'form is invalid')
                    return redirect('signupuser')
                    
        else:
            messages.error(request,'Password does not match')
            return redirect('signupuser')
            
    else:
        form = SignupForm()
        return render(request, 'givers/signupuser.html',{'form':form})


def contact(request):
    
    if request.method=='POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Thanks, we will treat as urgent')
            return redirect('contact')
    else:
        form=ContactUsForm()
        return render(request,'givers/contact.html',{'form':form})



@login_required(login_url='/login/')
def user_account(request):
    user = request.user
    sub=Subscription.objects.filter(email=user.email,verified=True).last()
    prof=Profile.objects.get(user=user)
    #change gift_recipient to user.profile.email
    give=Give.objects.filter(gift_recipient=request.user.username,gift_status='redeemed')
    
    offered =  Give.objects.filter(user=user, date_requested__isnull = True)[0:30]     
    all_gift = Give.objects.filter(user=user).count
    not_processed=['requested','redeemed']
    picks= Give.objects.filter(Q(gift_recipient=user) & Q(gift_status__in=not_processed))
    cart_items=picks.count
    pick_count= Give.objects.filter(gift_recipient=user,date_requested__isnull=False).count
    gifts = Give.objects.filter(gift_recipient=user, date_requested__isnull = True)
    mis_count = Give.objects.filter(gift_recipient=user, date_requested__isnull = True).count
    if user.profile.state=='lagos':
        fit=True
    else:
        fit=False
    about_to_expire=True
    if sub:
        about_to_expire=True
        if prof.balance==1:
             messages.info(request,'You have just one(1) more item to pick,kindly subscribe')
        elif prof.balance==0:
            about_to_expire=True
            prof.status=False
            prof.save(update_fields=['status'])
            messages.info(request,'Your Subscription has expired, kindly subscribe')
        else:
            about_to_expire=False 
        
    else:
        about_to_expire=True
        messages.info(request,'You need to make your first subscription')
    return render(request,'givers/user_account.html',{'gifts':gifts,'user':user,'mis_count':mis_count,'picks':picks,'pick_count':pick_count,'all_gift':all_gift,'form':VendorForm(),'offered':offered,
    'fit':fit,'about_to_expire':about_to_expire,'cart_items':cart_items})

@login_required(login_url='/login/')
def report(request):
    user = request.user
    give=Give.objects.filter(gift_recipient=request.user.username,gift_status='redeemed')
    if len(give)==0:
        amount=''
    else:
        amt=[]
        for i in give:
            if i.gift.payment_status == False:
                if i.gift.amount is not None:
                    amt.append(i.gift.amount)
        if sum(amt)==0:
            amount=''
        else:
            amount=sum(amt,1000)
    offered =  Give.objects.filter(user=user)      
    picks= Give.objects.filter(gift_recipient=user,date_requested__isnull=False)
    return render(request,'givers/report.html',{'picks':picks,'form':VendorForm(),'amount':amount,'offered':offered})




@login_required(login_url='/login/')
def logoutuser(request):
    logout(request)
    return redirect('home')


# def loginuser(request):
    
#     if request.method == 'GET':
#         return render(request, 'givers/loginuser.html', {'form':AuthenticationForm(),'recaptcha_site_key':settings.GOOGLE_RECAPTCHA_SITE_KEY})
#     else:
#         user= authenticate(request, username=request.POST['username'],password=request.POST['password']) 
#         if user is None:
#             messages.error(request,'Username or Password Incorrect')
#             return redirect('loginuser')
            
#         else:
            
#             recaptcha_response = request.POST.get('g-recaptcha-response')
#             print(recaptcha_response)
#             data = {
# 			'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
# 			'response': recaptcha_response,
# 			}
#             r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            
#             result = r.json()
            
#             if result['success']:
#                 login(request,user)
#                 if request.session.get('first_login'):
#                     return redirect('account_update')
#                 return redirect('user_account')
#             messages.error(request, 'Invalid reCAPTCHA. Please try again.')
#             return redirect('loginuser')


def loginuser(request):
    
    if request.method == 'GET':
        return render(request, 'givers/loginuser.html', {'form':AuthenticationForm()})
    else:
        user= authenticate(request, username=request.POST['username'],password=request.POST['password']) 
        check=User.objects.get(username=user).last_login
        if user is None:
            messages.error(request,'Username or Password Incorrect')
            return redirect('loginuser')
            
        else:
            login(request,user)
            if check:
                return redirect('user_account')
            return redirect('account_update')
            


@login_required(login_url='/login/')
def creategift(request):
    user=request.user
    if request.method == 'GET':
        return render(request, 'givers/creategiving.html', {'form':GiveForm()})
    else:
        form = GiveForm(request.POST,request.FILES)
        if form.is_valid():
            new_gift = form.save(commit = False)
            new_gift.user = user
            new_gift.state=user.profile.state
            new_gift.giver_number=user.profile.phone_number
            cat=new_gift.category
            tag_cat=cat
            gend=new_gift.gender
            gift=Give.objects.filter(category=cat).last()
            if gift:
                try:
                    a=gift.description
                    prev=a.split('-')[1]
                    prev_tag_number=int(prev[3:])
                    new_tag_series=prev_tag_number+1
                except:
                    b=Give.objects.filter(category=cat)
                    new_tag_series=1+len(b)
            else:
                new_tag_series=1

            desp=new_gift.description +'-' + gend + '_' + tag_cat + str(new_tag_series)
            new_gift.description=desp
            new_gift.save()
            new_gift.gift.description = desp
            new_gift.gift.category = new_gift.category
            new_gift.gift.image = form.cleaned_data.get('image')
            new_gift.gift.giver_number = user.profile.phone_number
            new_gift.save()
            messages.success(request,'gift added successfully')
            return redirect('creategift')
        else:
            return render(request,'givers/creategiving.html',{'form':form,'error':'something went wrong'})

@login_required(login_url='/login/')
def giveaway(request):
    user=request.user
    gift1= Give.objects.order_by('-date_posted')[:2]
    query = request.GET.get('q')
    if query:
        gifts = Give.objects.filter(Q(date_requested__isnull = True)&Q(state=user.profile.state)&Q(category__icontains=query)).order_by('-date_posted')
    else:
        gifts=  Give.objects.filter(Q(date_requested__isnull = True)&Q(state=user.profile.state)).order_by('-date_posted')
    p=Paginator(gifts,3)
    page_number=request.GET.get('page')
    try:
        page_obj=p.get_page(page_number)
    except PageNotAnInteger:
        page_obj=p.page(1)
    except EmptyPage:
        page_obj=p.page(p.num_pages)
    return render(request,'givers/giftpage.html',{'page_obj':page_obj,'user':user,'gift1':gift1})


@login_required(login_url='/login/')
def viewgift(request,gift_id):
    view = get_object_or_404(Give,pk = gift_id,user=request.user)
    if request.method == 'GET':
        form = GiveForm(instance=view)
        return render (request, 'givers/viewgift.html',{'view':view,'form':form})
    else:
        form = GiveForm(request.POST,instance=view)
        form.save()
        return redirect('user_account')

@login_required(login_url='/login/')
def edit_profile(request):
    user=request.user
    prof = get_object_or_404(Profile,user=request.user)
    if request.method == 'GET':
        profile_form= Profileform(instance=prof)
        return render (request, 'givers/account_update.html',{'user':user, 'profile_form':profile_form})
    else:
        profile_form = Profileform(request.POST,request.FILES,instance=prof)
        if  profile_form.is_valid():
            custom_form=profile_form.save(commit=False)
            custom_form.user=request.user
            custom_form.save()
            return redirect('user_account')
        else:
            return render(request,'givers/account_update.html',{'profile_form':profile_form,'error':'info not valid'})

@login_required(login_url='/login/')
def deletegift(request,gift_id):
    view = get_object_or_404(Give,user=request.user,pk=gift_id)
    if request.method == 'POST':
        view.delete()
        return redirect('user_account')


@login_required(login_url='/login/')
def pickgift(request,gift_id):
    user=request.user
    prof=Profile.objects.get(user=user)
    pick= get_object_or_404(Give,pk=gift_id)
    current_time=timezone.now()
    three_days_ago=timezone.now()-timedelta(days=3)
    month_ago=timezone.now()-timedelta(days=30)
    #change gift_recipient to user.email
    picked_within_three_days=Give.objects.filter(gift_recipient=user,date_requested__isnull=False,date_requested__range=[three_days_ago,current_time]).count()
    picked_within_a_month=Give.objects.filter(gift_recipient=user,date_requested__isnull=False,date_requested__range=[month_ago,current_time]).count()
    day_cap=GiveawayCap.objects.get(name='days')
    month_cap=GiveawayCap.objects.get(name='month')
    if prof.balance>0:
        prof.status=True
        prof.save(update_fields=['status'])
    else:
        prof.status=False
        prof.save(update_fields=['status'])

    if request.method=='POST':
        #check active subscription
        if user.profile.status == True:
            
        #minimize gift per user to 4 gifts in 3days
            if picked_within_three_days <= day_cap.number:
                pick.date_requested=timezone.now()
                pick.gift_recipient=str(user)
                pick.gift_status='requested'
                pick.save()
                prof.balance -=1
                prof.save(update_fields=['balance'])
            else:
                #update giftpage.html to show error message
                messages.error(request,'you have already picked 4 gifts within 3days')
                return redirect('giveaway')
        else:
            messages.error(request,'Inactive Subcription,Kindly subscribe to continue.')
            return redirect('user_account')
    # return redirect('user_account')
    messages.success(request,f'{pick.description} has been added to Requested tab in your dashboard')
    return redirect('giveaway')

@login_required(login_url='/login/')
def returnpicked(request,gift_id):
    user=request.user
    prof=Profile.objects.get(user=user)
    sub=Subscription.objects.filter(made_by=user,verified=True).last()
    view = get_object_or_404(Give,pk = gift_id)
    if request.method== 'POST':
        view.date_requested=None
        view.gift_recipient=''
        view.gift_status='unpicked'
        view.save(update_fields=['date_requested','gift_recipient','gift_status'])
    if sub:
        prof.balance+=1
        prof.status=True
        prof.save(update_fields=['balance','status'])
    else:
        prof.balance=0
        prof.save(update_fields=['balance'])
    return redirect('user_account')

@login_required(login_url='/login/')
def viewpicked(request,gift_id):
    pick = get_object_or_404(Give,pk = gift_id)
    picked= get_object_or_404(Give,pk=gift_id)
    if request.method == 'GET':
        form = GiveForm(instance=pick)
        return render (request, 'givers/viewpicked.html',{'pick':pick,'form':form,'picked':picked})
    else:
        form = GiveForm(request.POST,instance=pick)
        form.save()
        return redirect('user_account')


@login_required(login_url='/login/')
def redeempicked(request,gift_id):
    
    user=request.user
    picked= get_object_or_404(Give,pk=gift_id)
    if request.method=='POST':
        characters=list('0123456789')
        characters.extend('abcdefghijklmnopqrstuvwxyz')
        characters.extend('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        ticket=''
        for x in range(6):
            ticket +=random.choice(characters)
        form=VendorForm(request.POST,request.FILES,instance=picked)
        if form.is_valid:
            new_redeem=form.save()
            new_redeem.gift.ticket=ticket
            new_redeem.gift.request_date=timezone.now()
            new_redeem.gift.receiver_number=form.cleaned_data.get('receiver_number')
            new_redeem.gift.state=user.profile.state
            new_redeem.gift.delivery_address=form.cleaned_data.get('delivery_address')
            new_redeem.save()
        elif 'return' in request.POST:
            picked.date_requested=None
            picked.gift_recipient=''
            picked.gift_status='unpicked'
            picked.save()
        elif 'mark' in request.POST:
            return redirect ('home')
    elif request.method=='GET':
        return render(request,'givers/text.html',{'form':VendorForm(instance=picked),'picked':picked})
    return redirect('user_account')
            


@login_required(login_url='/login/')       
def cancelpicked(request):
    user=request.user
    if request.method=='POST':
        if 'redeem' in request.POST:
            state=State.objects.get(name=user.profile.state)
            city=PickupCentre.objects.filter(state=state.id)
            destination=DestinationCharge.objects.filter(state=state)
            
            return render(request,'givers/pickup_centre.html',{'form':PickupPointForm(),'form1':VendorForm(),'city':city,'destination':destination})
        
    return redirect('user_account')


@login_required(login_url='/login/')
def redeem(request):
    not_processed=['requested','redeemed']
    user=request.user
    destination=DestinationCharge.objects.get(city=request.POST.get('city','empty'))
    #gives=Give.objects.filter(gift_recipient=user,gift_status__in=not_processed)
    gives=Give.objects.select_related('gift').filter(gift_recipient=user,gift_status__in=not_processed)
    print(len(gives))
    if user.profile.state=='lagos':
        fit=True
    else:
        fit=False
    if request.method=='POST':
        characters=list('0123456789')
        characters.extend('abcdefghijklmnopqrstuvwxyz')
        characters.extend('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        ticket=''
        for x in range(6):
            ticket +=random.choice(characters)
        give=gives[0]
        give.gift_status='redeemed'
        give.save()
        form=VendorForm(request.POST,request.FILES,instance=give)
        
        if form.is_valid:
            print('in form')
            new_redeem=form.save()
            new_redeem.gift.ticket=ticket
            new_redeem.gift.request_date=timezone.now()
            new_redeem.gift.receiver_number=form.cleaned_data.get('receiver_number')
            #addition
            new_redeem.gift.pickup_location='delivery'
            print(len(str(form.cleaned_data.get('receiver_number'))))
            new_redeem.gift.amount=destination.charge
            new_redeem.gift.state=user.profile.state
            new_redeem.gift.delivery_address=form.cleaned_data.get('delivery_address')
            new_redeem.save()
            if len(gives)>1:
                for give in gives[1:]:
                    print('in iterator')
                    give.gift_status='redeemed'
                    give.save()
                    vend = Vendor.objects.get(give=give)
                    vend.ticket=ticket
                    vend.amount=0
                    vend.request_date=timezone.now()
                    vend.receiver_number=form.cleaned_data.get('receiver_number')
                    vend.state=user.profile.state
                    vend.delivery_address=form.cleaned_data.get('delivery_address')
                    #update pickup location
                    vend.pickup_location='delivery'
                    vend.save(update_fields=['ticket','request_date','receiver_number','delivery_address','pickup_location','amount'])
                    
            else:
                new_redeem.gift.ticket=ticket
                new_redeem.gift.request_date=timezone.now()
                new_redeem.gift.receiver_number=form.cleaned_data.get('receiver_number')
                new_redeem.gift.state=user.profile.state
                new_redeem.gift.amount=destination.charge
                new_redeem.gift.delivery_address=form.cleaned_data.get('delivery_address')
                #update pickup location
                new_redeem.gift.pickup_location='delivery'
                new_redeem.save()
    delivery=destination.charge
    request.session['delivery']=delivery
    service=Charge.objects.get(name='standard')
    service_charge=service.charge
    amount=delivery+service_charge
    cart_items=len(gives)
    print(cart_items)
    tested_delivery=OnDeliveryTransaction.objects.filter(made_by=user)
    if len(tested_delivery)>=1:
        tasted=True
    else:
        tasted=False
    
    if destination=='empty':
        messages.error(request,'choose the city you reside')
        return HttpResponse('kindly go back and choose the city you reside')
    else:
        return render(request,'givers/checkout.html',{'fit':fit,'amount':amount,'gifts':gives,'cart_items':cart_items,'delivery':delivery,'service_charge':service_charge,'tasted':tasted})


def my_mail(request):  
        subject = "Greetings from Programink"  
        msg     = "Learn Django at Programink.com"  
        to      = "shawen022@yahoo.com"  
        res     = send_mail(subject, msg, settings.EMAIL_HOST_USER, [to])  
        if(res == 1):  
            msg = "Mail Sent Successfully."  
        else:  
            msg = "Mail Sending Failed."  
        return HttpResponse(msg)  


def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data)|Q(username=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					plaintext = template.loader.get_template('password/password_reset_email.txt')
					htmltemp = template.loader.get_template('password/password_reset_email.html')
					c = { 
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Giveaway',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					text_content = plaintext.render(c)
					html_content = htmltemp.render(c)
					try:
						msg = EmailMultiAlternatives(subject, text_content, 'Giveaway <admin@example.com>', [user.email], headers = {'Reply-To': 'admin@example.com'})
						msg.attach_alternative(html_content, "text/html")
                        
						msg.send()
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					messages.info(request, "Password reset instructions have been sent to the email address entered.")
					return redirect ("home")
                
               
	password_reset_form = PasswordResetForm()
	return render(request,"password/password_reset.html",{"password_reset_form":password_reset_form})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request,'Thank you for your email confirmation. Now you can login your account.')
        return redirect('loginuser')
    else:
        return HttpResponse('Activation link is invalid!')


@login_required(login_url='/login/')
def initiate_payment(request):
    cost=request.session.get('delivery')
    user = request.user
    trans=Transaction()
    a,b=final_checkout(trans,user,cost)
    total=a['amount']
    paystack_charge=b
    transaction=Transaction.objects.create(**a)

    return render(request,'givers/make_payment.html',{'transaction':transaction,'paystack_public_key':settings.PAYSTACK_PUBLIC_KEY,
    'logistics':cost,'charge':paystack_charge,'total':total})

def verify_payment(request,ref):
    payment = get_object_or_404(Transaction,ref=ref)
    verified = payment.verify_payment()
    
    if verified:
        #change filter to gift_recipient=user.profile.email
        give=Give.objects.filter(gift_recipient=request.user,gift_status='redeemed')
        for i in give:
            if i.gift.payment_status in ['unpaid','on-delivery','on-pickup']:
                i.gift_status='paid'
                i.save()
                vend= Vendor.objects.get(give=i)
                vend.payment_status='paid'
                vend.save(update_fields=['payment_status'])
        messages.success(request, 'Payment Successful,you will be contacted soon for delivery')
    else:
        messages.error(request,"Payment Failed.")
    return redirect('user_account')



@login_required(login_url='/login/')
def on_delivery_payment(request):
    user=request.user
    cost=request.session.get('delivery')
    trans=OnDeliveryTransaction()
    a,b=final_checkout(trans,user,cost) 
    amount=a['amount']
    OnDeliveryTransaction.objects.create(**a)
    latest_on_delivery=OnDeliveryTransaction.objects.filter(made_by=request.user).last()
    ref=latest_on_delivery.ref
    messages.success(request,'you will be contacted soon for delivery')
    plaintext = template.loader.get_template('password/invoice.txt')
    c={
        'amount':amount,
        'ref':ref,
        'ordered_giveaway':b
    }
    text_content = plaintext.render(c)
    
    subject = "Giveawaynow invoice"  
    msg = text_content
    to = request.user.email
    send_mail(subject, msg, settings.EMAIL_HOST_USER, [to])
    return redirect('user_account')

def ad_text(request):
    return render(request,'password/ads.txt')

@login_required(login_url='/login/')
def subscription(request):
    basic=Charge.objects.get(name='basic')
    basic_charge=basic.charge
    standard=Charge.objects.get(name='standard')
    standard_charge=standard.charge
    premium=Charge.objects.get(name='premium')
    premium_charge=premium.charge

    return render(request,'givers/subscription.html',{'basic':basic,'standard':standard,'premium':premium})

@login_required(login_url='/login/')
def initiate_subscription(request):
    user=User.objects.get(username=request.user)
    basic=Charge.objects.get(name='basic')
    standard=Charge.objects.get(name='standard')
    premium=Charge.objects.get(name='premium')
    
    if basic.name in request.POST:
        amount=basic.charge
        package=basic.name
        days=30
        balance=4
    if standard.name in request.POST:
        amount=standard.charge
        package=standard.name
        days=90
        balance=7
    if premium.name in request.POST:
        amount=premium.charge
        package=premium.name
        days=180
        balance=10
    sub=Subscription.objects.filter(made_by=request.user,verified=True).last()
    end_date=timezone.now() + timedelta(days=days)
    if sub:
        if sub.end_date<=timezone.now():
            end_date=timezone.now() + timedelta(days=days)
        elif sub.end_date > timezone.now():
            end_date=sub.end_date + timedelta(days=days)
    Vat=0.075*amount
    Vat=round(Vat,2)
    total1=amount+Vat
    if total1>=2500:
        paystack_charge=100 + (0.015*total1)
    else:
        paystack_charge=(0.015*total1)
    paystack_charge=round(paystack_charge,2)
    total=total1+paystack_charge
    total=round(total,2)
    data={
        'made_by':request.user,
        'amount':total,
        'end_date':end_date,
        'email':request.user.email,
        'balance':balance
    }
    
    request.session['package']=package
    subscription=Subscription.objects.create(**data)
    return render(request,'givers/make_subscription.html',{'basic':basic,'standard':standard,'premium':premium,'subscription':subscription,
    'paystack_public_key':settings.PAYSTACK_PUBLIC_KEY,'Vat':Vat,'amount':amount,'paystack_charge':paystack_charge,'package':package})

@login_required(login_url='/login/')
def verify_subscription(request,ref):
    user=User.objects.get(username=request.user)
    profile=Profile.objects.get(email=request.user.email)
    payment = get_object_or_404(Subscription,ref=ref)
    verified = payment.verify_payment()
    if verified:
        profile.package=request.session.get('package')
        profile.status=True
        profile.balance=payment.balance+profile.balance
        profile.end_date=payment.end_date
        profile.save(update_fields=['end_date','package','balance','status'])
        messages.success(request, 'Subscription Successful.')
    else:
        messages.error(request,"Subscription Failed,check balance and try again.")
    del request.session['package']
    return redirect('user_account')




@login_required(login_url='/login/')
def pickup(request):
    
    shape=request.session.get('gift_id')
    user=request.user
    if request.method=='POST':
        print(request.POST['centre'])
        characters=list('0123456789')
        characters.extend('abcdefghijklmnopqrstuvwxyz')
        characters.extend('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        ticket=''
        for x in range(6):
            ticket +=random.choice(characters)
        
        items=[]
        for id in shape:
            give=Give.objects.get(id=id)
            give.gift_status='on-pickup'
            give.save()
            items.append(give.description)
            vend = Vendor.objects.get(give=give)
            vend.ticket=ticket
            vend.request_date=timezone.now()
            vend.receiver_number=user.profile.phone_number
            vend.state=user.profile.state
            vend.delivery_address='on-pickup'
            vend.payment_status='on-pickup'
            vend.pickup_location= request.POST['centre']  
            vend.save(update_fields=['ticket','request_date','receiver_number','delivery_address','payment_status','pickup_location'])
        item=[]
        for count,ele in enumerate(items,1):
            t=f'{count}.{ele}'
            item.append(t)
        item=('\n'.join(item))
        data={
            'made_by':user,
            'item':item,
            'state':user.profile.state,
            'pickup_centre':request.POST['centre'],
            'email':user.email,
            'collection_status':False
            }
    
        on_pickup=OnPickup.objects.create(**data)
        latest_on_pickup=OnPickup.objects.filter(made_by=user).last()
        ref=latest_on_pickup.ref
        a=State.objects.get(name=user.profile.state)
        b=PickupCentre.objects.get(state=a.id,name=data['pickup_centre'] )
        c=Location.objects.get(state=a.id,pickup_centre=b.id)
        address=c.address
        phone_number=c.phone_number
        plaintext = template.loader.get_template('password/on_pickup.txt')
        mail_data={
            'phone_number':str(0)+str(phone_number),
            'address':address,
            'pickup_centre':data['pickup_centre'], 
            'ref':ref,
            'item':item,
            }
        text_content = plaintext.render(mail_data)
            
        subject = "Giveawaynow Pickup details"  
        msg = text_content
        to = user.email
        send_mail(subject, msg, settings.EMAIL_HOST_USER, [to])

    del request.session['gift_id']
    messages.info(request, "Kindly ensure you check your mail for pickup details")
    return redirect('user_account')









    #for API
from rest_framework.mixins import CreateModelMixin,ListModelMixin,RetrieveModelMixin,UpdateModelMixin
from rest_framework import viewsets
from .serializer import OnDeliveryTransactionSerializer,UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken


# class ProfileViewSet(GenericViewSet,CreateModelMixin,ListModelMixin,RetrieveModelMixin,UpdateModelMixin):
#     # serializer_class = ProfileSerializer
#     # queryset= Profile.objects.all()
#     pass
@api_view(['GET','POST','PUT'])
def on_delivery_list(request,format=None):
    user=request.user
    
    if request.method=='GET':
        on_delivery=OnDeliveryTransaction.objects.filter(delivered=False)
        serializer=OnDeliveryTransactionSerializer(on_delivery,many=True)
        return Response(serializer.data)
    elif request.method=='POST':
        if len(request.data)>1:
            serializer_list=[OnDeliveryTransactionSerializer(data=i) for i in request.data]
            posted_serializer=[]
            for serializer in  serializer_list:
                if serializer.is_valid():
                    serializer.save()
                    posted_serializer.append(serializer.data)
            return Response(posted_serializer,status=status.HTTP_201_CREATED)
        else:
            serializer=OnDeliveryTransactionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
    elif request.method=='PUT':
        datas=request.data
        trans_id=[]
        for data in datas:
            trans_id.append(data['id'])
        delivered_items=OnDeliveryTransaction.objects.filter(id__in=trans_id)
        gift_ids=[]
        for trans in delivered_items:
            gift_ids+=trans.items_id
        gives=Give.objects.filter(id__in=gift_ids).update(gift_status='received',date_received=timezone.now())
        vends=Vendor.objects.filter(give__in=gift_ids).update(payment_status='paid')
        serializer_list=[OnDeliveryTransactionSerializer(i,data={'id':i.id,'ref':i.ref,'made_on':i.made_on,'amount':i.amount,'delivery_address':i.delivery_address,'delivered':True,'items_id':i.items_id}) for i in delivered_items ]
        for serializer in serializer_list:
            if serializer.is_valid():
                serializer.save(update_fields=['delivered'])
        return Response({'message':'delivered items updated'},status=status.HTTP_201_CREATED)


@api_view(['POST'])
def update_delivered(request,format=None):
    if request.method=='POST':
        check_ids=request.POST.getlist("chk[]")
        data=[{'id':int(i),'delivered':True} for i in check_ids]
        headers={ 'Content-Type':'application/json'}
        updated_details=requests.put('http://localhost:8000/api/on-delivery/',json=data,headers=headers)
        return redirect('get_news')
    return redirect('get_news')
    

def get_news(request):
    url='http://localhost:8000/api/on-delivery/'
    response=requests.get(url)
    if response.status_code==200:
        news=json.loads(response.text)
    else:
        return HttpResponse(response.status_code)
    return render(request,'givers/testing.html',{'news':news})

# @api_view(['POST'])
# def api_loginuser(request,format=None):
#     data=request.data
#     user= authenticate(request, username=data['username'],password=data['password'])
#     if user is None:
#         return Response({'message':'incorrect username or password'},status=status.HTTP_401_UNAUTHORIZED)
#     else:
#         login(request,user)
#         return Response({'message':'login successful'},status=status.HTTP_200_OK)

@api_view(['POST'])
def deliver_token(request):
    data=request.data
    user=User.objects.get(username=data['username'])
    token=TokenSerializer(user)
    user1=authenticate(request, username=data['username'],password=data['password'])
    if user1 is None:
        return Response({'message':'incorrect username or password'},status=status.HTTP_401_UNAUTHORIZED)
    else:
        login(request,user1)
        if token.exists():
            print('in')
            return Response(token.data,status=status.HTTP_200_OK)




class UserViewSets(viewsets.ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer

class HelloView(APIView):
    permission_classes=(IsAuthenticated,)

    def get(self,request):
        content={'message':'hello shawen17'}
        return Response(content)
