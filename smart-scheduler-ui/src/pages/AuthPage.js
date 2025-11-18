// src/pages/AuthPage.js
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './AuthPage.css';

const features = [
  { title: 'Tạo lịch thông minh', description: 'Ưu tiên môn quan trọng, cân bằng thời khóa biểu của bạn.' },
  { title: 'Giáo trình cập nhật', description: 'Môn học được admin upload từ PDF/Excel/CSV chính thức.' },
  { title: 'Chatbot trợ lý', description: 'Giải đáp mọi câu hỏi về đăng ký học phần hoặc GA.' },
];

const ADMIN_USERNAME = 'admin';
const ADMIN_PASSWORD = 'Admin@123';

function AuthPage() {
  const [mode, setMode] = useState('login'); // login | register | forgot-password
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [authMessage, setAuthMessage] = useState('');
  
  // State cho quên mật khẩu
  const [forgotStep, setForgotStep] = useState(1); // 1: nhập email/phone, 2: nhập OTP, 3: đặt lại mật khẩu
  const [forgotIdentifier, setForgotIdentifier] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmNewPassword, setShowConfirmNewPassword] = useState(false);

  const { login } = useAuth();

  const switchMode = (nextMode) => {
    setMode(nextMode);
    setAuthMessage('');
    setPassword('');
    setConfirmPassword('');
    setFullName('');
    setEmail('');
    setPhone('');
    // Reset forgot password state
    setForgotStep(1);
    setForgotIdentifier('');
    setOtpCode('');
    setNewPassword('');
    setConfirmNewPassword('');
  };

  const fillAdminCredentials = () => {
    setMode('login');
    setUsername(ADMIN_USERNAME);
    setPassword(ADMIN_PASSWORD);
    setConfirmPassword(ADMIN_PASSWORD);
    setAuthMessage('Đã tự động điền tài khoản quản trị mặc định.');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setAuthMessage('');
    const success = await login(username.trim(), password);
    if (!success) {
      setAuthMessage('Đăng nhập không thành công. Vui lòng kiểm tra lại thông tin hoặc thử lại sau.');
    }
    setIsSubmitting(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setAuthMessage('');

    // Validation
    if (!fullName.trim()) {
      setAuthMessage('Vui lòng nhập Họ và Tên.');
      return;
    }
    if (!username.trim()) {
      setAuthMessage('Vui lòng nhập Tên đăng nhập.');
      return;
    }
    if (password.length < 6) {
      setAuthMessage('Mật khẩu cần tối thiểu 6 ký tự.');
      return;
    }
    if (password !== confirmPassword) {
      setAuthMessage('Mật khẩu xác nhận không khớp.');
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        full_name: fullName.trim(),
        username: username.trim(),
        password,
        confirm_password: confirmPassword,
        email: email.trim() || null,
        phone: phone.trim() || null,
      };
      const response = await api.post('/api/register', payload);
      if (response.status === 201) {
        setAuthMessage('🎉 Đăng ký thành công! Vui lòng đăng nhập.');
        // Tự động quay lại login sau 1.5 giây
        setTimeout(() => {
          switchMode('login');
          setUsername('');
          setPassword('');
          setConfirmPassword('');
          setFullName('');
          setEmail('');
          setPhone('');
        }, 1500);
      }
    } catch (error) {
      console.error('Lỗi đăng ký:', error);
      const detail = error.response?.data?.detail;
      if (Array.isArray(detail)) {
        setAuthMessage(detail.map((err) => `${err.loc?.join('.')}: ${err.msg}`).join('\n'));
      } else if (typeof detail === 'string') {
        setAuthMessage(detail);
      } else if (error.response?.data?.message) {
        setAuthMessage(error.response.data.message);
      } else {
        setAuthMessage(error.message || 'Có lỗi không xác định.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Quên mật khẩu - Bước 1: Gửi OTP
  const handleForgotPasswordRequest = async (e) => {
    e.preventDefault();
    setAuthMessage('');
    
    if (!forgotIdentifier.trim()) {
      setAuthMessage('Vui lòng nhập email hoặc số điện thoại.');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.post('/api/forgot-password/request', {
        identifier: forgotIdentifier.trim()
      });
      setAuthMessage(response.data.message || 'Mã OTP đã được gửi. Vui lòng kiểm tra email/số điện thoại.');
      setForgotStep(2);
    } catch (error) {
      console.error('Lỗi gửi OTP:', error);
      const detail = error.response?.data?.detail || error.message || 'Có lỗi khi gửi mã OTP.';
      setAuthMessage(detail);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Quên mật khẩu - Bước 2: Xác nhận OTP
  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setAuthMessage('');
    
    if (!otpCode.trim() || otpCode.length !== 6) {
      setAuthMessage('Vui lòng nhập mã OTP 6 chữ số.');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.post('/api/forgot-password/verify', {
        identifier: forgotIdentifier.trim(),
        otp_code: otpCode.trim()
      });
      setAuthMessage(response.data.message || 'Mã OTP hợp lệ. Vui lòng đặt lại mật khẩu.');
      setForgotStep(3);
    } catch (error) {
      console.error('Lỗi xác nhận OTP:', error);
      const detail = error.response?.data?.detail || error.message || 'Mã OTP không hợp lệ.';
      setAuthMessage(detail);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Quên mật khẩu - Bước 3: Đặt lại mật khẩu
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setAuthMessage('');
    
    if (newPassword.length < 6) {
      setAuthMessage('Mật khẩu cần tối thiểu 6 ký tự.');
      return;
    }
    if (newPassword !== confirmNewPassword) {
      setAuthMessage('Mật khẩu xác nhận không khớp.');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.post('/api/forgot-password/reset', {
        identifier: forgotIdentifier.trim(),
        otp_code: otpCode.trim(),
        new_password: newPassword,
        confirm_password: confirmNewPassword
      });
      setAuthMessage('✅ ' + (response.data.message || 'Đặt lại mật khẩu thành công. Vui lòng đăng nhập.'));
      // Quay lại login sau 2 giây
      setTimeout(() => {
        switchMode('login');
      }, 2000);
    } catch (error) {
      console.error('Lỗi đặt lại mật khẩu:', error);
      const detail = error.response?.data?.detail || error.message || 'Có lỗi khi đặt lại mật khẩu.';
      setAuthMessage(detail);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderInput = ({
    label,
    type = 'text',
    placeholder = '',
    value,
    onChange,
    required,
    addon,
  }) => (
    <div className="auth-form-group">
      <label className="auth-form-label">{label}</label>
      <div className="auth-password-wrapper">
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          required={required}
          className="auth-form-input"
        />
        {addon}
      </div>
    </div>
  );

  return (
    <div className="auth-page-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="auth-container"
      >
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="auth-left-panel"
        >
          <h1 className="auth-welcome-title">🎓 Smart Scheduler</h1>
          <p className="auth-welcome-subtitle">
            Tối ưu thời khóa biểu, tiết kiệm thời gian đăng ký học phần với trợ lý thông minh.
          </p>
          <ul className="auth-features-list">
            {features.map((feature, index) => (
              <motion.li
                key={feature.title}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1, duration: 0.5 }}
                className="auth-feature-item"
              >
                <span className="auth-feature-icon">
                  {index === 0 ? '📅' : index === 1 ? '📚' : '💬'}
                </span>
                <div className="auth-feature-content">
                  <h4>{feature.title}</h4>
                  <p>{feature.description}</p>
                </div>
              </motion.li>
            ))}
          </ul>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="auth-admin-hint"
          >
            <h4 style={{ marginTop: 0, marginBottom: '10px' }}>🔑 Tài khoản quản trị mặc định</h4>
            <p style={{ margin: '6px 0', fontSize: '0.95rem' }}>
              Username: <strong>{ADMIN_USERNAME}</strong> – Password: <strong>{ADMIN_PASSWORD}</strong>
            </p>
            <button
              type="button"
              onClick={fillAdminCredentials}
              className="auth-admin-button"
            >
              Điền thông tin admin
            </button>
          </motion.div>
          <Link to="/" className="auth-back-link">
            ← Về trang chủ
          </Link>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="auth-right-panel"
        >
          <div className="auth-tabs">
            <button
              type="button"
              onClick={() => switchMode('login')}
              className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
            >
              Đăng nhập
            </button>
            <button
              type="button"
              onClick={() => switchMode('register')}
              className={`auth-tab ${mode === 'register' ? 'active' : ''}`}
            >
              Đăng ký
            </button>
          </div>
          
          {mode === 'login' && (
            <button
              type="button"
              onClick={() => switchMode('forgot-password')}
              style={{
                background: 'none',
                border: 'none',
                color: '#667eea',
                cursor: 'pointer',
                fontSize: '0.9rem',
                marginTop: '10px',
                textDecoration: 'underline',
                padding: '5px 0'
              }}
            >
              Quên mật khẩu?
            </button>
          )}

          {authMessage && (
            <div
              className={`auth-message ${
                authMessage.includes('thành công') || authMessage.includes('🎉')
                  ? 'success'
                  : authMessage.includes('⚠️') || authMessage.includes('thông tin')
                  ? 'info'
                  : 'error'
              }`}
            >
              {authMessage}
            </div>
          )}

          {mode === 'login' ? (
            <form onSubmit={handleLogin} className="auth-form">
              {renderInput({
                label: 'Tên đăng nhập',
                type: 'text',
                placeholder: 'ví dụ: sinhvien123',
                value: username,
                onChange: (e) => setUsername(e.target.value),
                required: true,
              })}
              {renderInput({
                label: 'Mật khẩu',
                type: showPassword ? 'text' : 'password',
                placeholder: '••••••••',
                value: password,
                onChange: (e) => setPassword(e.target.value),
                required: true,
                addon: (
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="auth-password-toggle"
                  >
                    {showPassword ? '👁️' : '👁️‍🗨️'}
                  </button>
                ),
              })}
              <motion.button
                type="submit"
                disabled={isSubmitting}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="auth-submit-button"
              >
                {isSubmitting ? 'Đang đăng nhập...' : 'Đăng nhập'}
              </motion.button>
            </form>
          ) : mode === 'register' ? (
            <form onSubmit={handleRegister} className="auth-form">
              {renderInput({
                label: 'Họ và Tên *',
                type: 'text',
                placeholder: 'Nhập họ và tên đầy đủ',
                value: fullName,
                onChange: (e) => setFullName(e.target.value),
                required: true,
              })}
              {renderInput({
                label: 'Tên đăng nhập *',
                type: 'text',
                placeholder: 'ví dụ: sinhvien123',
                value: username,
                onChange: (e) => setUsername(e.target.value),
                required: true,
              })}
              {renderInput({
                label: 'Mật khẩu *',
                type: showPassword ? 'text' : 'password',
                placeholder: 'Tối thiểu 6 ký tự',
                value: password,
                onChange: (e) => setPassword(e.target.value),
                required: true,
                addon: (
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="auth-password-toggle"
                  >
                    {showPassword ? '👁️' : '👁️‍🗨️'}
                  </button>
                ),
              })}
              {renderInput({
                label: 'Xác nhận mật khẩu *',
                type: showConfirmPassword ? 'text' : 'password',
                placeholder: 'Nhập lại mật khẩu',
                value: confirmPassword,
                onChange: (e) => setConfirmPassword(e.target.value),
                required: true,
                addon: (
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword((prev) => !prev)}
                    className="auth-password-toggle"
                  >
                    {showConfirmPassword ? '👁️' : '👁️‍🗨️'}
                  </button>
                ),
              })}
              {renderInput({
                label: 'Email (tùy chọn)',
                type: 'email',
                placeholder: 'name@student.edu.vn',
                value: email,
                onChange: (e) => setEmail(e.target.value),
              })}
              {renderInput({
                label: 'Số điện thoại (tùy chọn)',
                type: 'tel',
                placeholder: '0123456789',
                value: phone,
                onChange: (e) => setPhone(e.target.value),
              })}
              <motion.button
                type="submit"
                disabled={isSubmitting}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="auth-submit-button"
              >
                {isSubmitting ? 'Đang đăng ký...' : 'Tạo tài khoản'}
              </motion.button>
            </form>
          ) : (
            // Form quên mật khẩu
            <div className="auth-form">
              {forgotStep === 1 && (
                <form onSubmit={handleForgotPasswordRequest}>
                  <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#1e293b' }}>
                    Quên mật khẩu
                  </h3>
                  <p style={{ marginBottom: '20px', color: '#64748b', fontSize: '0.95rem' }}>
                    Nhập email hoặc số điện thoại đã đăng ký để nhận mã OTP.
                  </p>
                  {renderInput({
                    label: 'Email hoặc Số điện thoại',
                    type: 'text',
                    placeholder: 'email@example.com hoặc 0123456789',
                    value: forgotIdentifier,
                    onChange: (e) => setForgotIdentifier(e.target.value),
                    required: true,
                  })}
                  <motion.button
                    type="submit"
                    disabled={isSubmitting}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="auth-submit-button"
                  >
                    {isSubmitting ? 'Đang gửi...' : 'Gửi mã OTP'}
                  </motion.button>
                  <button
                    type="button"
                    onClick={() => switchMode('login')}
                    style={{
                      width: '100%',
                      marginTop: '10px',
                      padding: '12px',
                      background: 'transparent',
                      border: '2px solid #e2e8f0',
                      borderRadius: '12px',
                      color: '#64748b',
                      cursor: 'pointer',
                      fontSize: '1rem',
                      fontWeight: '500'
                    }}
                  >
                    Quay lại đăng nhập
                  </button>
                </form>
              )}
              
              {forgotStep === 2 && (
                <form onSubmit={handleVerifyOTP}>
                  <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#1e293b' }}>
                    Nhập mã OTP
                  </h3>
                  <p style={{ marginBottom: '20px', color: '#64748b', fontSize: '0.95rem' }}>
                    Mã OTP đã được gửi đến <strong>{forgotIdentifier}</strong>. Vui lòng kiểm tra và nhập mã 6 chữ số.
                  </p>
                  {renderInput({
                    label: 'Mã OTP',
                    type: 'text',
                    placeholder: '123456',
                    value: otpCode,
                    onChange: (e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6)),
                    required: true,
                  })}
                  <motion.button
                    type="submit"
                    disabled={isSubmitting || otpCode.length !== 6}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="auth-submit-button"
                  >
                    {isSubmitting ? 'Đang xác nhận...' : 'Xác nhận OTP'}
                  </motion.button>
                  <button
                    type="button"
                    onClick={() => setForgotStep(1)}
                    style={{
                      width: '100%',
                      marginTop: '10px',
                      padding: '12px',
                      background: 'transparent',
                      border: '2px solid #e2e8f0',
                      borderRadius: '12px',
                      color: '#64748b',
                      cursor: 'pointer',
                      fontSize: '1rem',
                      fontWeight: '500'
                    }}
                  >
                    Gửi lại mã OTP
                  </button>
                </form>
              )}
              
              {forgotStep === 3 && (
                <form onSubmit={handleResetPassword}>
                  <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#1e293b' }}>
                    Đặt lại mật khẩu
                  </h3>
                  <p style={{ marginBottom: '20px', color: '#64748b', fontSize: '0.95rem' }}>
                    Nhập mật khẩu mới của bạn.
                  </p>
                  {renderInput({
                    label: 'Mật khẩu mới',
                    type: showNewPassword ? 'text' : 'password',
                    placeholder: 'Tối thiểu 6 ký tự',
                    value: newPassword,
                    onChange: (e) => setNewPassword(e.target.value),
                    required: true,
                    addon: (
                      <button
                        type="button"
                        onClick={() => setShowNewPassword((prev) => !prev)}
                        className="auth-password-toggle"
                      >
                        {showNewPassword ? '👁️' : '👁️‍🗨️'}
                      </button>
                    ),
                  })}
                  {renderInput({
                    label: 'Xác nhận mật khẩu mới',
                    type: showConfirmNewPassword ? 'text' : 'password',
                    placeholder: 'Nhập lại mật khẩu mới',
                    value: confirmNewPassword,
                    onChange: (e) => setConfirmNewPassword(e.target.value),
                    required: true,
                    addon: (
                      <button
                        type="button"
                        onClick={() => setShowConfirmNewPassword((prev) => !prev)}
                        className="auth-password-toggle"
                      >
                        {showConfirmNewPassword ? '👁️' : '👁️‍🗨️'}
                      </button>
                    ),
                  })}
                  <motion.button
                    type="submit"
                    disabled={isSubmitting}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="auth-submit-button"
                  >
                    {isSubmitting ? 'Đang đặt lại...' : 'Đặt lại mật khẩu'}
                  </motion.button>
                </form>
              )}
            </div>
          )}
        </motion.div>
      </motion.div>
    </div>
  );
}

export default AuthPage;