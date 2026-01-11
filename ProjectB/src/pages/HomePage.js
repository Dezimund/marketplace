import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import { productsAPI, categoriesAPI } from '../services/api';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';

function HomePage() {
  const { isAuthenticated } = useContext(AuthContext);
  const [categories, setCategories] = useState([]);
  const [recommendedProducts, setRecommendedProducts] = useState([]);
  const [newProducts, setNewProducts] = useState([]);
  const [bestsellers, setBestsellers] = useState([]);
  const [trending, setTrending] = useState([]);
  const [forYou, setForYou] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [categoriesRes, recommendedRes, newRes, bestsellersRes] = await Promise.all([
          categoriesAPI.getAll(),
          productsAPI.getRecommended(),
          productsAPI.getNew(),
          productsAPI.getBestsellers()
        ]);

        setCategories(categoriesRes.data);
        setRecommendedProducts(recommendedRes.data);
        setNewProducts(newRes.data);
        setBestsellers(bestsellersRes.data);

        // ML Recommendations
        try {
          const trendingRes = await api.get('/recommendations/?type=trending&limit=6');
          setTrending(trendingRes.data.products || []);
        } catch (e) {
          console.log('Trending not available');
        }

        // Персоналізовані рекомендації для авторизованого користувача
        if (isAuthenticated) {
          try {
            const forYouRes = await api.get('/recommendations/?type=for_user&limit=6');
            setForYou(forYouRes.data.products || []);
          } catch (e) {
            console.log('Personal recommendations not available');
          }
        }

      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isAuthenticated]);

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner-border text-success" role="status">
          <span className="visually-hidden">Завантаження...</span>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="row mb-4">
        <div className="col-12">
          <div className="hero-banner p-4 p-lg-5">
            <div className="row align-items-center">
              <div className="col-lg-6 text-white">
                <h1 className="display-5 fw-bold mb-3">Ласкаво просимо до Market!</h1>
                <p className="lead mb-4">Найкращі товари від перевірених продавців з усієї України</p>
                <Link to="/catalog" className="btn btn-light btn-lg px-5 rounded-pill">
                  <i className="bi bi-arrow-right me-2"></i>Перейти до каталогу
                </Link>
              </div>
              <div className="col-lg-6 d-none d-lg-block text-center">
                <i className="bi bi-box-seam-fill text-white" style={{ fontSize: '180px', opacity: 0.3 }}></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <section className="mb-5">
        <h2 className="h4 mb-4 fw-bold">
          <i className="bi bi-grid-3x3-gap-fill text-success me-2"></i>Популярні категорії
        </h2>
        <div className="row g-3">
          {categories.length > 0 ? (
            categories.map((category) => (
              <div key={category.id} className="col-6 col-md-4 col-lg-3 col-xl-2">
                <Link to={`/catalog/${category.slug}`} className="text-decoration-none">
                  <div className="bg-white rounded-4 p-4 text-center h-100 category-card">
                    <div className="mb-3">
                      <i className="bi bi-tag-fill text-success" style={{ fontSize: '48px' }}></i>
                    </div>
                    <h6 className="text-dark mb-0">{category.name}</h6>
                    <small className="text-muted">{category.products_count || 0} товарів</small>
                  </div>
                </Link>
              </div>
            ))
          ) : (
            <div className="col-12">
              <div className="alert alert-info">Категорії ще не додані</div>
            </div>
          )}
        </div>
      </section>

      {forYou.length > 0 && (
        <section className="mb-5">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2 className="h4 mb-0 fw-bold">
              <i className="bi bi-person-heart text-primary me-2"></i>Рекомендовано для вас
            </h2>
          </div>
          <div className="row g-3">
            {forYou.slice(0, 6).map((product) => (
              <div key={product.id} className="col-6 col-md-4 col-lg-3 col-xl-2">
                <ProductCard product={product} />
              </div>
            ))}
          </div>
        </section>
      )}

      {trending.length > 0 && (
        <section className="mb-5">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2 className="h4 mb-0 fw-bold">
              <i className="bi bi-graph-up-arrow text-success me-2"></i>Зараз у тренді
            </h2>
          </div>
          <div className="row g-3">
            {trending.slice(0, 6).map((product) => (
              <div key={product.id} className="col-6 col-md-4 col-lg-3 col-xl-2">
                <ProductCard product={product} />
              </div>
            ))}
          </div>
        </section>
      )}

      {recommendedProducts.length > 0 && (
        <section className="mb-5">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2 className="h4 mb-0 fw-bold">
              <i className="bi bi-star-fill text-warning me-2"></i>Рекомендовані товари
            </h2>
          </div>
          <div className="row g-3">
            {recommendedProducts.slice(0, 6).map((product) => (
              <div key={product.id} className="col-6 col-md-4 col-lg-3 col-xl-2">
                <ProductCard product={product} />
              </div>
            ))}
          </div>
        </section>
      )}

      {bestsellers.length > 0 && (
        <section className="mb-5">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2 className="h4 mb-0 fw-bold">
              <i className="bi bi-fire text-danger me-2"></i>Хіти продажів
            </h2>
          </div>
          <div className="row g-3">
            {bestsellers.slice(0, 6).map((product) => (
              <div key={product.id} className="col-6 col-md-4 col-lg-3 col-xl-2">
                <ProductCard product={product} />
              </div>
            ))}
          </div>
        </section>
      )}

      {newProducts.length > 0 && (
        <section className="mb-5">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2 className="h4 mb-0 fw-bold">
              <i className="bi bi-sparkles text-info me-2"></i>Новинки
            </h2>
          </div>
          <div className="row g-3">
            {newProducts.slice(0, 6).map((product) => (
              <div key={product.id} className="col-6 col-md-4 col-lg-3 col-xl-2">
                <ProductCard product={product} />
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="mb-5">
        <div className="row g-4">
          <div className="col-md-3">
            <div className="bg-white rounded-4 p-4 text-center h-100">
              <i className="bi bi-truck text-success" style={{ fontSize: '48px' }}></i>
              <h6 className="mt-3 mb-2">Швидка доставка</h6>
              <small className="text-muted">По всій Україні за 1-3 дні</small>
            </div>
          </div>
          <div className="col-md-3">
            <div className="bg-white rounded-4 p-4 text-center h-100">
              <i className="bi bi-shield-check text-success" style={{ fontSize: '48px' }}></i>
              <h6 className="mt-3 mb-2">Гарантія якості</h6>
              <small className="text-muted">Тільки перевірені продавці</small>
            </div>
          </div>
          <div className="col-md-3">
            <div className="bg-white rounded-4 p-4 text-center h-100">
              <i className="bi bi-credit-card text-success" style={{ fontSize: '48px' }}></i>
              <h6 className="mt-3 mb-2">Безпечна оплата</h6>
              <small className="text-muted">Різні способи оплати</small>
            </div>
          </div>
          <div className="col-md-3">
            <div className="bg-white rounded-4 p-4 text-center h-100">
              <i className="bi bi-arrow-counterclockwise text-success" style={{ fontSize: '48px' }}></i>
              <h6 className="mt-3 mb-2">Легке повернення</h6>
              <small className="text-muted">14 днів на повернення</small>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}

export default HomePage;