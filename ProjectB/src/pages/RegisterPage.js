import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function RegisterPage() {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    password_confirm: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const { register, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    if (formData.password !== formData.password_confirm) {
      setErrors({ password_confirm: 'Паролі не співпадають' });
      return;
    }

    setLoading(true);
    const result = await register(formData);

    if (result.success) {
      navigate('/');
    } else {
      setErrors(result.errors || { general: 'Помилка реєстрації' });
    }

    setLoading(false);
  };

  return (
    <div className="row justify-content-center">
      <div className="col-md-6 col-lg-5">
        <div className="bg-white rounded-4 p-4 p-md-5">
          <div className="text-center mb-4">
            <i className="bi bi-person-plus text-success" style={{ fontSize: '64px' }}></i>
            <h2 className="h4 mt-3">Реєстрація</h2>
          </div>

          {errors.general && (
            <div className="alert alert-danger" role="alert">
              <i className="bi bi-exclamation-circle me-2"></i>{errors.general}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">Ім'я</label>
                <input
                  type="text"
                  className={`form-control ${errors.first_name ? 'is-invalid' : ''}`}
                  name="first_name"
                  placeholder="Ваше ім'я"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                />
                {errors.first_name && (
                  <div className="invalid-feedback">{errors.first_name}</div>
                )}
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">Прізвище</label>
                <input
                  type="text"
                  className={`form-control ${errors.last_name ? 'is-invalid' : ''}`}
                  name="last_name"
                  placeholder="Ваше прізвище"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                />
                {errors.last_name && (
                  <div className="invalid-feedback">{errors.last_name}</div>
                )}
              </div>
            </div>

            <div className="mb-3">
              <label className="form-label">Email</label>
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-envelope"></i>
                </span>
                <input
                  type="email"
                  className={`form-control ${errors.email ? 'is-invalid' : ''}`}
                  name="email"
                  placeholder="example@email.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
                {errors.email && (
                  <div className="invalid-feedback">{errors.email}</div>
                )}
              </div>
            </div>

            <div className="mb-3">
              <label className="form-label">Пароль</label>
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-lock"></i>
                </span>
                <input
                  type="password"
                  className={`form-control ${errors.password ? 'is-invalid' : ''}`}
                  name="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  minLength="8"
                />
                {errors.password && (
                  <div className="invalid-feedback">{errors.password}</div>
                )}
              </div>
            </div>

            <div className="mb-4">
              <label className="form-label">Підтвердження пароля</label>
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-lock-fill"></i>
                </span>
                <input
                  type="password"
                  className={`form-control ${errors.password_confirm ? 'is-invalid' : ''}`}
                  name="password_confirm"
                  placeholder="••••••••"
                  value={formData.password_confirm}
                  onChange={handleChange}
                  required
                />
                {errors.password_confirm && (
                  <div className="invalid-feedback">{errors.password_confirm}</div>
                )}
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-buy btn-lg w-100"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                  Реєстрація...
                </>
              ) : (
                <>
                  <i className="bi bi-person-plus me-2"></i>Зареєструватися
                </>
              )}
            </button>
          </form>

          <hr className="my-4" />

          <p className="text-center text-muted mb-0">
            Вже маєте акаунт?{' '}
            <Link to="/login" className="text-success text-decoration-none fw-medium">
              Увійти
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;