import React from 'react';
import { Link } from 'react-router-dom';

function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="row">
          <div className="col-lg-3 col-md-6 mb-4">
            <h5 className="footer-title">Покупцям</h5>
            <Link to="#" className="footer-link">Як зробити замовлення</Link>
            <Link to="#" className="footer-link">Способи оплати</Link>
            <Link to="#" className="footer-link">Доставка</Link>
            <Link to="#" className="footer-link">Повернення товару</Link>
            <Link to="#" className="footer-link">Питання та відповіді</Link>
          </div>
          <div className="col-lg-3 col-md-6 mb-4">
            <h5 className="footer-title">Продавцям</h5>
            <Link to="#" className="footer-link">Як стати продавцем</Link>
            <Link to="#" className="footer-link">Правила роботи</Link>
            <Link to="#" className="footer-link">Тарифи</Link>
          </div>
          <div className="col-lg-3 col-md-6 mb-4">
            <h5 className="footer-title">Про нас</h5>
            <Link to="#" className="footer-link">Про маркетплейс</Link>
            <Link to="#" className="footer-link">Контакти</Link>
            <Link to="#" className="footer-link">Вакансії</Link>
          </div>
          <div className="col-lg-3 col-md-6 mb-4">
            <h5 className="footer-title">Контакти</h5>
            <p className="footer-link">
              <i className="bi bi-telephone me-2"></i>0 800 123 456
            </p>
            <p className="footer-link">
              <i className="bi bi-envelope me-2"></i>info@market.ua
            </p>
            <div className="d-flex gap-3 mt-3">
              <a href="#" className="text-white fs-4"><i className="bi bi-facebook"></i></a>
              <a href="#" className="text-white fs-4"><i className="bi bi-instagram"></i></a>
              <a href="#" className="text-white fs-4"><i className="bi bi-telegram"></i></a>
            </div>
          </div>
        </div>

        <div className="d-flex justify-content-center gap-4 py-4 border-top border-secondary">
          <div className="bg-white rounded px-3 py-2 d-flex align-items-center">
            <i className="bi bi-credit-card-2-front text-primary me-2"></i>
            <span className="text-dark fw-medium" style={{ fontSize: '14px' }}>Visa</span>
          </div>
          <div className="bg-white rounded px-3 py-2 d-flex align-items-center">
            <i className="bi bi-credit-card text-warning me-2"></i>
            <span className="text-dark fw-medium" style={{ fontSize: '14px' }}>Mastercard</span>
          </div>
          <div className="bg-white rounded px-3 py-2 d-flex align-items-center">
            <i className="bi bi-bank text-success me-2"></i>
            <span className="text-dark fw-medium" style={{ fontSize: '14px' }}>Приват24</span>
          </div>
        </div>

        <div className="text-center text-muted pt-3">
          <small style={{ color: 'rgba(255,255,255,0.5)' }}>
            © 2026 Market — маркетплейс України
          </small>
        </div>
      </div>
    </footer>
  );
}

export default Footer;