import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../services/api';

const OrdersPage = () => {
    const navigate = useNavigate();
    const { isAuthenticated } = useContext(AuthContext);
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/login?next=/orders');
            return;
        }
        fetchOrders();
    }, [isAuthenticated, navigate]);

    const fetchOrders = async () => {
        try {
            setLoading(true);
            const response = await api.get('/orders/');
            setOrders(response.data.results || response.data || []);
        } catch (err) {
            setError('Помилка завантаження замовлень');
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
        return <span className={`badge ${badge.class}`}>{badge.text}</span>;
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
        <div className="container py-5">
            <nav aria-label="breadcrumb" className="mb-4">
                <ol className="breadcrumb">
                    <li className="breadcrumb-item">
                        <Link to="/">Головна</Link>
                    </li>
                    <li className="breadcrumb-item active">Мої замовлення</li>
                </ol>
            </nav>

            <h2 className="fw-bold mb-4">Мої замовлення</h2>

            {error && (
                <div className="alert alert-danger">{error}</div>
            )}

            {orders.length > 0 ? (
                <div className="row g-4">
                    {orders.map((order) => (
                        <div key={order.id} className="col-12">
                            <div className="card border-0 shadow-sm">
                                <div className="card-body p-4">
                                    <div className="d-flex justify-content-between align-items-start flex-wrap gap-3">
                                        <div>
                                            <h5 className="fw-bold mb-2">
                                                Замовлення #{order.id}
                                            </h5>
                                            <p className="text-muted mb-2">
                                                <i className="bi bi-calendar me-1"></i>
                                                {new Date(order.created_at).toLocaleString('uk-UA')}
                                            </p>
                                            <p className="mb-0">
                                                {getStatusBadge(order.status)}
                                            </p>
                                        </div>

                                        <div className="text-end">
                                            <p className="h4 fw-bold text-success mb-2">
                                                {order.total_price} ₴
                                            </p>
                                            <p className="text-muted small mb-0">
                                                {order.items_count || order.items?.length || 0} товар(ів)
                                            </p>
                                        </div>
                                    </div>

                                    <hr className="my-3" />

                                    <div className="d-flex justify-content-between align-items-center flex-wrap gap-2">
                                        <div className="text-muted small">
                                            <i className="bi bi-geo-alt me-1"></i>
                                            {order.city && `${order.city}`}
                                            {order.address1 && `, ${order.address1}`}
                                        </div>

                                        <Link
                                            to={`/orders/${order.id}`}
                                            className="btn btn-outline-dark btn-sm"
                                        >
                                            <i className="bi bi-eye me-1"></i>
                                            Деталі
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="text-center py-5">
                    <div className="mb-4">
                        <i className="bi bi-bag-x text-muted" style={{ fontSize: '80px' }}></i>
                    </div>
                    <h4 className="text-muted mb-4">У вас ще немає замовлень</h4>
                    <Link to="/" className="btn btn-success btn-lg">
                        <i className="bi bi-cart me-2"></i>
                        Почати покупки
                    </Link>
                </div>
            )}
        </div>
    );
};

export default OrdersPage;