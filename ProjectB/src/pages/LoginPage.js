import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(email, password);

    if (result.success) {
      navigate('/');
    } else {
      setError(result.error || 'Помилка входу');
    }

    setLoading(false);
  };

  return (
    <div className="row justify-content-center">
      <div className="col-md-5 col-lg-4">
        <div className="bg-white rounded-4 p-4 p-md-5">
          <div className="text-center mb-4">
            <i className="bi bi-person-circle text-success" style={{ fontSize: '64px' }}></i>
            <h2 className="h4 mt-3">Вхід в акаунт</h2>
          </div>

          {error && (
            <div className="alert alert-danger" role="alert">
              <i className="bi bi-exclamation-circle me-2"></i>{error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label">Email</label>
              <div className="input-group">
                <span className="input-group-text">
                  <i className="bi bi-envelope"></i>
                </span>
                <input
                  type="email"
                  className="form-control"
                  placeholder="example@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
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
                  className="form-control"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="d-flex justify-content-between align-items-center mb-4">
              <div className="form-check">
                <input type="checkbox" className="form-check-input" id="remember" />
                <label className="form-check-label" htmlFor="remember">
                  Запам'ятати мене
                </label>
              </div>
              <Link to="/forgot-password" className="text-success text-decoration-none">
                Забули пароль?
              </Link>
            </div>

            <button
              type="submit"
              className="btn btn-buy btn-lg w-100"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                  Вхід...
                </>
              ) : (
                <>
                  <i className="bi bi-box-arrow-in-right me-2"></i>Увійти
                </>
              )}
            </button>
          </form>

          <hr className="my-4" />

          <p className="text-center text-muted mb-0">
            Немає акаунту?{' '}
            <Link to="/register" className="text-success text-decoration-none fw-medium">
              Зареєструватися
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;