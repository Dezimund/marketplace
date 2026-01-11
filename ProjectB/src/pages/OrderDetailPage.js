import React, { useState, useEffect, useContext } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../services/api';

const OrderDetailPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { isAuthenticated } = useContext(AuthContext);
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/login?next=/orders/' + id);
            return;
        }
        fetchOrder();
    }, [id, isAuthenticated, navigate]);

    const fetchOrder = async () => {
        try {
            setLoading(true);
            const response = await api.get(`/orders/${id}/`);
            setOrder(response.data);
        } catch (err) {
            setError('Замовлення не знайдено');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (status) => {
        const statusMap = {
            'pending': { class: 'bg-warning text-dark', text: 'Очікує' },
            'processing': { class: 'bg-info', text: 'Обробляється' },
            'shipped': { class: 'bg-primary', text: 'Відправлено' },
            'delivered': { class: 'bg-success', text: 'Доставлено' },
            'cancelled': { class: 'bg-danger', text: 'Скасовано' },
        };
        const badge = statusMap[status] || { class: 'bg-secondary', text: status };
        return <span className={`badge fs-6 ${badge.class}`}>{badge.text}</span>;
    };

    const getPaymentDisplay = (provider) => {
        const map = {
            'visa': 'Visa',
            'mastercard': 'Mastercard',
            'privat24': 'Приват24',
        };
        return map[provider] || provider || 'Не вказано';
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

    if (error || !order) {
        return (
            <div className="container py-5 text-center">
                <div className="alert alert-danger">{error || 'Замовлення не знайдено'}</div>
                <Link to="/orders" className="btn btn-outline-dark">
                    До списку замовлень
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
                        <Link to="/orders">Мої замовлення</Link>
                    </li>
                    <li className="breadcrumb-item active">Замовлення #{order.id}</li>
                </ol>
            </nav>

            <div className="row g-4">
                <div className="col-lg-8">
                    <div className="card border-0 shadow-sm mb-4">
                        <div className="card-header bg-white py-3">
                            <div className="d-flex justify-content-between align-items-center">
                                <h4 className="mb-0 fw-bold">Замовлення #{order.id}</h4>
                                {getStatusBadge(order.status)}
                            </div>
                        </div>
                        <div className="card-body p-4">
                            <h5 className="fw-bold mb-3">Товари</h5>

                            <div className="vstack gap-3">
                                {order.items?.map((item, index) => (
                                    <div key={index} className="d-flex align-items-center p-3 bg-light rounded">
                                        <div className="me-3">
                                            {item.product?.main_image ? (
                                                <img
                                                    src={item.product.main_image}
                                                    alt={item.product.name}
                                                    className="rounded"
                                                    style={{ width: '80px', height: '80px', objectFit: 'cover' }}
                                                />
                                            ) : (
                                                <div
                                                    className="rounded bg-secondary d-flex align-items-center justify-content-center"
                                                    style={{ width: '80px', height: '80px' }}
                                                >
                                                    <i className="bi bi-image text-white"></i>
                                                </div>
                                            )}
                                        </div>

                                        <div className="flex-grow-1">
                                            <h6 className="mb-1">
                                                <Link
                                                    to={`/product/${item.product?.slug}`}
                                                    className="text-decoration-none text-dark"
                                                >
                                                    {item.product?.name}
                                                </Link>
                                            </h6>
                                            {item.size && (
                                                <p className="text-muted small mb-1">
                                                    Розмір: {item.size.size?.name}
                                                </p>
                                            )}
                                            <p className="text-muted small mb-0">
                                                Кількість: {item.quantity}
                                            </p>
                                        </div>

                                        <div className="text-end">
                                            <p className="fw-bold mb-0">
                                                {(item.price * item.quantity).toFixed(2)} ₴
                                            </p>
                                            <p className="text-muted small mb-0">
                                                {item.price} ₴ × {item.quantity}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="col-lg-4">
                    <div className="card border-0 shadow-sm mb-4">
                        <div className="card-header bg-white py-3">
                            <h5 className="mb-0 fw-bold">Інформація</h5>
                        </div>
                        <div className="card-body p-4">
                            <div className="mb-3">
                                <p className="text-muted small mb-1">Дата замовлення</p>
                                <p className="fw-medium mb-0">
                                    {new Date(order.created_at).toLocaleString('uk-UA')}
                                </p>
                            </div>

                            <div className="mb-3">
                                <p className="text-muted small mb-1">Спосіб оплати</p>
                                <p className="fw-medium mb-0">
                                    {getPaymentDisplay(order.payment_provider)}
                                </p>
                            </div>

                            <hr />

                            <div className="mb-3">
                                <p className="text-muted small mb-1">Отримувач</p>
                                <p className="fw-medium mb-0">
                                    {order.first_name} {order.last_name}
                                </p>
                            </div>

                            <div className="mb-3">
                                <p className="text-muted small mb-1">Email</p>
                                <p className="fw-medium mb-0">{order.email}</p>
                            </div>

                            <div className="mb-3">
                                <p className="text-muted small mb-1">Телефон</p>
                                <p className="fw-medium mb-0">{order.phone_number || '-'}</p>
                            </div>

                            <div className="mb-3">
                                <p className="text-muted small mb-1">Адреса доставки</p>
                                <p className="fw-medium mb-0">
                                    {order.country && `${order.country}, `}
                                    {order.city && `${order.city}, `}
                                    {order.address1}
                                    {order.address2 && `, ${order.address2}`}
                                    {order.postal_code && `, ${order.postal_code}`}
                                </p>
                            </div>

                            <hr />

                            <div className="d-flex justify-content-between align-items-center">
                                <span className="h5 mb-0">Разом:</span>
                                <span className="h4 mb-0 text-success fw-bold">
                                    {order.total_price} ₴
                                </span>
                            </div>
                        </div>
                    </div>

                    <Link
                        to="/orders"
                        className="btn btn-outline-dark w-100"
                    >
                        <i className="bi bi-arrow-left me-2"></i>
                        До списку замовлень
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default OrderDetailPage;