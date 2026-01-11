import React from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { getImageUrl } from '../services/api';

function CartPage() {
  const { cart, loading, updateQuantity, removeFromCart, clearCart } = useCart();

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner-border text-success" role="status">
          <span className="visually-hidden">Завантаження...</span>
        </div>
      </div>
    );
  }

  if (!cart?.items?.length) {
    return (
      <div className="bg-white rounded-4 p-5 text-center">
        <i className="bi bi-cart-x text-muted" style={{ fontSize: '80px' }}></i>
        <h4 className="mt-4">Кошик порожній</h4>
        <p className="text-muted mb-4">Додайте товари до кошика, щоб оформити замовлення</p>
        <Link to="/catalog" className="btn btn-success btn-lg">
          <i className="bi bi-arrow-left me-2"></i>Перейти до каталогу
        </Link>
      </div>
    );
  }

  return (
    <>
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item">
            <Link to="/"><i className="bi bi-house-fill me-1"></i>Головна</Link>
          </li>
          <li className="breadcrumb-item active" aria-current="page">Кошик</li>
        </ol>
      </nav>

      <h1 className="h3 mb-4">
        <i className="bi bi-cart3 me-2"></i>Кошик
        <span className="badge bg-success ms-2">{cart.total_items}</span>
      </h1>

      <div className="row">
        <div className="col-lg-8 mb-4">
          <div className="bg-white rounded-4 overflow-hidden">
            <div className="d-flex justify-content-between align-items-center p-3 border-bottom">
              <span className="text-muted">{cart.total_items} товарів</span>
              <button
                className="btn btn-sm btn-outline-danger"
                onClick={clearCart}
              >
                <i className="bi bi-trash me-1"></i>Очистити кошик
              </button>
            </div>

            {cart.items.map((item) => (
              <div key={item.id} className="p-3 border-bottom">
                <div className="row align-items-center">
                  <div className="col-3 col-md-2">
                    <Link to={`/product/${item.product?.slug}`}>
                      {item.product?.main_image ? (
                        <img
                          src={getImageUrl(item.product.main_image)}
                          alt={item.product?.name}
                          className="img-fluid rounded"
                          style={{ maxHeight: '80px', objectFit: 'cover' }}
                        />
                      ) : (
                        <div className="bg-light rounded d-flex align-items-center justify-content-center" style={{ height: '80px' }}>
                          <i className="bi bi-image text-muted"></i>
                        </div>
                      )}
                    </Link>
                  </div>

                  <div className="col-9 col-md-4">
                    <Link to={`/product/${item.product?.slug}`} className="text-decoration-none text-dark">
                      <h6 className="mb-1">{item.product?.name}</h6>
                    </Link>
                    {item.product_size && (
                      <small className="text-muted">Розмір: {item.product_size.size_name}</small>
                    )}
                  </div>

                  <div className="col-6 col-md-2 mt-2 mt-md-0">
                    <span className="fw-bold">{item.product?.price} ₴</span>
                  </div>

                  <div className="col-6 col-md-2 mt-2 mt-md-0">
                    <div className="d-flex align-items-center">
                      <button
                        className="btn btn-sm btn-outline-secondary"
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        disabled={item.quantity <= 1}
                      >
                        <i className="bi bi-dash"></i>
                      </button>
                      <span className="mx-2">{item.quantity}</span>
                      <button
                        className="btn btn-sm btn-outline-secondary"
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      >
                        <i className="bi bi-plus"></i>
                      </button>
                    </div>
                  </div>

                  <div className="col-12 col-md-2 mt-2 mt-md-0 d-flex justify-content-between align-items-center">
                    <span className="fw-bold text-success">{item.total_price} ₴</span>
                    <button
                      className="btn btn-sm text-danger"
                      onClick={() => removeFromCart(item.id)}
                      title="Видалити"
                    >
                      <i className="bi bi-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="col-lg-4">
          <div className="bg-white rounded-4 p-4 sticky-top" style={{ top: '100px' }}>
            <h5 className="mb-4">Разом</h5>

            <div className="d-flex justify-content-between mb-2">
              <span className="text-muted">Товари ({cart.total_items})</span>
              <span>{cart.subtotal} ₴</span>
            </div>
            <div className="d-flex justify-content-between mb-2">
              <span className="text-muted">Доставка</span>
              <span className="text-success">Безкоштовно</span>
            </div>

            <hr />

            <div className="d-flex justify-content-between mb-4">
              <span className="h5 mb-0">До сплати</span>
              <span className="h5 mb-0 text-success">{cart.subtotal} ₴</span>
            </div>

            <Link to="/checkout" className="btn btn-buy btn-lg w-100 mb-3">
              <i className="bi bi-credit-card me-2"></i>Оформити замовлення
            </Link>

            <Link to="/catalog" className="btn btn-outline-secondary w-100">
              <i className="bi bi-arrow-left me-2"></i>Продовжити покупки
            </Link>

            <div className="mt-4 pt-4 border-top">
              <div className="d-flex align-items-center text-muted mb-2">
                <i className="bi bi-truck me-2"></i>
                <small>Безкоштовна доставка від 1000 ₴</small>
              </div>
              <div className="d-flex align-items-center text-muted">
                <i className="bi bi-arrow-counterclockwise me-2"></i>
                <small>14 днів на повернення</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default CartPage;