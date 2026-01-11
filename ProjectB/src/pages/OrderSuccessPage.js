import React from 'react';
import { Link, useParams } from 'react-router-dom';

const OrderSuccessPage = () => {
    const { id } = useParams();

    return (
        <div className="container py-5">
            <div className="row justify-content-center">
                <div className="col-lg-6">
                    <div className="card border-0 shadow-sm">
                        <div className="card-body p-5 text-center">
                            <div className="mb-4">
                                <i
                                    className="bi bi-check-circle-fill text-success"
                                    style={{ fontSize: '80px' }}
                                ></i>
                            </div>

                            <h2 className="fw-bold mb-3">Дякуємо за замовлення!</h2>
                            <p className="text-muted mb-4">
                                Ваше замовлення #{id} успішно оформлено.<br />
                                Ми надіслали деталі на вашу електронну пошту.
                            </p>

                            <div className="d-flex gap-3 justify-content-center flex-wrap">
                                <Link
                                    to={`/orders/${id}`}
                                    className="btn btn-outline-success"
                                >
                                    <i className="bi bi-eye me-2"></i>
                                    Переглянути замовлення
                                </Link>
                                <Link
                                    to="/"
                                    className="btn btn-success"
                                >
                                    <i className="bi bi-arrow-left me-2"></i>
                                    Продовжити покупки
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OrderSuccessPage;