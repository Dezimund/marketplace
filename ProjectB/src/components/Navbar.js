import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';

function Navbar({ categories }) {
  const [searchQuery, setSearchQuery] = useState('');
  const { user, isAuthenticated, logout } = useAuth();
  const { totalItems } = useCart();
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/catalog?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <>
      <header className="header-top py-3">
        <div className="container">
          <div className="d-flex align-items-center justify-content-between gap-4">
            {/* Logo */}
            <Link to="/" className="logo">
              <i className="bi bi-shop me-2"></i>Market
            </Link>

            <form onSubmit={handleSearch} className="d-none d-md-flex flex-grow-1" style={{ maxWidth: '600px' }}>
              <input
                type="text"
                className="form-control search-input"
                placeholder="Я шукаю..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button type="submit" className="btn search-btn">
                <i className="bi bi-search"></i>
              </button>
            </form>

            <div className="d-flex align-items-center gap-2">
              {/* Cart */}
              <Link to="/cart" className="header-icon position-relative">
                <i className="bi bi-cart3" style={{ fontSize: '24px' }}></i>
                <span className="d-none d-md-block" style={{ fontSize: '12px' }}>Кошик</span>
                {totalItems > 0 && (
                  <span className="cart-badge">{totalItems}</span>
                )}
              </Link>

              {isAuthenticated ? (
                <div className="dropdown">
                  <button
                    className="header-icon dropdown-toggle border-0 bg-transparent"
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                  >
                    <i className="bi bi-person-circle" style={{ fontSize: '24px' }}></i>
                    <span className="d-none d-md-block" style={{ fontSize: '12px' }}>
                      {user?.first_name || 'Профіль'}
                    </span>
                  </button>
                  <ul className="dropdown-menu dropdown-menu-end">
                    <li>
                      <Link className="dropdown-item" to="/profile">
                        <i className="bi bi-person me-2"></i>Мій профіль
                      </Link>
                    </li>
                    <li>
                      <Link className="dropdown-item" to="/orders">
                        <i className="bi bi-box me-2"></i>Мої замовлення
                      </Link>
                    </li>
                    {user?.is_seller && (
                      <li>
                        <Link className="dropdown-item" to="/my-products">
                          <i className="bi bi-shop me-2"></i>Мої товари
                        </Link>
                      </li>
                    )}
                    <li><hr className="dropdown-divider" /></li>
                    <li>
                      <button className="dropdown-item text-danger" onClick={logout}>
                        <i className="bi bi-box-arrow-right me-2"></i>Вийти
                      </button>
                    </li>
                  </ul>
                </div>
              ) : (
                <Link to="/login" className="btn btn-success">
                  <i className="bi bi-box-arrow-in-right me-1"></i>
                  <span className="d-none d-md-inline">Увійти</span>
                </Link>
              )}
            </div>
          </div>
        </div>
      </header>

      <nav className="categories-nav">
        <div className="container">
          <div className="d-flex align-items-center gap-3">
            <div className="dropdown">
              <button
                className="btn catalog-btn dropdown-toggle"
                type="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                <i className="bi bi-grid-3x3-gap-fill me-2"></i>
                Каталог
              </button>
              <ul className="dropdown-menu">
                {categories?.map((category) => (
                  <li key={category.id}>
                    <Link className="dropdown-item" to={`/catalog/${category.slug}`}>
                      {category.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div className="d-flex overflow-auto" style={{ gap: '0' }}>
              {categories?.map((category) => (
                <Link
                  key={category.id}
                  to={`/catalog/${category.slug}`}
                  className="category-link"
                >
                  {category.name}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </nav>
    </>
  );
}

export default Navbar;