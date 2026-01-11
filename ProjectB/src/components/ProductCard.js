import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { getImageUrl } from '../services/api';

function ProductCard({ product }) {
  const { addToCart } = useCart();
  const [loading, setLoading] = useState(false);

  const handleAddToCart = async () => {
    if (!product.is_in_stock) return;
    setLoading(true);
    await addToCart(product.id, 1);
    setLoading(false);
  };

  const discountPercent = product.old_price
    ? Math.round((1 - product.price / product.old_price) * 100)
    : 0;

  const imageUrl = getImageUrl(product.main_image);
  const isInStock = product.is_in_stock !== false; // За замовчуванням true

  return (
    <div className={`product-card ${!isInStock ? 'out-of-stock' : ''}`}>
      <div className="product-image-container">
        {imageUrl ? (
          <img
            src={imageUrl}
            className="product-image"
            alt={product.name}
            loading="lazy"
            style={!isInStock ? { opacity: 0.6 } : {}}
          />
        ) : (
          <div className="product-image bg-light d-flex align-items-center justify-content-center">
            <i className="bi bi-image text-muted" style={{ fontSize: '48px' }}></i>
          </div>
        )}

        {/* Badges */}
        {!isInStock ? (
          <span className="product-badge bg-secondary">Немає</span>
        ) : product.old_price ? (
          <span className="product-badge bg-danger">-{discountPercent}%</span>
        ) : product.is_new ? (
          <span className="product-badge bg-info">Новинка</span>
        ) : null}

        {/* Favorite Button */}
        <button className="product-favorite" title="Додати в обране">
          <i className="bi bi-heart"></i>
        </button>
      </div>

      <div className="product-info">
        <Link to={`/product/${product.slug}`} className="product-title">
          {product.name}
        </Link>

        {product.color && (
          <small className="text-muted d-block mb-1">
            <i className="bi bi-palette me-1"></i>{product.color}
          </small>
        )}

        <div className={`product-availability ${!isInStock ? 'out-of-stock' : ''}`}>
          {isInStock ? (
            <>
              <i className="bi bi-check-circle-fill me-1"></i>В наявності
            </>
          ) : (
            <>
              <i className="bi bi-x-circle-fill me-1"></i>Немає в наявності
            </>
          )}
        </div>

        <div className="product-price-container">
          <span className="product-price">{product.price} ₴</span>
          {product.old_price && (
            <span className="product-old-price">{product.old_price} ₴</span>
          )}
        </div>

        <button
          className={`btn ${isInStock ? 'btn-buy' : 'btn-secondary'}`}
          onClick={handleAddToCart}
          disabled={loading || !isInStock}
        >
          {loading ? (
            <span className="spinner-border spinner-border-sm me-1" role="status"></span>
          ) : isInStock ? (
            <i className="bi bi-cart-plus me-1"></i>
          ) : (
            <i className="bi bi-x-circle me-1"></i>
          )}
          {isInStock ? 'Купити' : 'Немає'}
        </button>
      </div>
    </div>
  );
}

export default ProductCard;