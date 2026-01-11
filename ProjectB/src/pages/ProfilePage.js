import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';

function ProfilePage() {
  const { user, isAuthenticated, updateUser, logout } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: user.phone || '',
      });
    }
  }, [user, isAuthenticated, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await authAPI.updateProfile(formData);
      updateUser(response.data);
      setSuccess('Профіль успішно оновлено!');
    } catch (err) {
      setError('Помилка оновлення профілю');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item">
            <Link to="/"><i className="bi bi-house-fill me-1"></i>Головна</Link>
          </li>
          <li className="breadcrumb-item active" aria-current="page">Профіль</li>
        </ol>
      </nav>

      <div className="row">
        <div className="col-lg-3 mb-4">
          <div className="bg-white rounded-4 p-4">
            <div className="text-center mb-4">
              <div className="bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center" style={{ width: '80px', height: '80px' }}>
                <i className="bi bi-person-fill" style={{ fontSize: '40px' }}></i>
              </div>
              <h5 className="mt-3 mb-1">{user?.first_name} {user?.last_name}</h5>
              <small className="text-muted">{user?.email}</small>
            </div>

            <ul className="list-unstyled">
              <li className="mb-2">
                <Link to="/profile" className="d-flex align-items-center text-decoration-none text-success fw-medium p-2 rounded" style={{ backgroundColor: 'rgba(0,160,70,0.1)' }}>
                  <i className="bi bi-person me-3"></i>Особисті дані
                </Link>
              </li>
              <li className="mb-2">
                <Link to="/orders" className="d-flex align-items-center text-decoration-none text-dark p-2 rounded hover-bg-light">
                  <i className="bi bi-box me-3"></i>Мої замовлення
                </Link>
              </li>
              <li className="mb-2">
                <Link to="/wishlist" className="d-flex align-items-center text-decoration-none text-dark p-2 rounded">
                  <i className="bi bi-heart me-3"></i>Список бажань
                </Link>
              </li>
              {user?.is_seller && (
                <li className="mb-2">
                  <Link to="/my-products" className="d-flex align-items-center text-decoration-none text-dark p-2 rounded">
                    <i className="bi bi-shop me-3"></i>Мої товари
                  </Link>
                </li>
              )}
              <li className="mb-2">
                <button onClick={handleLogout} className="d-flex align-items-center text-decoration-none text-danger p-2 rounded border-0 bg-transparent w-100">
                  <i className="bi bi-box-arrow-right me-3"></i>Вийти
                </button>
              </li>
            </ul>
          </div>
        </div>

        <div className="col-lg-9">
          <div className="bg-white rounded-4 p-4">
            <h4 className="mb-4">
              <i className="bi bi-person me-2"></i>Особисті дані
            </h4>

            {success && (
              <div className="alert alert-success" role="alert">
                <i className="bi bi-check-circle me-2"></i>{success}
              </div>
            )}

            {error && (
              <div className="alert alert-danger" role="alert">
                <i className="bi bi-exclamation-circle me-2"></i>{error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">Ім'я</label>
                  <input
                    type="text"
                    className="form-control"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                  />
                </div>
                <div className="col-md-6 mb-3">
                  <label className="form-label">Прізвище</label>
                  <input
                    type="text"
                    className="form-control"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="row">
                <div className="col-md-6 mb-3">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-control"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    disabled
                  />
                  <small className="text-muted">Email не можна змінити</small>
                </div>
                <div className="col-md-6 mb-3">
                  <label className="form-label">Телефон</label>
                  <input
                    type="tel"
                    className="form-control"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    placeholder="+380"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="btn btn-success"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                    Збереження...
                  </>
                ) : (
                  <>
                    <i className="bi bi-check2 me-2"></i>Зберегти зміни
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="bg-white rounded-4 p-4 mt-4">
            <h4 className="mb-4">
              <i className="bi bi-lock me-2"></i>Зміна пароля
            </h4>
            <p className="text-muted">Для зміни пароля натисніть кнопку нижче</p>
            <button className="btn btn-outline-secondary">
              <i className="bi bi-key me-2"></i>Змінити пароль
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default ProfilePage;