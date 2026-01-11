import React, { createContext, useState, useEffect, useContext } from 'react';
import { cartAPI } from '../services/api';
import { toast } from 'react-toastify';

export const CartContext = createContext();

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState({ items: [], total_items: 0, subtotal: 0 });
  const [loading, setLoading] = useState(true);

  const fetchCart = async () => {
    try {
      const response = await cartAPI.get();
      setCart(response.data);
    } catch (error) {
      console.error('Error fetching cart:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const addToCart = async (productId, quantity = 1, sizeId = null) => {
    try {
      const response = await cartAPI.add(productId, quantity, sizeId);
      const cartData = response.data.cart || response.data;
      setCart(cartData);
      toast.success('Товар додано до кошика');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail ||
                     error.response?.data?.product_id?.[0] ||
                     error.response?.data?.product_size_id?.[0] ||
                     'Помилка додавання товару';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const updateQuantity = async (itemId, quantity) => {
    if (quantity < 1) return;

    try {
      const response = await cartAPI.update(itemId, quantity);
      const cartData = response.data.cart || response.data;
      setCart(cartData);
    } catch (error) {
      toast.error('Помилка оновлення кількості');
    }
  };

  const removeFromCart = async (itemId) => {
    try {
      const response = await cartAPI.remove(itemId);
      const cartData = response.data.cart || response.data;
      setCart(cartData);
      toast.success('Товар видалено з кошика');
    } catch (error) {
      toast.error('Помилка видалення товару');
    }
  };

  const clearCart = async () => {
    try {
      const response = await cartAPI.clear();
      const cartData = response.data.cart || response.data;
      setCart(cartData);
      toast.success('Кошик очищено');
    } catch (error) {
      toast.error('Помилка очищення кошика');
    }
  };

  const totalItems = cart?.total_items || 0;

  const value = {
    cart,
    loading,
    totalItems,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    fetchCart,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};