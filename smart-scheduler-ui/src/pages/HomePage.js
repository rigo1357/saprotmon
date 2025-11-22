// src/pages/HomePage.js
import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import './HomePage.css';

function HomePage() {
  const features = [
    {
      icon: '📅',
      title: 'Xếp lịch tự động',
      description: 'Hệ thống sử dụng giải thuật di truyền để tự động tạo thời khóa biểu tối ưu, ưu tiên ngày rảnh và tránh trùng lịch một cách thông minh.'
    },
    {
      icon: '🤖',
      title: 'Trợ lý AI',
      description: 'Chatbot thông minh hỗ trợ tư vấn về môn học, xếp lịch và giải đáp mọi thắc mắc. Lưu lịch sử chat và tìm kiếm dễ dàng.'
    },
    {
      icon: '⚡',
      title: 'Tối ưu hóa',
      description: 'Tự động cân bằng số môn học giữa các ngày, ưu tiên môn học lại, và tối ưu hóa lịch học theo nhu cầu của bạn.'
    },
    {
      icon: '📊',
      title: 'Quản lý môn học',
      description: 'Chọn môn học từ danh sách phong phú, lọc theo học kỳ và chuyên ngành. Hỗ trợ nhiều ngành học khác nhau.'
    },
    {
      icon: '📄',
      title: 'Xuất file',
      description: 'Xuất thời khóa biểu ra file PDF hoặc Excel để lưu trữ, in ấn và chia sẻ với bạn bè một cách tiện lợi.'
    },
    {
      icon: '🎯',
      title: 'Tùy chỉnh linh hoạt',
      description: 'Thiết lập thời gian rảnh, ưu tiên môn học, ràng buộc bổ sung và nhiều tùy chọn khác để có lịch học phù hợp nhất.'
    }
  ];

  const steps = [
    {
      number: '1',
      title: 'Chọn học kỳ và môn học',
      description: 'Nhập thông tin học kỳ, chuyên ngành và chọn các môn học bạn muốn đăng ký từ danh sách có sẵn.'
    },
    {
      number: '2',
      title: 'Thiết lập thời gian rảnh',
      description: 'Chọn các khung giờ rảnh trong tuần. Hệ thống sẽ ưu tiên xếp môn học vào những thời gian này.'
    },
    {
      number: '3',
      title: 'Tùy chỉnh ràng buộc',
      description: 'Thiết lập các ràng buộc như tránh môn liên tiếp, cân bằng ngày học, ưu tiên buổi sáng...'
    },
    {
      number: '4',
      title: 'Nhận kết quả tối ưu',
      description: 'Hệ thống sử dụng giải thuật di truyền để tạo lịch học tối ưu và xuất file PDF/Excel.'
    }
  ];

  return (
    <div className="homepage-container">
      {/* Navigation Bar */}
      <nav className="navbar">
        <div className="navbar-logo">
          <span>🎓</span>
          <span>PTT Smart Scheduler</span>
        </div>
        <div className="navbar-links">
          <Link to="/" className="navbar-link">Trang chủ</Link>
          <Link to="/login" className="navbar-button">Đăng nhập</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="hero-title">
            Xếp Lịch Học Thông Minh
            <br />
            Với AI & Giải Thuật Di Truyền
          </h1>
          <p className="hero-subtitle">
            Giải pháp tự động hóa việc tạo thời khóa biểu, giúp bạn tiết kiệm thời gian và có lịch học tối ưu nhất
          </p>
          <div className="hero-buttons">
            <Link to="/login">
              <motion.button
                className="hero-button-primary"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Bắt đầu ngay
              </motion.button>
            </Link>
            <motion.a
              href="#features"
              className="hero-button-secondary"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Tìm hiểu thêm
            </motion.a>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="section-title">Tính năng nổi bật</h2>
          <p className="section-subtitle">
            Những tính năng mạnh mẽ giúp bạn tạo thời khóa biểu hoàn hảo
          </p>
          <div className="features-grid">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                className="feature-card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                whileHover={{ scale: 1.02 }}
              >
                <span className="feature-icon">{feature.icon}</span>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <motion.div
          className="stats-grid"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className="stat-item"
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1, duration: 0.5 }}
          >
            <span className="stat-number">100%</span>
            <span className="stat-label">Tự động hóa</span>
          </motion.div>
          <motion.div
            Link to="/login"
            className="stat-item"
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <span className="stat-number">AI</span>
            <span className="stat-label">Trợ lý thông minh</span>
          </motion.div>
          <motion.div
            className="stat-item"
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            <span className="stat-number">24/7</span>
            <span className="stat-label">Hỗ trợ</span>
          </motion.div>
          <motion.div
            className="stat-item"
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4, duration: 0.5 }}
          >
            <span className="stat-number">∞</span>
            <span className="stat-label">Tùy chỉnh</span>
          </motion.div>
        </motion.div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="section-title">Cách sử dụng</h2>
          <p className="section-subtitle">
            Chỉ với 4 bước đơn giản để có thời khóa biểu tối ưu
          </p>
          <div className="steps-container">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                className="step-item"
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.15, duration: 0.6 }}
              >
                <div className="step-number">{step.number}</div>
                <div className="step-content">
                  <h3>{step.title}</h3>
                  <p>{step.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="cta-title">Sẵn sàng bắt đầu?</h2>
          <p className="cta-description">
            Đăng nhập ngay để trải nghiệm hệ thống xếp lịch học thông minh và tiết kiệm thời gian của bạn
          </p>
          <Link to="/login">
            <motion.button
              className="cta-button"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Đăng nhập ngay →
            </motion.button>
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p className="footer-text">
          © 2024 PTT Smart Scheduler. Giải pháp xếp lịch học thông minh.
        </p>
      </footer>
    </div>
  );
}

export default HomePage;
