from rest_framework import serializers
from django.db.models import Sum
from main.models import Category, Product, ProductSize, ProductImage, Size
from cart.models import Cart, CartItem
from users.models import CustomUser
from django.utils.text import slugify
from seller.views import generate_unique_slug


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    is_seller = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name',
                  'phone_number', 'is_seller', 'date_joined']
        read_only_fields = ['id', 'date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_is_seller(self, obj):
        if hasattr(obj, 'is_seller') and obj.is_seller:
            return True
        if obj.has_perm('main.add_product'):
            return True
        if obj.is_staff or obj.is_superuser:
            return True
        return False


class UserDetailSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            'company', 'address1', 'address2', 'city',
            'country', 'state', 'postal_code'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Паролі не співпадають'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'requires_size', 'products_count']
        read_only_fields = ['id', 'slug']

    def get_products_count(self, obj):
        return obj.products.count()


class SizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Size
        fields = ['id', 'name']


class ProductSizeSerializer(serializers.ModelSerializer):
    size = SizeSerializer(read_only=True)
    size_id = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(),
        source='size',
        write_only=True
    )
    size_name = serializers.CharField(source='size.name', read_only=True)

    class Meta:
        model = ProductSize
        fields = ['id', 'size', 'size_id', 'size_name', 'stock']

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class SellerSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number']


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    discount_percent = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'price', 'old_price',
            'main_image', 'color', 'total_stock', 'is_in_stock', 'is_new', 'is_bestseller',
            'is_recommended', 'discount_percent', 'views_count'
        ]

    def get_discount_percent(self, obj):
        if obj.old_price and obj.old_price > obj.price:
            return round((1 - float(obj.price) / float(obj.old_price)) * 100)
        return 0

    def get_is_in_stock(self, obj):
        if obj.category and obj.category.requires_size:
            total = obj.product_sizes.aggregate(total=Sum('stock'))['total']
            return (total or 0) > 0
        else:
            if hasattr(obj, 'stock') and obj.stock is not None:
                return obj.stock > 0
            return True

    def get_total_stock(self, obj):
        if obj.category and obj.category.requires_size:
            return obj.product_sizes.aggregate(total=Sum('stock'))['total'] or 0
        else:
            return getattr(obj, 'stock', 0) or 0


class ProductDetailSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    seller = SellerSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    product_sizes = ProductSizeSerializer(many=True, read_only=True)
    discount_percent = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'category_id',
            'seller', 'price', 'old_price', 'main_image', 'images',
            'color', 'total_stock', 'is_in_stock', 'product_sizes',
            'is_new', 'is_bestseller', 'is_recommended', 'discount_percent',
            'views_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'seller', 'views_count', 'created_at', 'updated_at']

    def get_discount_percent(self, obj):
        if obj.old_price and obj.old_price > obj.price:
            return round((1 - float(obj.price) / float(obj.old_price)) * 100)
        return 0

    def get_is_in_stock(self, obj):
        if obj.category and obj.category.requires_size:
            total = obj.product_sizes.aggregate(total=Sum('stock'))['total']
            return (total or 0) > 0
        else:
            if hasattr(obj, 'stock') and obj.stock is not None:
                return obj.stock > 0
            return True

    def get_total_stock(self, obj):
        if obj.category and obj.category.requires_size:
            return obj.product_sizes.aggregate(total=Sum('stock'))['total'] or 0
        else:
            return getattr(obj, 'stock', 0) or 0

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'price', 'old_price',
            'main_image', 'color', 'stock', 'is_new', 'is_bestseller', 'is_recommended'
        ]
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True, 'default': ''},
            'color': {'required': False, 'allow_blank': True, 'default': ''},
            'old_price': {'required': False, 'allow_null': True},
            'main_image': {'required': False, 'allow_null': True},
            'stock': {'required': False, 'default': 0},
            'is_new': {'required': False, 'default': True},
            'is_bestseller': {'required': False, 'default': False},
            'is_recommended': {'required': False, 'default': False},
        }

    def to_internal_value(self, data):
        if hasattr(data, 'getlist'):
            new_data = {}
            for key in data.keys():
                values = data.getlist(key)
                if key == 'main_image':
                    new_data[key] = values[0] if values else None
                elif len(values) == 1:
                    new_data[key] = values[0]
                else:
                    new_data[key] = values
            data = new_data
        else:
            data = data.copy() if hasattr(data, 'copy') else dict(data)

        bool_fields = ['is_new', 'is_bestseller', 'is_recommended']
        for field in bool_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    data[field] = value.lower() in ('true', '1', 'yes')

        self._sizes_data = data.pop('sizes', None)

        return super().to_internal_value(data)

    def create(self, validated_data):
        import json

        validated_data['seller'] = self.context['request'].user

        product = Product.objects.create(**validated_data)

        if not product.slug:
            product.slug = generate_unique_slug(product.name, Product)
            product.save(update_fields=['slug'])

        sizes_raw = getattr(self, '_sizes_data', None)
        if sizes_raw:
            try:
                sizes_data = json.loads(sizes_raw) if isinstance(sizes_raw, str) else sizes_raw
                total_stock = 0
                for size_data in sizes_data:
                    size_id = size_data.get('size_id')
                    stock = int(size_data.get('stock', 0))
                    if size_id:
                        ProductSize.objects.create(
                            product=product,
                            size_id=size_id,
                            stock=stock
                        )
                        total_stock += stock

                if product.category and product.category.requires_size:
                    product.stock = total_stock
                    product.save(update_fields=['stock'])
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error parsing sizes: {e}")

        return product


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    product_size = ProductSizeSerializer(read_only=True)
    product_size_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductSize.objects.all(),
        source='product_size',
        write_only=True,
        required=False,
        allow_null=True
    )
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'product_size',
            'product_size_id', 'quantity', 'total_price', 'added_at'
        ]
        read_only_fields = ['id', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'session_key', 'items', 'total_items', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['id', 'session_key', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_size_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError('Product not found')
        return value

    def validate_product_size_id(self, value):
        if value and not ProductSize.objects.filter(id=value).exists():
            raise serializers.ValidationError('Size not found')
        return value