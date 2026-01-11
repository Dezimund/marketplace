import React, { useState, useEffect, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { CartContext } from '../context/CartContext';
import api, { getImageUrl } from '../services/api';

const CheckoutPage = () => {
    const navigate = useNavigate();
    const { user, isAuthenticated } = useContext(AuthContext);
    const { cart, clearCart } = useContext(CartContext);

    const cartItems = cart?.items || [];

    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        phone_number: '',
        country: 'Україна',
        city: '',
        address1: '',
        address2: '',
        state: '',
        postal_code: '',
        company: '',
    });

    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/login?next=/checkout');
            return;
        }

        if (user) {
            setFormData(prev => ({
                ...prev,
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                email: user.email || '',
                phone_number: user.phone_number || '',
                city: user.city || '',
                address1: user.address1 || '',
            }));
        }
    }, [user, isAuthenticated, navigate]);

    useEffect(() => {
        if (cartItems.length === 0 && !loading) {
            navigate('/cart');
        }
    }, [cartItems, loading, navigate]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: null }));
        }
    };

    const calculateTotal = () => {
        return cartItems.reduce((sum, item) => {
            const price = parseFloat(item.product?.price) || 0;
            return sum + price * item.quantity;
        }, 0);
    };

    const handleSubmit = async (paymentProvider) => {
        setLoading(true);
        setErrors({});

        try {
            const response = await api.post('/orders/checkout/', {
                ...formData,
                payment_provider: paymentProvider,
            });

            if (response.data.order_id) {
                clearCart();
                navigate(`/orders/${response.data.order_id}/success`);
            }
        } catch (error) {
            if (error.response?.data) {
                setErrors(error.response.data);
            } else {
                setErrors({ general: 'Помилка при оформленні замовлення' });
            }
        } finally {
            setLoading(false);
        }
    };

    if (cartItems.length === 0) {
        return (
            <div className="container py-5 text-center">
                <i className="bi bi-cart-x text-muted" style={{ fontSize: '80px' }}></i>
                <h3 className="mt-4">Кошик порожній</h3>
                <Link to="/" className="btn btn-success mt-3">
                    Продовжити покупки
                </Link>
            </div>
        );
    }

    return (
        <div className="container py-5">
            <nav aria-label="breadcrumb" className="mb-4">
                <ol className="breadcrumb">
                    <li className="breadcrumb-item">
                        <Link to="/">Головна</Link>
                    </li>
                    <li className="breadcrumb-item">
                        <Link to="/cart">Кошик</Link>
                    </li>
                    <li className="breadcrumb-item active">Оформлення</li>
                </ol>
            </nav>

            <div className="row g-5">
                <div className="col-lg-7">
                    <div className="card border-0 shadow-sm">
                        <div className="card-body p-4">
                            <h4 className="fw-bold mb-4">Контактна інформація</h4>

                            {errors.general && (
                                <div className="alert alert-danger">{errors.general}</div>
                            )}
                            {errors.error && (
                                <div className="alert alert-danger">{errors.error}</div>
                            )}

                            <form>
                                <div className="mb-3">
                                    <label className="form-label">Email</label>
                                    <input
                                        type="email"
                                        name="email"
                                        value={formData.email}
                                        className="form-control"
                                        readOnly
                                    />
                                </div>

                                <hr className="my-4" />

                                <h5 className="fw-bold mb-3">Адреса доставки</h5>

                                <div className="row g-3">
                                    <div className="col-md-6">
                                        <label className="form-label">Ім'я *</label>
                                        <input
                                            type="text"
                                            name="first_name"
                                            value={formData.first_name}
                                            onChange={handleChange}
                                            className={`form-control ${errors.first_name ? 'is-invalid' : ''}`}
                                            required
                                        />
                                        {errors.first_name && (
                                            <div className="invalid-feedback">{errors.first_name}</div>
                                        )}
                                    </div>
                                    <div className="col-md-6">
                                        <label className="form-label">Прізвище *</label>
                                        <input
                                            type="text"
                                            name="last_name"
                                            value={formData.last_name}
                                            onChange={handleChange}
                                            className={`form-control ${errors.last_name ? 'is-invalid' : ''}`}
                                            required
                                        />
                                        {errors.last_name && (
                                            <div className="invalid-feedback">{errors.last_name}</div>
                                        )}
                                    </div>
                                </div>

                                <div className="mb-3 mt-3">
                                    <label className="form-label">Телефон</label>
                                    <input
                                        type="tel"
                                        name="phone_number"
                                        value={formData.phone_number}
                                        onChange={handleChange}
                                        className="form-control"
                                        placeholder="+380 XX XXX XX XX"
                                    />
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">Країна</label>
                                    <input
                                        type="text"
                                        name="country"
                                        value={formData.country}
                                        onChange={handleChange}
                                        className="form-control"
                                    />
                                </div>

                                <div className="row g-3">
                                    <div className="col-md-6">
                                        <label className="form-label">Місто</label>
                                        <input
                                            type="text"
                                            name="city"
                                            value={formData.city}
                                            onChange={handleChange}
                                            className="form-control"
                                        />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="form-label">Область</label>
                                        <input
                                            type="text"
                                            name="state"
                                            value={formData.state}
                                            onChange={handleChange}
                                            className="form-control"
                                        />
                                    </div>
                                </div>

                                <div className="mb-3 mt-3">
                                    <label className="form-label">Адреса</label>
                                    <input
                                        type="text"
                                        name="address1"
                                        value={formData.address1}
                                        onChange={handleChange}
                                        className="form-control"
                                        placeholder="Вулиця, будинок"
                                    />
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">Квартира, офіс</label>
                                    <input
                                        type="text"
                                        name="address2"
                                        value={formData.address2}
                                        onChange={handleChange}
                                        className="form-control"
                                        placeholder="Опціонально"
                                    />
                                </div>

                                <div className="mb-3">
                                    <label className="form-label">Поштовий індекс</label>
                                    <input
                                        type="text"
                                        name="postal_code"
                                        value={formData.postal_code}
                                        onChange={handleChange}
                                        className="form-control"
                                    />
                                </div>

                                <hr className="my-4" />

                                <h5 className="fw-bold mb-3">Спосіб оплати</h5>

                                <div className="row g-3">
                                    <div className="col-6">
                                        <button
                                            type="button"
                                            onClick={() => handleSubmit('visa')}
                                            disabled={loading}
                                            className="btn btn-success w-100 py-3 fw-bold"
                                        >
                                            {loading ? (
                                                <span className="spinner-border spinner-border-sm me-2"></span>
                                            ) : (
                                                <i className="bi bi-credit-card me-2"></i>
                                            )}
                                            Visa/Mastercard
                                        </button>
                                    </div>
                                    <div className="col-6">
                                        <button
                                            type="button"
                                            onClick={() => handleSubmit('privat24')}
                                            disabled={loading}
                                            className="btn btn-warning w-100 py-3 fw-bold text-dark"
                                        >
                                            {loading ? (
                                                <span className="spinner-border spinner-border-sm me-2"></span>
                                            ) : (
                                                <i className="bi bi-bank me-2"></i>
                                            )}
                                            Приват24
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>

                <div className="col-lg-5">
                    <div className="card border-0 shadow-sm sticky-top" style={{ top: '100px' }}>
                        <div className="card-body p-4">
                            <h5 className="fw-bold mb-4">Ваше замовлення</h5>

                            <div className="vstack gap-3 mb-4">
                                {cartItems.map((item, index) => (
                                    <div key={item.id || index} className="d-flex align-items-center">
                                        <div className="position-relative me-3">
                                            {item.product?.main_image ? (
                                                <img
                                                    src={getImageUrl(item.product.main_image)}
                                                    alt={item.product.name}
                                                    className="rounded bg-light"
                                                    style={{ width: '64px', height: '64px', objectFit: 'cover' }}
                                                />
                                            ) : (
                                                <div
                                                    className="rounded bg-light d-flex align-items-center justify-content-center"
                                                    style={{ width: '64px', height: '64px' }}
                                                >
                                                    <i className="bi bi-image text-muted"></i>
                                                </div>
                                            )}
                                            <span
                                                className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-secondary"
                                                style={{ fontSize: '0.75rem' }}
                                            >
                                                {item.quantity}
                                            </span>
                                        </div>

                                        <div className="flex-grow-1">
                                            <h6 className="mb-0 fw-medium">{item.product?.name}</h6>
                                            {item.product_size && (
                                                <small className="text-muted">
                                                    Розмір: {item.product_size.size_name || item.product_size.size?.name}
                                                </small>
                                            )}
                                        </div>

                                        <div className="text-end fw-medium">
                                            {item.product?.price} ₴
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="border-top pt-3">
                                <div className="d-flex justify-content-between mb-2">
                                    <span>Товарів: {cart?.total_items || cartItems.reduce((sum, i) => sum + i.quantity, 0)} шт.</span>
                                    <span>{calculateTotal().toFixed(2)} ₴</span>
                                </div>

                                <div className="d-flex justify-content-between mb-3 small">
                                    <span>Доставка</span>
                                    <span className="text-muted">Розраховується окремо</span>
                                </div>

                                <div className="d-flex justify-content-between align-items-center border-top pt-3">
                                    <span className="h5 mb-0">Разом</span>
                                    <div className="text-end">
                                        <span className="small text-muted me-1">UAH</span>
                                        <span className="h5 mb-0 text-success fw-bold">
                                            {(cart?.subtotal || calculateTotal()).toFixed(2)} ₴
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CheckoutPage;