from django import forms
from .models import City, Chupiao


class ShowForm(forms.Form):
    date = forms.DateField()
    city = forms.ModelChoiceField(required=False, queryset=City.objects.order_by('seq'))


class ApiShowDayForm(forms.Form):
    date = forms.DateField()
    city = forms.CharField(required=False, max_length=100)


class ChupiaoSearchForm(forms.Form):
    keyword = forms.CharField(label='音乐剧', max_length=100)
    date = forms.DateField(label='日期')


class ChupiaoForm(forms.ModelForm):
    class Meta:
        model = Chupiao
        fields = ['show', 'par_value', 'seat', 'price', 'xianyu', 'note']

    def clean(self):
        cleaned_data = super().clean()
        par_value = cleaned_data.get("par_value")
        price = cleaned_data.get("price")

        if price > par_value:
            msg = "出票价格不能高于票面价格。"
            self.add_error('price', msg)
