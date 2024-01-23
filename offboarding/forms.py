"""
offboarding/forms.py

This module is used to register forms for offboarding app
"""

from typing import Any
from django import forms
from django.template.loader import render_to_string
from base.forms import ModelForm
from employee.forms import MultipleFileField
from offboarding.models import (
    EmployeeTask,
    Offboarding,
    OffboardingEmployee,
    OffboardingNote,
    OffboardingStage,
    OffboardingStageMultipleFile,
    OffboardingTask,
)


class OffboardingForm(ModelForm):
    """
    OffboardingForm model form class
    """

    verbose_name = "Offboarding"

    class Meta:
        model = Offboarding
        fields = "__all__"

    def as_p(self):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("common_form.html", context)
        return table_html


class OffboardingStageForm(ModelForm):
    """
    OffboardingStage model form
    """

    verbose_name = "Stage"

    class Meta:
        model = OffboardingStage
        fields = "__all__"
        exclude = [
            "offboarding_id",
        ]

    def as_p(self):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("common_form.html", context)
        return table_html


class OffboardingEmployeeForm(ModelForm):
    """
    OffboardingEmployeeForm model form
    """

    verbose_name = "Offboarding "

    class Meta:
        model = OffboardingEmployee
        fields = "__all__"
        widgets = {
            "notice_period_starts": forms.DateTimeInput(attrs={"type": "date"}),
            "notice_period_ends": forms.DateTimeInput(attrs={"type": "date"}),
        }

    def as_p(self):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("common_form.html", context)
        return table_html

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial["notice_period_starts"] = self.instance.notice_period_starts.strftime("%Y-%m-%d")
            self.initial["notice_period_ends"] = self.instance.notice_period_ends.strftime("%Y-%m-%d")

class StageSelectForm(ModelForm):
    """
    This form is used to register drop down for the pipeline
    """

    class Meta:
        model = OffboardingEmployee
        fields = [
            "stage_id",
        ]

    def __init__(self, *args, offboarding=None, **kwargs):
        super().__init__(*args, **kwargs)
        attrs = self.fields["stage_id"].widget.attrs
        attrs["onchange"] = "offboardingUpdateStage($(this))"
        attrs["class"] = "w-100 oh-select-custom"
        self.fields["stage_id"].widget.attrs.update(attrs)
        self.fields["stage_id"].empty_label = None
        self.fields["stage_id"].queryset = OffboardingStage.objects.filter(
            offboarding_id=offboarding
        )
        self.fields["stage_id"].label = ""


class NoteForm(ModelForm):
    """
    Offboarding note model form
    """

    verbose_name = "Add Note"

    class Meta:
        model = OffboardingNote
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["attachment"] = MultipleFileField(label="Attachements")
        self.fields["attachment"].required = False

    def as_p(self):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("common_form.html", context)
        return table_html

    def save(self, commit: bool = ...) -> Any:
        multiple_attachment_ids = []
        attachemnts = None
        if self.files.getlist("attachment"):
            attachemnts = self.files.getlist("attachment")
            self.instance.attachemnt = attachemnts[0]
            multiple_attachment_ids = []
            for attachemnt in attachemnts:
                file_instance = OffboardingStageMultipleFile()
                file_instance.attachment = attachemnt
                file_instance.save()
                multiple_attachment_ids.append(file_instance.pk)
        instance = super().save(commit)
        if commit:
            instance.attachments.add(*multiple_attachment_ids)
        return instance, attachemnts


class TaskForm(ModelForm):
    """
    TaskForm model form
    """

    verbose_name = "Offboarding Task"
    tasks_to = forms.ModelMultipleChoiceField(
        queryset=OffboardingEmployee.objects.all()
    )

    class Meta:
        model = OffboardingTask
        fields = "__all__"
        exclude = [
            "status",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["stage_id"].empty_label = "All Stages in Offboarding"
        self.fields["managers"].empty_label = None

    def as_p(self):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("common_form.html", context)
        return table_html

    def save(self, commit: bool = ...) -> Any:
        super().save(commit)
        if commit:
            employees = self.cleaned_data["tasks_to"]
            print(employees)
            for employee in employees:
                assinged_task = EmployeeTask.objects.get_or_create(
                    employee_id=employee,
                    task_id=self.instance,
                )