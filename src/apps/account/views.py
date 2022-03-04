import random

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import View
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import OtpCode
from .forms import (
    UserRegistrationForm,
    VerifyCodeForm,
    UserLoginForm,
    ForgettingPasswordForm,
    VerifyCodePasswordForm,
    RestPasswordDoneForm,
    UserEditProfileForm,
)
from .mixins import CheckAccessTpPageWithSessionMixins
from apps.utils import send_otp_code, get_instance_otpcode_from_session, delete_session_key


class RegisterView(View):
    """
        Register a new User
        input: phone_number and password
        save to session detail input
        output: send code for phone_number
    """
    form_class = UserRegistrationForm
    template_name = 'account/registration/register.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone')
            password = form.cleaned_data.get('password')
            password2 = form.cleaned_data.get('password2')

            random_code = random.randint(100000, 999999)
            random_code = str(random_code)
            # send_otp_code(phone, random_code)
            print(random_code)
            otp_code = OtpCode.objects.create(phone_number=phone, code=random_code)
            otp_code.expire_time += timezone.timedelta(minutes=3)
            otp_code.save()
            request.session['user_registration_info'] = {
                'phone_number': phone,
                'password': password,
                'password2': password2,
            }

            messages.success(request, _('we sent you a code'), 'success')
            return redirect('account:verify')
        return render(request, self.template_name, {'form': form})


class UserRegisterVerifyCodeView(CheckAccessTpPageWithSessionMixins, View):
    """
        Validation new user with code
        input: code
        get detail user form session and check code with code in session
        output: register user
    """
    form_class = VerifyCodeForm
    template_name = 'account/registration/verify.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('catalogue:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user_session = request.session.get('user_registration_info')
        code_instance = get_instance_otpcode_from_session(user_session)

        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if code_instance.expire_time > timezone.now():
                if cd.get('code') == code_instance.code:
                    user = get_user_model().objects.create_user(phone_number=user_session.get('phone_number'),
                                                                password=user_session.get('password'))

                    user.is_active = True
                    user.save()
                    login(request, user)
                    code_instance.delete()
                    delete_session_key(request, 'user_registration_info')
                    messages.success(request, _('you registered. and loggen in successfully'), 'success')
                    return redirect('catalogue:home')
                else:
                    messages.error(request, _('this code is wrong'), 'danger')
                    return redirect('account:verify')
            else:
                code_instance.delete()
                delete_session_key(request, 'user_registration_info')
                messages.warning(request, 'code is expire . Try Again', 'warning')
                return redirect('account:register')

        return redirect('catalogue:home')


class UserLoginView(View):
    """
        Login a user
        input: phone_number and password
        output: Login a user and redirect to path
    """
    form_class = UserLoginForm
    template_name = 'account/registration/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next', None)
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('catalogue:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):

        form = self.form_class(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=phone, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, _('you logged in successfully'), 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('catalogue:home')
            else:
                messages.error(request, _('wrong phone or password'), 'warning')
                return redirect('account:login')
        else:
            return render(request, self.template_name, {'form': form})


class ForgettingPasswordView(View):
    """
        Forget user password and send code
        input: phone number
        check if phone number is exist and send code for reset password & create session for save phone_number
        output: send code
    """
    form_class = ForgettingPasswordForm
    template_name = 'account/password/forget_password.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone')
            user = get_object_or_404(get_user_model(), phone_number=phone)
            if user is not None:
                random_code = random.randint(100000, 999999)
                random_code = str(random_code)
                # send_otp_code(phone, random_code)
                print(random_code)
                otp_code = OtpCode.objects.create(phone_number=phone, code=random_code)
                otp_code.expire_time += timezone.timedelta(minutes=3)
                otp_code.save()
                request.session['user_forgetting_password'] = {
                    'phone_number': phone,
                }

                messages.success(request, _('we sent you a code'), 'success')
                return redirect('account:reset_password')
            else:
                messages.warning(request, _('wrong phone number!'), 'info')
                return redirect('account:forget_password')

        else:
            return render(request, self.template_name, {'form': form})


class ResetPasswordView(CheckAccessTpPageWithSessionMixins, View):
    """
        Validation user with code for reset password
        input: code
        check is code is correct and session exists
        output: redirect for change password view
    """
    form_class = VerifyCodePasswordForm
    template_name = 'account/password/reset_password.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user_password_session = request.session.get('user_forgetting_password')
        code_instance = get_instance_otpcode_from_session(user_password_session)

        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if code_instance.expire_time > timezone.now():
                if cd.get('code') == code_instance.code:
                    code_instance.delete()
                    messages.success(request, 'now change password!', 'success')
                    return redirect('account:reset_password_done')
                else:
                    messages.error(request, _('this code is wrong'), 'danger')
                    return redirect('account:reset_password')
            else:
                code_instance.delete()
                delete_session_key(request, 'user_forgetting_password')
                messages.warning(request, 'code is expire . Try Again', 'warning')
                return redirect('account:register')
        return redirect('catalogue:home')


class ResetPasswordDoneView(CheckAccessTpPageWithSessionMixins, View):
    """
        reset password completely
        input: password and confirm password
        check is session exists and get form database current user
        output: change current password
    """
    form_class = RestPasswordDoneForm
    template_name = 'account/password/reset_password_done.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user_password_session = request.session.get('user_forgetting_password')

        form = self.form_class(request.POST)
        if form.is_valid():
            user = get_object_or_404(get_user_model(), phone_number=user_password_session.get('phone_number'))
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            delete_session_key(request, 'user_forgetting_password')
            messages.success(request, 'reset password successfully!', 'success')
            return redirect('account:login')
        return render(request, self.template_name, {'form': form})


class LogoutView(LoginRequiredMixin, View):
    """
        logout current user from site
        and current user must be available
        output: logout user and redirect to home page
    """

    def get(self, request):
        logout(request)
        messages.success(request, 'your logged out successfully!', 'success')
        return redirect('account:login')


class DashboardView(LoginRequiredMixin, View):
    """
        Dashboard user
        current user must be available
        output: return to dashboard current user
    """

    template_name = 'account/dashboard/dashboard.html'

    def get(self, request):
        return render(request, self.template_name)


class EditProfileView(LoginRequiredMixin, View):
    """
        Change profile user
        input: email, full_name, (phone_number can't change)
        show form for change current user info and current user must be available
    """

    form_class = UserEditProfileForm
    template_name = 'account/dashboard/edit_profile.html'

    def get(self, request):
        user_form = self.form_class(instance=request.user)
        return render(request, self.template_name, {'user_form': user_form})

    def post(self, request):
        user_form = self.form_class(data=request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'updating your profile successfully', 'success')
            return redirect('account:dashboard')
        return render(request, self.template_name, {'user_form': self.form_class(instance=request.user)})
