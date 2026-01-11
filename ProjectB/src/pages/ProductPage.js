import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { productsAPI, getImageUrl } from '../services/api';
import { useCart } from '../context/CartContext';
import ProductCard from '../components/ProductCard';
import ProductReviews, { ReviewStars } from '../components/Reviews';
import api from '../services/api';

function ProductPage() {
  const { slug } = useParams();
  const { addToCart } = useCart();
  
  const [product, setProduct] = useState(null);
  const [relatedProducts, setRelatedProducts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [reviewStats, setReviewStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [addingToCart, setAddingToCart] = useState(false);
  
  const [selectedSize, setSelectedSize] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [activeImage, setActiveImage] = useState(null);

  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true);
      try {
        const response = await productsAPI.getBySlug(slug);
        setProduct(response.data);
        setActiveImage(getImageUrl(response.data.main_image));
        
        if (response.data.product_sizes?.length > 0) {
          const availableSize = response.data.product_sizes.find(ps => ps.stock > 0);
          setSelectedSize(availableSize?.id || response.data.product_sizes[0].id);
        }

        if (response.data.category) {
          const relatedRes = await productsAPI.getRelated(slug);
          setRelatedProducts(relatedRes.data);
        }
        
        try {
          const statsRes = await api.get(`/products/${slug}/reviews/stats/`);
          setReviewStats(statsRes.data);
        } catch (e) {
          console.log('No review stats');
        }
        
        try {
          const recRes = await api.get(`/recommendations/?type=also_bought&product=${slug}&limit=4`);
          setRecommendations(recRes.data.products || []);
        } catch (e) {
          console.log('No recommendations');
        }
      } catch (error) {
        console.error('Error fetching product:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
    window.scrollTo(0, 0);
  }, [slug]);

  const handleAddToCart = async () => {
    setAddingToCart(true);
    await addToCart(product.id, quantity, selectedSize);
    setAddingToCart(false);
  };

  const changeQty = (delta) => {
    const newQty = quantity + delta;
    if (newQty >= 1) {
      setQuantity(newQty);
    }
  };

  const discountPercent = product?.old_price
    ? Math.round((1 - product.price / product.old_price) * 100)
    : 0;

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner-border text-success" role="status">
          <span className="visually-hidden">Завантаження...</span>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="bg-white rounded-4 p-5 text-center">
        <i className="bi bi-exclamation-circle text-muted" style={{ fontSize: '64px' }}></i>
        <h5 className="mt-3">Товар не знайдено</h5>
        <Link to="/catalog" className="btn btn-success mt-3">
          Повернутися до каталогу
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
          <li className="breadcrumb-item">
            <Link to="/catalog">Каталог</Link>
          </li>
          <li className="breadcrumb-item">
            <Link to={`/catalog/${product.category?.slug}`}>{product.category?.name}</Link>
          </li>
          <li className="breadcrumb-item active" aria-current="page">{product.name}</li>
        </ol>
      </nav>

      <div className="bg-white rounded-4 p-4 mb-4">
        <div className="row">
          <div className="col-lg-5 mb-4 mb-lg-0">
            <div className="product-gallery">
              <div
                className="position-relative mb-3"
                style={{ paddingTop: '100%', borderRadius: '12px', overflow: 'hidden', background: '#f8f9fa' }}
              >
                {activeImage ? (
                  <img
                    src={activeImage}
                    className="position-absolute top-0 start-0 w-100 h-100"
                    style={{ objectFit: 'contain' }}
                    alt={product.name}
                  />
                ) : (
                  <div className="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-light">
                    <i className="bi bi-image text-muted" style={{ fontSize: '100px' }}></i>
                  </div>
                )}

                {product.is_new && (
                  <span className="position-absolute badge bg-info" style={{ top: '12px', left: '12px' }}>
                    Новинка
                  </span>
                )}
                {product.old_price && (
                  <span className="position-absolute badge bg-danger" style={{ top: '12px', left: '12px' }}>
                    -{discountPercent}%
                  </span>
                )}
              </div>

              {product.images?.length > 0 && (
                <div className="d-flex gap-2 overflow-auto pb-2">
                  <div
                    className={`thumbnail-item ${activeImage === getImageUrl(product.main_image) ? 'active' : ''}`}
                    onClick={() => setActiveImage(getImageUrl(product.main_image))}
                  >
                    <img src={getImageUrl(product.main_image)} className="w-100 h-100" style={{ objectFit: 'cover' }} alt="" />
                  </div>
                  {product.images.map((img, index) => (
                    <div
                      key={index}
                      className={`thumbnail-item ${activeImage === getImageUrl(img.image) ? 'active' : ''}`}
                      onClick={() => setActiveImage(getImageUrl(img.image))}
                    >
                      <img src={getImageUrl(img.image)} className="w-100 h-100" style={{ objectFit: 'cover' }} alt="" />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="col-lg-7">
            <div className="ps-lg-4">
              <h1 className="h3 mb-3">{product.name}</h1>

              <div className="d-flex align-items-center gap-4 mb-3">
                <div className="d-flex align-items-center">
                  <ReviewStars rating={Math.round(reviewStats?.average_rating || product.rating || 0)} size="small" />
                  <span className="text-muted ms-2">
                    {(reviewStats?.average_rating || product.rating || 0).toFixed(1)} ({reviewStats?.total_reviews || product.reviews_count || 0} відгуків)
                  </span>
                </div>
                <span className="text-muted">
                  <i className="bi bi-eye me-1"></i>{product.views_count} переглядів
                </span>
              </div>

              <div className="d-flex flex-wrap gap-3 mb-4">
                {product.is_in_stock ? (
                  <span className="badge bg-success-subtle text-success px-3 py-2">
                    <i className="bi bi-check-circle-fill me-1"></i>
                    В наявності {product.total_stock > 0 && product.total_stock < 10}
                  </span>
                ) : (
                  <span className="badge bg-danger-subtle text-danger px-3 py-2">
                    <i className="bi bi-x-circle-fill me-1"></i>Немає в наявності
                  </span>
                )}
                {product.seller && (
                  <Link to={`/seller/${product.seller.id}`} className="text-decoration-none">
                    <span className="badge bg-light text-dark border px-3 py-2">
                      <i className="bi bi-shop me-1"></i>
                      Продавець: {product.seller.first_name || product.seller.email || 'Магазин'}
                    </span>
                  </Link>
                )}
                {!product.seller && product.seller_name && (
                  <span className="text-muted">
                    <i className="bi bi-shop me-1"></i>Продавець: {product.seller_name}
                  </span>
                )}
                <span className="text-muted">
                  <i className="bi bi-tag me-1"></i>{product.category?.name}
                </span>
              </div>

              <div className="bg-light rounded-3 p-4 mb-4">
                <div className="d-flex align-items-baseline gap-3">
                  <span className="display-5 fw-bold text-success">{product.price} ₴</span>
                  {product.old_price && (
                    <>
                      <span className="fs-4 text-muted text-decoration-line-through">{product.old_price} ₴</span>
                      <span className="badge bg-danger">-{discountPercent}%</span>
                    </>
                  )}
                </div>
              </div>

              {product.color && (
                <div className="mb-4">
                  <h6 className="text-muted mb-2">Колір:</h6>
                  <span className="badge bg-light text-dark border px-3 py-2">
                    <i className="bi bi-palette me-1"></i>{product.color}
                  </span>
                </div>
              )}

              {product.product_sizes?.length > 0 && (
                <div className="mb-4">
                  <h6 className="text-muted mb-2">Оберіть розмір:</h6>
                  <div className="d-flex flex-wrap gap-2">
                    {product.product_sizes.map((ps) => (
                      <button
                        key={ps.id}
                        type="button"
                        className={`btn btn-outline-secondary size-btn ${selectedSize === ps.id ? 'active' : ''}`}
                        onClick={() => setSelectedSize(ps.id)}
                        disabled={ps.stock === 0}
                      >
                        {ps.size_name}
                        {ps.stock < 5 && ps.stock > 0 && (
                          <small className="text-warning ms-1"></small>
                        )}
                        {ps.stock === 0 && (
                          <small className="text-danger ms-1">(немає)</small>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="d-flex gap-3 mb-4">
                <div className="d-flex align-items-center">
                  <button
                    type="button"
                    className="btn btn-outline-secondary qty-btn"
                    onClick={() => changeQty(-1)}
                  >
                    <i className="bi bi-dash"></i>
                  </button>
                  <input
                    type="number"
                    className="form-control qty-input mx-2"
                    value={quantity}
                    onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                    min="1"
                  />
                  <button
                    type="button"
                    className="btn btn-outline-secondary qty-btn"
                    onClick={() => changeQty(1)}
                  >
                    <i className="bi bi-plus"></i>
                  </button>
                </div>

                <button
                  className={`btn flex-grow-1 ${product.is_in_stock ? 'btn-buy' : 'btn-secondary'}`}
                  onClick={handleAddToCart}
                  disabled={addingToCart || !product.is_in_stock}
                  style={{ maxWidth: '300px' }}
                >
                  {addingToCart ? (
                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                  ) : product.is_in_stock ? (
                    <i className="bi bi-cart-plus me-2"></i>
                  ) : (
                    <i className="bi bi-x-circle me-2"></i>
                  )}
                  {product.is_in_stock ? 'Додати в кошик' : 'Немає в наявності'}
                </button>

                <button className="btn btn-outline-danger" title="Додати в обране">
                  <i className="bi bi-heart"></i>
                </button>
              </div>

              <div className="row g-3">
                <div className="col-md-6">
                  <div className="d-flex align-items-center p-3 bg-light rounded-3">
                    <i className="bi bi-truck text-success me-3" style={{ fontSize: '24px' }}></i>
                    <div>
                      <div className="fw-medium">Доставка</div>
                      <small className="text-muted">Нова Пошта, Укрпошта</small>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="d-flex align-items-center p-3 bg-light rounded-3">
                    <i className="bi bi-shield-check text-success me-3" style={{ fontSize: '24px' }}></i>
                    <div>
                      <div className="fw-medium">Гарантія</div>
                      <small className="text-muted">14 днів на повернення</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {product.description && (
        <div className="bg-white rounded-4 p-4 mb-4">
          <h3 className="h5 mb-3">
            <i className="bi bi-file-text me-2"></i>Опис товару
          </h3>
          <p className="text-muted mb-0" style={{ whiteSpace: 'pre-line' }}>
            {product.description}
          </p>
        </div>
      )}

      {relatedProducts.length > 0 && (
        <div className="mb-4">
          <h3 className="h5 mb-4">
            <i className="bi bi-collection me-2"></i>Схожі товари
          </h3>
          <div className="row g-3">
            {relatedProducts.slice(0, 4).map((relatedProduct) => (
              <div key={relatedProduct.id} className="col-6 col-md-4 col-lg-3">
                <ProductCard product={relatedProduct} />
              </div>
            ))}
          </div>
        </div>
      )}

      {recommendations.length > 0 && (
        <div className="mb-4">
          <h3 className="h5 mb-4">
            <i className="bi bi-bag-check me-2"></i>Клієнти також купували
          </h3>
          <div className="row g-3">
            {recommendations.map((rec) => (
              <div key={rec.id} className="col-6 col-md-4 col-lg-3">
                <ProductCard product={rec} />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-4 p-4 mb-4">
        <ProductReviews productSlug={slug} />
      </div>
    </>
  );
}

export default ProductPage;