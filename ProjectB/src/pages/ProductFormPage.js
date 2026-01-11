import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../services/api';

const ProductFormPage = () => {
    const { slug } = useParams();
    const navigate = useNavigate();
    const { user, isAuthenticated } = useContext(AuthContext);
    const isEdit = Boolean(slug);
    
    const [formData, setFormData] = useState({
        name: '',
        category: '',
        price: '',
        old_price: '',
        description: '',
        color: '',
        stock: '0',
        is_recommended: false,
    });
    
    const [categories, setCategories] = useState([]);
    const [sizes, setSizes] = useState([]);
    const [productSizes, setProductSizes] = useState([]);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [errors, setErrors] = useState({});
    const [mainImage, setMainImage] = useState(null);

    // Перевірка чи обрана категорія потребує розмірів
    const selectedCategory = categories.find(c => c.id === parseInt(formData.category));
    const requiresSize = selectedCategory?.requires_size || false;

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/login?next=/my-products/create');
            return;
        }
        
        if (user && !user.is_seller) {
            navigate('/profile');
            return;
        }
        
        fetchCategories();
        fetchSizes();
        
        if (isEdit) {
            fetchProduct();
        }
    }, [isAuthenticated, user, slug, navigate]);

    const fetchCategories = async () => {
        try {
            const response = await api.get('/categories/');
            setCategories(response.data || []);
        } catch (err) {
            console.error('Помилка завантаження категорій:', err);
        }
    };

    const fetchSizes = async () => {
        try {
            const response = await api.get('/sizes/');
            setSizes(response.data || []);
        } catch (err) {
            console.error('Помилка завантаження розмірів:', err);
        }
    };

    const fetchProduct = async () => {
        try {
            setLoading(true);
            const response = await api.get(`/products/${slug}/`);
            const product = response.data;
            setFormData({
                name: product.name || '',
                category: product.category?.id || product.category || '',
                price: product.price || '',
                old_price: product.old_price || '',
                description: product.description || '',
                color: product.color || '',
                stock: product.total_stock || '0',
                is_recommended: product.is_recommended || false,
            });
            
            // Завантажуємо розміри товару
            if (product.product_sizes && product.product_sizes.length > 0) {
                setProductSizes(product.product_sizes.map(ps => ({
                    size_id: ps.size?.id || ps.size_id,
                    size_name: ps.size?.name || ps.size_name,
                    stock: ps.stock || 0
                })));
            }
        } catch (err) {
            console.error('Помилка завантаження товару:', err);
            navigate('/my-products');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: null }));
        }
    };

    const handleImageChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setMainImage(e.target.files[0]);
        }
    };

    // Управління розмірами
    const handleAddSize = () => {
        setProductSizes([...productSizes, { size_id: '', size_name: '', stock: 0 }]);
    };

    const handleRemoveSize = (index) => {
        setProductSizes(productSizes.filter((_, i) => i !== index));
    };

    const handleSizeChange = (index, field, value) => {
        const newSizes = [...productSizes];
        if (field === 'size_id') {
            const selectedSize = sizes.find(s => s.id === parseInt(value));
            newSizes[index] = {
                ...newSizes[index],
                size_id: value,
                size_name: selectedSize?.name || ''
            };
        } else {
            newSizes[index] = {
                ...newSizes[index],
                [field]: field === 'stock' ? parseInt(value) || 0 : value
            };
        }
        setProductSizes(newSizes);
    };

    // Підрахунок загальної кількості
    const totalStock = requiresSize 
        ? productSizes.reduce((sum, ps) => sum + (parseInt(ps.stock) || 0), 0)
        : parseInt(formData.stock) || 0;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setErrors({});

        try {
            const data = new FormData();
            data.append('name', formData.name);
            data.append('category', formData.category);
            data.append('price', formData.price);
            if (formData.old_price) data.append('old_price', formData.old_price);
            if (formData.description) data.append('description', formData.description);
            if (formData.color) data.append('color', formData.color);
            
            // Для товарів без розмірів - відправляємо stock
            if (!requiresSize) {
                data.append('stock', formData.stock || '0');
            }
            
            data.append('is_recommended', formData.is_recommended);
            
            if (mainImage) {
                data.append('main_image', mainImage);
            }

            // Для товарів з розмірами - відправляємо sizes як JSON
            if (requiresSize && productSizes.length > 0) {
                data.append('sizes', JSON.stringify(productSizes.filter(ps => ps.size_id)));
            }

            if (isEdit) {
                await api.patch(`/products/${slug}/`, data, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
            } else {
                await api.post('/products/', data, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
            }

            navigate('/my-products');
        } catch (err) {
            console.error('Error:', err.response?.data);
            if (err.response?.data) {
                setErrors(err.response.data);
            } else {
                setErrors({ general: 'Помилка збереження товару' });
            }
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="container py-5 text-center">
                <div className="spinner-border text-success" role="status">
                    <span className="visually-hidden">Завантаження...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="row">
            <div className="col-lg-8">
                <div className="bg-white rounded-4 p-4 shadow-sm">
                    <h4 className="fw-bold mb-4">
                        <i className={`bi bi-${isEdit ? 'pencil' : 'plus-circle'} text-success me-2`}></i>
                        {isEdit ? 'Редагувати товар' : 'Додати новий товар'}
                    </h4>

                    {errors.general && (
                        <div className="alert alert-danger">{errors.general}</div>
                    )}
                    {errors.detail && (
                        <div className="alert alert-danger">{errors.detail}</div>
                    )}

                    <form onSubmit={handleSubmit}>
                        {/* Основна інформація */}
                        <div className="mb-4">
                            <h6 className="fw-bold text-muted mb-3">
                                <i className="bi bi-info-circle me-1"></i>Основна інформація
                            </h6>
                            
                            <div className="mb-3">
                                <label className="form-label">Назва товару *</label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    className={`form-control ${errors.name ? 'is-invalid' : ''}`}
                                    required
                                />
                                {errors.name && (
                                    <div className="invalid-feedback">{errors.name}</div>
                                )}
                            </div>

                            <div className="row mb-3">
                                <div className="col-md-6">
                                    <label className="form-label">Категорія *</label>
                                    <select
                                        name="category"
                                        value={formData.category}
                                        onChange={handleChange}
                                        className={`form-select ${errors.category ? 'is-invalid' : ''}`}
                                        required
                                    >
                                        <option value="">Оберіть категорію</option>
                                        {categories.map(cat => (
                                            <option key={cat.id} value={cat.id}>
                                                {cat.name} {cat.requires_size ? '(з розмірами)' : ''}
                                            </option>
                                        ))}
                                    </select>
                                    {errors.category && (
                                        <div className="invalid-feedback">{errors.category}</div>
                                    )}
                                </div>
                                <div className="col-md-3">
                                    <label className="form-label">Ціна (₴) *</label>
                                    <input
                                        type="number"
                                        name="price"
                                        value={formData.price}
                                        onChange={handleChange}
                                        className={`form-control ${errors.price ? 'is-invalid' : ''}`}
                                        min="0"
                                        step="0.01"
                                        required
                                    />
                                    {errors.price && (
                                        <div className="invalid-feedback">{errors.price}</div>
                                    )}
                                </div>
                                <div className="col-md-3">
                                    <label className="form-label">Стара ціна (₴)</label>
                                    <input
                                        type="number"
                                        name="old_price"
                                        value={formData.old_price}
                                        onChange={handleChange}
                                        className="form-control"
                                        min="0"
                                        step="0.01"
                                    />
                                </div>
                            </div>

                            <div className="mb-3">
                                <label className="form-label">Опис товару</label>
                                <textarea
                                    name="description"
                                    value={formData.description}
                                    onChange={handleChange}
                                    className="form-control"
                                    rows="4"
                                />
                            </div>
                        </div>

                        {/* Характеристики */}
                        <div className="mb-4">
                            <h6 className="fw-bold text-muted mb-3">
                                <i className="bi bi-list-check me-1"></i>Характеристики
                            </h6>
                            
                            <div className="row">
                                <div className="col-md-6 mb-3">
                                    <label className="form-label">Колір</label>
                                    <input
                                        type="text"
                                        name="color"
                                        value={formData.color}
                                        onChange={handleChange}
                                        className="form-control"
                                        placeholder="Наприклад: Чорний, Білий"
                                    />
                                </div>
                                
                                {/* Кількість для товарів БЕЗ розмірів */}
                                {!requiresSize && (
                                    <div className="col-md-6 mb-3">
                                        <label className="form-label">Кількість в наявності *</label>
                                        <input
                                            type="number"
                                            name="stock"
                                            value={formData.stock}
                                            onChange={handleChange}
                                            className={`form-control ${errors.stock ? 'is-invalid' : ''}`}
                                            min="0"
                                            required
                                        />
                                        {errors.stock && (
                                            <div className="invalid-feedback">{errors.stock}</div>
                                        )}
                                        <div className="form-text">0 = немає в наявності</div>
                                    </div>
                                )}
                            </div>

                            <div className="form-check mb-3">
                                <input
                                    type="checkbox"
                                    name="is_recommended"
                                    checked={formData.is_recommended}
                                    onChange={handleChange}
                                    className="form-check-input"
                                    id="is_recommended"
                                />
                                <label className="form-check-label" htmlFor="is_recommended">
                                    Рекомендований товар
                                </label>
                            </div>
                        </div>

                        {/* Розміри - тільки для категорій з requires_size */}
                        {requiresSize && (
                            <div className="mb-4">
                                <h6 className="fw-bold text-muted mb-3">
                                    <i className="bi bi-rulers me-1"></i>Розміри та кількість
                                </h6>
                                
                                <div className="alert alert-info small">
                                    <i className="bi bi-info-circle me-1"></i>
                                    Для цієї категорії потрібно вказати розміри та кількість для кожного розміру.
                                </div>

                                {productSizes.map((ps, index) => (
                                    <div key={index} className="row mb-2 align-items-center">
                                        <div className="col-md-5">
                                            <select
                                                value={ps.size_id}
                                                onChange={(e) => handleSizeChange(index, 'size_id', e.target.value)}
                                                className="form-select"
                                            >
                                                <option value="">Оберіть розмір</option>
                                                {sizes.map(size => (
                                                    <option 
                                                        key={size.id} 
                                                        value={size.id}
                                                        disabled={productSizes.some((p, i) => i !== index && p.size_id === String(size.id))}
                                                    >
                                                        {size.name}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                        <div className="col-md-4">
                                            <input
                                                type="number"
                                                value={ps.stock}
                                                onChange={(e) => handleSizeChange(index, 'stock', e.target.value)}
                                                className="form-control"
                                                placeholder="Кількість"
                                                min="0"
                                            />
                                        </div>
                                        <div className="col-md-3">
                                            <button
                                                type="button"
                                                className="btn btn-outline-danger"
                                                onClick={() => handleRemoveSize(index)}
                                            >
                                                <i className="bi bi-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                ))}

                                <button
                                    type="button"
                                    className="btn btn-outline-success"
                                    onClick={handleAddSize}
                                >
                                    <i className="bi bi-plus-lg me-1"></i>Додати розмір
                                </button>

                                <div className="mt-3 p-3 bg-light rounded">
                                    <strong>Загальна кількість: {totalStock} шт</strong>
                                </div>
                            </div>
                        )}

                        {/* Зображення */}
                        <div className="mb-4">
                            <h6 className="fw-bold text-muted mb-3">
                                <i className="bi bi-images me-1"></i>Зображення
                            </h6>
                            
                            <div className="mb-3">
                                <label className="form-label">Головне зображення</label>
                                <input
                                    type="file"
                                    onChange={handleImageChange}
                                    className="form-control"
                                    accept="image/*"
                                />
                                <div className="form-text">Рекомендований розмір: 800x800 пікселів</div>
                            </div>
                        </div>

                        {/* Кнопки */}
                        <div className="d-flex gap-3">
                            <button 
                                type="submit" 
                                className="btn btn-success btn-lg px-5"
                                disabled={saving}
                            >
                                {saving ? (
                                    <>
                                        <span className="spinner-border spinner-border-sm me-2"></span>
                                        Збереження...
                                    </>
                                ) : (
                                    <>
                                        <i className="bi bi-check-lg me-2"></i>
                                        {isEdit ? 'Зберегти зміни' : 'Створити товар'}
                                    </>
                                )}
                            </button>
                            <Link to="/my-products" className="btn btn-outline-secondary btn-lg">
                                Скасувати
                            </Link>
                        </div>
                    </form>
                </div>
            </div>

            {/* Sidebar */}
            <div className="col-lg-4">
                <div className="bg-white rounded-4 p-4 shadow-sm sticky-top" style={{ top: '100px' }}>
                    <h6 className="fw-bold mb-3">
                        <i className="bi bi-lightbulb text-warning me-2"></i>Поради
                    </h6>
                    <ul className="list-unstyled text-muted small">
                        <li className="mb-2">
                            <i className="bi bi-check-circle text-success me-1"></i>
                            Використовуйте чіткі та якісні фото товару
                        </li>
                        <li className="mb-2">
                            <i className="bi bi-check-circle text-success me-1"></i>
                            Детальний опис підвищує довіру покупців
                        </li>
                        <li className="mb-2">
                            <i className="bi bi-check-circle text-success me-1"></i>
                            Конкурентна ціна привертає більше покупців
                        </li>
                        <li>
                            <i className="bi bi-check-circle text-success me-1"></i>
                            Стара ціна показує знижку покупцям
                        </li>
                    </ul>

                    <hr />

                    {requiresSize && (
                        <div className="alert alert-warning small mb-3">
                            <i className="bi bi-exclamation-triangle me-1"></i>
                            Не забудьте додати розміри для товару!
                        </div>
                    )}

                    <div className="alert alert-info small mb-0">
                        <i className="bi bi-info-circle me-1"></i>
                        Товар з'явиться в каталозі одразу після створення.
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProductFormPage;