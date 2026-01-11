import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import api from '../services/api';

const ReviewStars = ({ rating, size = 'normal', interactive = false, onChange }) => {
    const [hoverRating, setHoverRating] = useState(0);
    const stars = [1, 2, 3, 4, 5];
    const sizeClass = size === 'small' ? 'fs-6' : size === 'large' ? 'fs-4' : '';

    return (
        <div className="d-inline-flex">
            {stars.map((star) => (
                <i
                    key={star}
                    className={`bi ${
                        star <= (hoverRating || rating) ? 'bi-star-fill text-warning' : 'bi-star text-muted'
                    } ${sizeClass} ${interactive ? 'cursor-pointer' : ''}`}
                    style={interactive ? { cursor: 'pointer' } : {}}
                    onMouseEnter={() => interactive && setHoverRating(star)}
                    onMouseLeave={() => interactive && setHoverRating(0)}
                    onClick={() => interactive && onChange && onChange(star)}
                />
            ))}
        </div>
    );
};

const ReviewItem = ({ review, onHelpful, currentUserId }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <div className="border-bottom py-4">
            <div className="d-flex justify-content-between align-items-start mb-2">
                <div>
                    <ReviewStars rating={review.rating} size="small" />
                    {review.is_verified_purchase && (
                        <span className="badge bg-success-subtle text-success ms-2">
                            <i className="bi bi-patch-check me-1"></i>
                            Підтверджена покупка
                        </span>
                    )}
                </div>
                <small className="text-muted">
                    {new Date(review.created_at).toLocaleDateString('uk-UA')}
                </small>
            </div>

            <div className="d-flex align-items-center mb-2">
                <div className="rounded-circle bg-secondary text-white d-flex align-items-center justify-content-center me-2"
                     style={{ width: '32px', height: '32px', fontSize: '14px' }}>
                    {review.user?.first_name?.[0] || 'U'}
                </div>
                <span className="fw-medium">
                    {review.user?.first_name || 'Користувач'} {review.user?.last_name || ''}
                </span>
                {review.is_own && (
                    <span className="badge bg-primary-subtle text-primary ms-2">Ваш відгук</span>
                )}
            </div>

            {review.title && (
                <h6 className="fw-bold mb-2">{review.title}</h6>
            )}

            <p className={`mb-2 ${!isExpanded && review.text?.length > 200 ? 'text-truncate' : ''}`}
               style={!isExpanded && review.text?.length > 200 ? { maxHeight: '100px', overflow: 'hidden' } : {}}>
                {review.text}
            </p>

            {review.text?.length > 200 && (
                <button
                    className="btn btn-link btn-sm p-0 mb-2"
                    onClick={() => setIsExpanded(!isExpanded)}
                >
                    {isExpanded ? 'Згорнути' : 'Читати далі'}
                </button>
            )}

            {(review.advantages || review.disadvantages) && (
                <div className="row g-3 mb-3">
                    {review.advantages && (
                        <div className="col-md-6">
                            <div className="small">
                                <span className="text-success fw-medium">
                                    <i className="bi bi-plus-circle me-1"></i>Переваги:
                                </span>
                                <p className="mb-0 text-muted">{review.advantages}</p>
                            </div>
                        </div>
                    )}
                    {review.disadvantages && (
                        <div className="col-md-6">
                            <div className="small">
                                <span className="text-danger fw-medium">
                                    <i className="bi bi-dash-circle me-1"></i>Недоліки:
                                </span>
                                <p className="mb-0 text-muted">{review.disadvantages}</p>
                            </div>
                        </div>
                    )}
                </div>
            )}

            <div className="d-flex align-items-center">
                <span className="text-muted small me-3">Корисний відгук?</span>
                <button
                    className={`btn btn-sm ${review.user_vote === 'helpful' ? 'btn-success' : 'btn-outline-secondary'} me-2`}
                    onClick={() => onHelpful(review.id, true)}
                    disabled={review.is_own}
                >
                    <i className="bi bi-hand-thumbs-up me-1"></i>
                    {review.helpful_count || 0}
                </button>
                <button
                    className={`btn btn-sm ${review.user_vote === 'not_helpful' ? 'btn-danger' : 'btn-outline-secondary'}`}
                    onClick={() => onHelpful(review.id, false)}
                    disabled={review.is_own}
                >
                    <i className="bi bi-hand-thumbs-down"></i>
                </button>
            </div>
        </div>
    );
};

const ReviewForm = ({ productSlug, onSubmit, existingReview }) => {
    const [formData, setFormData] = useState({
        rating: existingReview?.rating || 5,
        title: existingReview?.title || '',
        text: existingReview?.text || '',
        advantages: existingReview?.advantages || '',
        disadvantages: existingReview?.disadvantages || '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            if (existingReview) {
                await api.patch(`/products/${productSlug}/reviews/${existingReview.id}/`, formData);
            } else {
                await api.post(`/products/${productSlug}/reviews/`, formData);
            }
            onSubmit();
        } catch (err) {
            setError(err.response?.data?.detail || 'Помилка збереження відгуку');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="bg-light rounded-3 p-4 mb-4">
            <h5 className="fw-bold mb-3">
                {existingReview ? 'Редагувати відгук' : 'Написати відгук'}
            </h5>

            {error && <div className="alert alert-danger">{error}</div>}

            <div className="mb-3">
                <label className="form-label">Ваша оцінка</label>
                <div>
                    <ReviewStars
                        rating={formData.rating}
                        size="large"
                        interactive
                        onChange={(rating) => setFormData(prev => ({ ...prev, rating }))}
                    />
                    <span className="ms-2 text-muted">{formData.rating} з 5</span>
                </div>
            </div>

            <div className="mb-3">
                <label className="form-label">Заголовок (необов'язково)</label>
                <input
                    type="text"
                    className="form-control"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Коротко про враження"
                />
            </div>

            <div className="mb-3">
                <label className="form-label">Ваш відгук</label>
                <textarea
                    className="form-control"
                    rows="4"
                    value={formData.text}
                    onChange={(e) => setFormData(prev => ({ ...prev, text: e.target.value }))}
                    placeholder="Розкажіть про свій досвід використання товару"
                />
            </div>

            <div className="row g-3 mb-3">
                <div className="col-md-6">
                    <label className="form-label text-success">
                        <i className="bi bi-plus-circle me-1"></i>Переваги
                    </label>
                    <textarea
                        className="form-control"
                        rows="2"
                        value={formData.advantages}
                        onChange={(e) => setFormData(prev => ({ ...prev, advantages: e.target.value }))}
                        placeholder="Що сподобалось?"
                    />
                </div>
                <div className="col-md-6">
                    <label className="form-label text-danger">
                        <i className="bi bi-dash-circle me-1"></i>Недоліки
                    </label>
                    <textarea
                        className="form-control"
                        rows="2"
                        value={formData.disadvantages}
                        onChange={(e) => setFormData(prev => ({ ...prev, disadvantages: e.target.value }))}
                        placeholder="Що не сподобалось?"
                    />
                </div>
            </div>

            <button type="submit" className="btn btn-success" disabled={loading}>
                {loading ? (
                    <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Збереження...
                    </>
                ) : (
                    <>
                        <i className="bi bi-send me-2"></i>
                        {existingReview ? 'Оновити відгук' : 'Опублікувати'}
                    </>
                )}
            </button>
        </form>
    );
};

const ProductReviews = ({ productSlug }) => {
    const { isAuthenticated, user } = useContext(AuthContext);
    const [reviews, setReviews] = useState([]);
    const [stats, setStats] = useState(null);
    const [myReview, setMyReview] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [filter, setFilter] = useState({ rating: '', verified_only: false, ordering: '-created_at' });

    useEffect(() => {
        fetchReviews();
        fetchStats();
        if (isAuthenticated) {
            fetchMyReview();
        }
    }, [productSlug, filter, isAuthenticated]);

    const fetchReviews = async () => {
        try {
            const params = new URLSearchParams();
            if (filter.rating) params.append('rating', filter.rating);
            if (filter.verified_only) params.append('verified_only', 'true');
            if (filter.ordering) params.append('ordering', filter.ordering);

            const response = await api.get(`/products/${productSlug}/reviews/?${params}`);
            setReviews(response.data || []);
        } catch (err) {
            console.error('Error fetching reviews:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await api.get(`/products/${productSlug}/reviews/stats/`);
            setStats(response.data);
        } catch (err) {
            console.error('Error fetching stats:', err);
        }
    };

    const fetchMyReview = async () => {
        try {
            const response = await api.get(`/products/${productSlug}/reviews/my/`);
            setMyReview(response.data);
        } catch (err) {
        }
    };

    const handleHelpful = async (reviewId, isHelpful) => {
        if (!isAuthenticated) {
            alert('Увійдіть, щоб голосувати');
            return;
        }
        try {
            await api.post(`/products/${productSlug}/reviews/${reviewId}/helpful/`, { is_helpful: isHelpful });
            fetchReviews();
        } catch (err) {
            console.error('Error voting:', err);
        }
    };

    const handleFormSubmit = () => {
        setShowForm(false);
        fetchReviews();
        fetchStats();
        fetchMyReview();
    };

    const RatingBar = ({ rating, count, total }) => {
        const percent = total > 0 ? (count / total) * 100 : 0;
        return (
            <div className="d-flex align-items-center mb-1">
                <span className="me-2" style={{ width: '20px' }}>{rating}</span>
                <i className="bi bi-star-fill text-warning me-2"></i>
                <div className="progress flex-grow-1" style={{ height: '8px' }}>
                    <div className="progress-bar bg-warning" style={{ width: `${percent}%` }}></div>
                </div>
                <span className="ms-2 text-muted small" style={{ width: '30px' }}>{count}</span>
            </div>
        );
    };

    if (loading) {
        return (
            <div className="text-center py-4">
                <div className="spinner-border text-success"></div>
            </div>
        );
    }

    return (
        <div className="mt-5">
            <h4 className="fw-bold mb-4">
                <i className="bi bi-chat-left-text me-2"></i>
                Відгуки
                {stats && <span className="badge bg-secondary ms-2">{stats.total_reviews}</span>}
            </h4>

            <div className="row g-4 mb-4">
                <div className="col-md-4">
                    {stats && (
                        <div className="bg-light rounded-3 p-4 text-center">
                            <div className="display-4 fw-bold text-success mb-2">
                                {stats.average_rating?.toFixed(1) || '0.0'}
                            </div>
                            <ReviewStars rating={Math.round(stats.average_rating || 0)} />
                            <p className="text-muted mb-3">{stats.total_reviews} відгуків</p>

                            <div className="text-start">
                                {[5, 4, 3, 2, 1].map(rating => (
                                    <RatingBar
                                        key={rating}
                                        rating={rating}
                                        count={stats.rating_distribution?.[rating] || 0}
                                        total={stats.total_reviews}
                                    />
                                ))}
                            </div>

                            {stats.verified_purchases_percent > 0 && (
                                <p className="text-muted small mt-3 mb-0">
                                    <i className="bi bi-patch-check text-success me-1"></i>
                                    {stats.verified_purchases_percent.toFixed(0)}% підтверджених покупок
                                </p>
                            )}
                        </div>
                    )}

                    {isAuthenticated && !myReview && (
                        <button
                            className="btn btn-success w-100 mt-3"
                            onClick={() => setShowForm(true)}
                        >
                            <i className="bi bi-pencil me-2"></i>
                            Написати відгук
                        </button>
                    )}
                    {!isAuthenticated && (
                        <p className="text-muted small mt-3 text-center">
                            <a href="/login">Увійдіть</a>, щоб залишити відгук
                        </p>
                    )}
                </div>

                <div className="col-md-8">
                    {showForm && (
                        <ReviewForm
                            productSlug={productSlug}
                            onSubmit={handleFormSubmit}
                            existingReview={myReview}
                        />
                    )}

                    {myReview && !showForm && (
                        <div className="alert alert-info d-flex justify-content-between align-items-center">
                            <span>Ви вже залишили відгук на цей товар</span>
                            <button
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => setShowForm(true)}
                            >
                                Редагувати
                            </button>
                        </div>
                    )}

                    <div className="d-flex gap-2 flex-wrap mb-3">
                        <select
                            className="form-select form-select-sm"
                            style={{ width: 'auto' }}
                            value={filter.ordering}
                            onChange={(e) => setFilter(prev => ({ ...prev, ordering: e.target.value }))}
                        >
                            <option value="-created_at">Спочатку нові</option>
                            <option value="helpful">Найкорисніші</option>
                            <option value="rating_high">Висока оцінка</option>
                            <option value="rating_low">Низька оцінка</option>
                        </select>

                        <select
                            className="form-select form-select-sm"
                            style={{ width: 'auto' }}
                            value={filter.rating}
                            onChange={(e) => setFilter(prev => ({ ...prev, rating: e.target.value }))}
                        >
                            <option value="">Всі оцінки</option>
                            {[5, 4, 3, 2, 1].map(r => (
                                <option key={r} value={r}>{r} ★</option>
                            ))}
                        </select>

                        <div className="form-check form-check-inline align-self-center">
                            <input
                                type="checkbox"
                                className="form-check-input"
                                id="verifiedOnly"
                                checked={filter.verified_only}
                                onChange={(e) => setFilter(prev => ({ ...prev, verified_only: e.target.checked }))}
                            />
                            <label className="form-check-label small" htmlFor="verifiedOnly">
                                Тільки підтверджені покупки
                            </label>
                        </div>
                    </div>

                    {reviews.length > 0 ? (
                        reviews.map(review => (
                            <ReviewItem
                                key={review.id}
                                review={review}
                                onHelpful={handleHelpful}
                                currentUserId={user?.id}
                            />
                        ))
                    ) : (
                        <div className="text-center py-5 text-muted">
                            <i className="bi bi-chat-left text-muted" style={{ fontSize: '48px' }}></i>
                            <p className="mt-3">Ще немає відгуків</p>
                            {isAuthenticated && (
                                <button
                                    className="btn btn-success"
                                    onClick={() => setShowForm(true)}
                                >
                                    Будьте першим!
                                </button>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export { ProductReviews, ReviewStars };
export default ProductReviews;