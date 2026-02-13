from django import forms
from django.utils import timezone

from .models import Condition


class ConditionInputForm(forms.Form):
    SCORE_CHOICES = [(i, str(i)) for i in range(1, 6)]
    physical = forms.TypedChoiceField(
        choices=SCORE_CHOICES,
        coerce=int,
        required=False,
        widget=forms.RadioSelect,
    )
    mental = forms.TypedChoiceField(
        choices=SCORE_CHOICES,
        coerce=int,
        required=False,
        widget=forms.RadioSelect,
    )
    is_absent = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        is_absent = cleaned.get("is_absent")
        physical = cleaned.get("physical")
        mental = cleaned.get("mental")

        if is_absent:
            if physical is not None or mental is not None:
                raise forms.ValidationError("休みの場合はスコアを入力できません。")
        else:
            if physical is None or mental is None:
                raise forms.ValidationError("休みでない場合はスコアの入力が必要です。")

        if self.user and Condition.objects.filter(user=self.user, date=timezone.localdate()).exists():
            raise forms.ValidationError("本日は既に入力済みです。")

        return cleaned

    def save(self):
        cleaned = self.cleaned_data
        is_absent = cleaned["is_absent"]
        return Condition.objects.create(
            user=self.user,
            date=timezone.localdate(),
            physical=None if is_absent else cleaned["physical"],
            mental=None if is_absent else cleaned["mental"],
            is_absent=is_absent,
        )
