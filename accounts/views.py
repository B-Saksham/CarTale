from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomerRegistrationForm


@login_required
def post_login_redirect(request):
    if request.user.is_superuser or request.user.role == 'admin':
        return redirect('/admin/')
    return redirect('/')


def register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # 🔒 Lock customer role & permissions
            user.role = 'user'
            user.is_staff = False
            user.is_superuser = False

            user.save()
            login(request, user)

            return redirect('/')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})
