from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ConditionInputForm


@login_required
def input_view(request):
    if request.method == "POST":
        form = ConditionInputForm(request.POST, user=request.user)
        if form.is_valid():
            return render(request, "conditions/confirm.html", {"form": form})
    else:
        form = ConditionInputForm(user=request.user)
    return render(request, "conditions/input.html", {"form": form})


@login_required
def submit_view(request):
    if request.method != "POST":
        return redirect("conditions:input")

    form = ConditionInputForm(request.POST, user=request.user)
    if not form.is_valid():
        return render(request, "conditions/input.html", {"form": form})

    form.save()
    return render(request, "conditions/complete.html")


@login_required
def history_view(request):
    conditions = (
        request.user.condition_set.order_by("-date", "-created_at")
    )
    return render(request, "conditions/history.html", {"conditions": conditions})
