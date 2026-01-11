import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api, { getImageUrl } from '../services/api';

const MyProductsPage = () => {
    const navigate = useNavigate();
    const { user, isAuthenticated } = useContext(AuthContext);
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/login?next=/my-products');
            return;
        }

        if (user && !user.is_seller) {
            navigate('/profile');
            return;
        }

        if (user?.id) {
            fetchProducts();
        }
    }, [isAuthenticated, user, navigate]);

    const fetchProducts = async () => {
        try {
            setLoading(true);
            const response = await api.get(`/users/${user.id}/products/`);
            setProducts(response.data || []);
        } catch (err) {
            setError('Помилка завантаження товарів');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (slug, name) => {
        if (!window.confirm(`Видалити товар "${name}"?`)) {
            return;
        }

        try {
            await api.delete(`/products/${slug}/`);
            setProducts(products.filter(p => p.slug !== slug));
        } catch (err) {
            alert('Помилка видалення товару');
            console.error(err);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return '-';
            return date.toLocaleDateString('uk-UA');
        } catch {
            return '-';
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
        <div className="bg-white rounded-4 p-4 shadow-sm">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h4 className="fw-bold mb-0">
                    <i className="bi bi-shop text-success me-2"></i>
                    Мої товари
                    <span className="badge bg-success-subtle text-success ms-2">
                        {products.length}
                    </span>
                </h4>
                <Link to="/my-products/create" className="btn btn-success">
                    <i className="bi bi-plus-lg me-2"></i>Додати товар
                </Link>
            </div>

            {error && (
                <div className="alert alert-danger">{error}</div>
            )}

            {products.length > 0 ? (
                <div className="table-responsive">
                    <table className="table table-hover align-middle">
                        <thead className="table-light">
                            <tr>
                                <th style={{ width: '60px' }}></th>
                                <th>Товар</th>
                                <th>Категорія</th>
                                <th>Ціна</th>
                                <th>Статус</th>
                                <th className="text-center">Перегляди</th>
                                <th style={{ width: '120px' }}>Дії</th>
                            </tr>
                        </thead>
                        <tbody>
                            {products.map((product) => (
                                <tr key={product.id}>
                                    <td>
                                        {product.main_image ? (
                                            <img
                                                src={getImageUrl(product.main_image)}
                                                alt={product.name}
                                                className="rounded"
                                                style={{ width: '50px', height: '50px', objectFit: 'cover' }}
                                                onError={(e) => {
                                                    e.target.style.display = 'none';
                                                    e.target.nextSibling.style.display = 'flex';
                                                }}
                                            />
                                        ) : null}
                                        <div
                                            className="rounded bg-light align-items-center justify-content-center"
                                            style={{
                                                width: '50px',
                                                height: '50px',
                                                display: product.main_image ? 'none' : 'flex'
                                            }}
                                        >
                                            <i className="bi bi-image text-muted"></i>
                                        </div>
                                    </td>
                                    <td>
                                        <div>
                                            <Link
                                                to={`/product/${product.slug}`}
                                                className="fw-medium text-decoration-none text-dark"
                                            >
                                                {product.name}
                                            </Link>
                                            {product.old_price && (
                                                <span className="badge bg-danger ms-1">
                                                    -{product.discount_percent || Math.round((1 - product.price / product.old_price) * 100)}%
                                                </span>
                                            )}
                                        </div>
                                        <small className="text-muted">
                                            {formatDate(product.created_at)}
                                        </small>
                                    </td>
                                    <td>
                                        <span className="badge bg-secondary-subtle text-secondary">
                                            {product.category?.name || product.category_name || '-'}
                                        </span>
                                    </td>
                                    <td>
                                        <span className="fw-bold text-success">
                                            {product.price} ₴
                                        </span>
                                        {product.old_price && (
                                            <>
                                                <br />
                                                <small className="text-muted text-decoration-line-through">
                                                    {product.old_price} ₴
                                                </small>
                                            </>
                                        )}
                                    </td>
                                    <td>
                                        {product.is_available !== false ? (
                                            <span className="badge bg-success">В наявності</span>
                                        ) : (
                                            <span className="badge bg-secondary">Немає</span>
                                        )}
                                    </td>
                                    <td className="text-center">
                                        <span className="text-muted">
                                            <i className="bi bi-eye me-1"></i>
                                            {product.views_count || 0}
                                        </span>
                                    </td>
                                    <td>
                                        <div className="btn-group">
                                            <Link
                                                to={`/my-products/${product.slug}/edit`}
                                                className="btn btn-sm btn-outline-primary"
                                                title="Редагувати"
                                            >
                                                <i className="bi bi-pencil"></i>
                                            </Link>
                                            <button
                                                type="button"
                                                className="btn btn-sm btn-outline-danger"
                                                onClick={() => handleDelete(product.slug, product.name)}
                                                title="Видалити"
                                            >
                                                <i className="bi bi-trash"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div className="text-center py-5">
                    <div className="mb-4">
                        <i className="bi bi-box text-muted" style={{ fontSize: '80px' }}></i>
                    </div>
                    <h5 className="text-muted mb-3">У вас ще немає товарів</h5>
                    <p className="text-muted mb-4">Почніть продавати, додавши свій перший товар!</p>
                    <Link to="/my-products/create" className="btn btn-success btn-lg">
                        <i className="bi bi-plus-lg me-2"></i>Додати перший товар
                    </Link>
                </div>
            )}
        </div>
    );
};

export default MyProductsPage;