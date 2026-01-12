import React, { useState, useEffect } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import { productsAPI, categoriesAPI } from '../services/api';
import api from '../services/api';

function CatalogPage() {
  const { categorySlug } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [sizes, setSizes] = useState([]);
  const [currentCategory, setCurrentCategory] = useState(null);
  const [loading, setLoading] = useState(true);

  const [minPrice, setMinPrice] = useState(searchParams.get('min_price') || '');
  const [maxPrice, setMaxPrice] = useState(searchParams.get('max_price') || '');
  const [color, setColor] = useState(searchParams.get('color') || '');
  const [size, setSize] = useState(searchParams.get('size') || '');
  const [inStock, setInStock] = useState(searchParams.get('in_stock') === 'true');
  const [sort, setSort] = useState(searchParams.get('sort') || 'newest');
  const searchQuery = searchParams.get('q') || '';

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const categoriesRes = await categoriesAPI.getAll();
        setCategories(categoriesRes.data);

        try {
          const sizesRes = await api.get('/sizes/');
          setSizes(sizesRes.data || []);
        } catch (e) {
          console.log('Sizes not available');
        }

        if (categorySlug) {
          const cat = categoriesRes.data.find(c => c.slug === categorySlug);
          setCurrentCategory(cat);
        } else {
          setCurrentCategory(null);
        }

        const params = {};
        if (categorySlug) params.category_slug = categorySlug;
        if (searchQuery) params.search = searchQuery;
        if (minPrice) params.min_price = minPrice;
        if (maxPrice) params.max_price = maxPrice;
        if (color) params.color = color;
        if (size) params.size = size;
        if (inStock) params.in_stock = 'true';

        switch (sort) {
          case 'price_asc':
            params.ordering = 'price';
            break;
          case 'price_desc':
            params.ordering = '-price';
            break;
          case 'popular':
            params.ordering = '-views_count';
            break;
          default:
            params.ordering = '-created_at';
        }

        const productsRes = await productsAPI.getAll(params);
        setProducts(productsRes.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [categorySlug, searchParams, sort, minPrice, maxPrice, color, size, inStock, searchQuery]);

  const handleApplyFilters = (e) => {
    e.preventDefault();
    const newParams = new URLSearchParams();
    if (searchQuery) newParams.set('q', searchQuery);
    if (minPrice) newParams.set('min_price', minPrice);
    if (maxPrice) newParams.set('max_price', maxPrice);
    if (color) newParams.set('color', color);
    if (size) newParams.set('size', size);
    if (inStock) newParams.set('in_stock', 'true');
    if (sort !== 'newest') newParams.set('sort', sort);
    setSearchParams(newParams);
  };

  const handleResetFilters = () => {
    setMinPrice('');
    setMaxPrice('');
    setColor('');
    setSize('');
    setInStock(false);
    setSort('newest');
    setSearchParams(new URLSearchParams());
  };

  const handleSortChange = (e) => {
    setSort(e.target.value);
    const newParams = new URLSearchParams(searchParams);
    newParams.set('sort', e.target.value);
    setSearchParams(newParams);
  };

  return (
    <>
      {/* Breadcrumbs */}
      <nav aria-label="breadcrumb" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item">
            <Link to="/">
              <i className="bi bi-house-fill me-1"></i>Головна
            </Link>
          </li>
          <li className="breadcrumb-item">
            <Link to="/catalog">Каталог</Link>
          </li>
          {currentCategory && (
            <li className="breadcrumb-item active" aria-current="page">
              {currentCategory.name}
            </li>
          )}
        </ol>
      </nav>

      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3 mb-0">
          {currentCategory ? currentCategory.name : 'Всі товари'}
          {searchQuery && (
            <small className="text-muted fs-6"> — результати пошуку "{searchQuery}"</small>
          )}
        </h1>
        <span className="text-muted">{products.length} товарів</span>
      </div>

      <div className="row">
        {/* Sidebar Filters */}
        <div className="col-lg-3 mb-4">
          <div className="filter-sidebar">
            <h5 className="filter-title">
              <i className="bi bi-funnel me-2"></i>Фільтри
            </h5>

            <form onSubmit={handleApplyFilters}>
              {/* Price Filter */}
              <div className="filter-section">
                <h6 className="filter-section-title">Ціна, ₴</h6>
                <div className="price-inputs">
                  <input
                    type="number"
                    placeholder="Від"
                    value={minPrice}
                    onChange={(e) => setMinPrice(e.target.value)}
                    min="0"
                  />
                  <span>—</span>
                  <input
                    type="number"
                    placeholder="До"
                    value={maxPrice}
                    onChange={(e) => setMaxPrice(e.target.value)}
                    min="0"
                  />
                </div>
              </div>

              <div className="filter-section">
                <h6 className="filter-section-title">Колір</h6>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Введіть колір"
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                />
              </div>

              {(currentCategory?.requires_size || !categorySlug) && sizes.length > 0 && (
                <div className="filter-section">
                  <h6 className="filter-section-title">Розмір</h6>
                  <select
                    className="form-select"
                    value={size}
                    onChange={(e) => setSize(e.target.value)}
                  >
                    <option value="">Всі розміри</option>
                    {sizes.map(s => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="filter-section">
                <div className="form-check">
                  <input
                    type="checkbox"
                    className="form-check-input"
                    id="inStock"
                    checked={inStock}
                    onChange={(e) => setInStock(e.target.checked)}
                  />
                  <label className="form-check-label" htmlFor="inStock">
                    Тільки в наявності
                  </label>
                </div>
              </div>

              <button type="submit" className="btn btn-apply-filter">
                <i className="bi bi-check2 me-1"></i>Застосувати
              </button>

              <button
                type="button"
                className="btn btn-outline-secondary w-100 mt-2"
                onClick={handleResetFilters}
              >
                <i className="bi bi-x-lg me-1"></i>Скинути
              </button>
            </form>
          </div>

          <div className="filter-sidebar mt-4">
            <h5 className="filter-title">
              <i className="bi bi-list me-2"></i>Категорії
            </h5>
            <ul className="list-unstyled mb-0">
              <li className="mb-2">
                <Link
                  to="/catalog"
                  className={`text-decoration-none ${!categorySlug ? 'fw-bold text-success' : 'text-dark'}`}
                >
                  <i className="bi bi-grid-3x3-gap me-2"></i>Всі товари
                </Link>
              </li>
              {categories.map((category) => (
                <li key={category.id} className="mb-2">
                  <Link
                    to={`/catalog/${category.slug}`}
                    className={`text-decoration-none ${categorySlug === category.slug ? 'fw-bold text-success' : 'text-dark'}`}
                  >
                    <i className="bi bi-chevron-right me-2"></i>
                    {category.name}
                    <span className="text-muted"> ({category.products_count || 0})</span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="col-lg-9">
          <div className="bg-white rounded-3 p-3 mb-4 d-flex justify-content-between align-items-center">
            <div className="d-flex gap-2 align-items-center">
              <span className="text-muted me-2">Сортування:</span>
              <select
                className="form-select"
                style={{ width: 'auto' }}
                value={sort}
                onChange={handleSortChange}
              >
                <option value="newest">Новинки</option>
                <option value="price_asc">Дешевші</option>
                <option value="price_desc">Дорожчі</option>
                <option value="popular">Популярні</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className="loading-spinner">
              <div className="spinner-border text-success" role="status">
                <span className="visually-hidden">Завантаження...</span>
              </div>
            </div>
          ) : products.length > 0 ? (
            <div className="row g-3">
              {products.map((product) => (
                <div key={product.id} className="col-6 col-md-4 col-xl-3">
                  <ProductCard product={product} />
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-4 p-5 text-center">
              <i className="bi bi-search text-muted" style={{ fontSize: '64px' }}></i>
              <h5 className="mt-3 text-muted">Товари не знайдено</h5>
              <p className="text-muted mb-4">Спробуйте змінити параметри пошуку або фільтри</p>
              <Link to="/catalog" className="btn btn-success" onClick={handleResetFilters}>
                <i className="bi bi-arrow-left me-1"></i>Показати всі товари
              </Link>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default CatalogPage;