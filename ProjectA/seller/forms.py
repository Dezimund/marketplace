from django import forms
from main.models import Product, Category, Size, ProductSize, ProductImage


class ProductForm(forms.ModelForm):

    main_image = forms.ImageField(
        required=False,
        label='Головне зображення',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'price', 'old_price', 'description',
            'color', 'is_recommended',
            # 'material','stock',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Назва товару'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'old_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Стара ціна (опціонально)',
                'step': '0.01',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Опис товару...'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Колір'
            }),
            # 'material': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'Матеріал'
            # }),
            # 'stock': forms.CheckboxInput(attrs={
            #     'class': 'form-check-input'
            # }),
            'is_recommended': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Назва товару',
            'category': 'Категорія',
            'price': 'Ціна (₴)',
            'old_price': 'Стара ціна (₴)',
            'description': 'Опис',
            'color': 'Колір',
            # 'material': 'Матеріал',
            # 'stock': 'В наявності',
            'is_recommended': 'Рекомендований',
        }


class ProductSizeForm(forms.Form):

    sizes = forms.ModelMultipleChoiceField(
        queryset=Size.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label='Доступні розміри'
    )

    def __init__(self, *args, category=None, **kwargs):
        super().__init__(*args, **kwargs)
        if category and category.requires_size:
            self.fields['sizes'].queryset = category.sizes.all()


class ProductImageForm(forms.ModelForm):

    class Meta:
        model = ProductImage
        fields = ['image',]
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            # 'alt_text': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'Опис зображення'
            # }),
            # 'main_image': forms.CheckboxInput(attrs={
            #     'class': 'form-check-input'
            # }),
        }
        labels = {
            'image': 'Зображення',
            # 'alt_text': 'Опис (alt)',
            'main_image': 'Головне зображення',
        }


ProductImageFormSet = forms.inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=3,
    can_delete=True,
    max_num=10
)