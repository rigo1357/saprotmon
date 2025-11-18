// src/pages/AdminPage.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './AdminPage.css';

function AdminPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [semester, setSemester] = useState('2023-2');
  const [department, setDepartment] = useState('');
  const [major, setMajor] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoadingCourses, setIsLoadingCourses] = useState(false);
  const [uploadInfo, setUploadInfo] = useState(null);
  const [courses, setCourses] = useState([]);
  const [error, setError] = useState(null);
  const [manualCourse, setManualCourse] = useState({
    code: '',
    name: '',
    credits: '',
    department: '',
    major: '',
  });
  const [manualMessage, setManualMessage] = useState(null);
  
  // State cho quản lý người dùng
  const [users, setUsers] = useState([]);
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);
  const [usersError, setUsersError] = useState(null);

  const fetchCourses = async () => {
    setIsLoadingCourses(true);
    try {
      const response = await api.get('/api/courses', {
        params: { semester, major: major || undefined },
      });
      setCourses(response.data?.items || []);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Không thể tải danh sách môn học. Vui lòng thử lại.');
    } finally {
      setIsLoadingCourses(false);
    }
  };

  useEffect(() => {
    fetchCourses();
    fetchUsers();
  }, [semester, major]);

  const fetchUsers = async () => {
    setIsLoadingUsers(true);
    setUsersError(null);
    try {
      const response = await api.get('/api/admin/users');
      setUsers(response.data?.users || []);
    } catch (err) {
      console.error('Lỗi tải danh sách người dùng:', err);
      setUsersError('Không thể tải danh sách người dùng. Vui lòng thử lại.');
    } finally {
      setIsLoadingUsers(false);
    }
  };

  const handleDeleteUser = async (userId, username) => {
    if (!window.confirm(`Bạn có chắc chắn muốn xóa người dùng "${username}"? Tất cả dữ liệu liên quan (lịch học, lịch sử chat) sẽ bị xóa vĩnh viễn.`)) {
      return;
    }
    
    try {
      await api.delete(`/api/admin/users/${userId}`);
      alert('Đã xóa người dùng thành công!');
      await fetchUsers();
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Xóa người dùng thất bại';
      alert(errorMessage);
    }
  };

  const handleToggleAdmin = async (userId, username, currentIsAdmin) => {
    const action = currentIsAdmin ? 'thu hồi quyền admin' : 'cấp quyền admin';
    if (!window.confirm(`Bạn có chắc chắn muốn ${action} cho người dùng "${username}"?`)) {
      return;
    }
    
    try {
      const response = await api.patch(`/api/admin/users/${userId}/toggle-admin`);
      alert(response.data.message);
      await fetchUsers();
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Thay đổi quyền admin thất bại';
      alert(errorMessage);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Vui lòng chọn file PDF/Excel/CSV');
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('semester', semester);
    if (department) {
      formData.append('department', department);
    }
    if (major) {
      formData.append('major', major);
    }
    formData.append('file', selectedFile);

    try {
      const response = await api.post('/api/admin/upload-courses', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setUploadInfo(response.data);
      setSelectedFile(null);
      await fetchCourses();
    } catch (err) {
      console.error(err);
      const errorMessage = err.response?.data?.detail || err.message || 'Upload thất bại';
      alert(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleManualSubmit = async () => {
    if (!manualCourse.code.trim() || !manualCourse.name.trim()) {
      setManualMessage({ type: 'error', text: 'Vui lòng nhập mã môn và tên môn.' });
      return;
    }
    const creditsValue = parseInt(manualCourse.credits || '0', 10);
    if (Number.isNaN(creditsValue) || creditsValue < 0) {
      setManualMessage({ type: 'error', text: 'Số tín chỉ phải là số không âm.' });
      return;
    }

    try {
      const payload = {
        code: manualCourse.code.trim().toUpperCase(),
        name: manualCourse.name.trim(),
        credits: creditsValue,
        semester: semester,
        department: manualCourse.department.trim() || department || null,
        major: manualCourse.major?.trim() || major || null,
        metadata: {},
      };
      const response = await api.post('/api/admin/courses', payload);
      setManualMessage({
        type: 'success',
        text: `Đã lưu môn ${response.data.code} - ${response.data.name}.`,
      });
      setManualCourse({ code: '', name: '', credits: '', department: '', major: '' });
      await fetchCourses();
    } catch (err) {
      console.error(err);
      const message = err.response?.data?.detail || err.message || 'Không thể thêm môn.';
      setManualMessage({ type: 'error', text: message });
    }
  };

  return (
    <div className="admin-page-container">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="admin-header"
      >
        <div className="admin-header-content">
          <h1>⚙️ Bảng điều khiển quản trị</h1>
          <p>Xin chào, {user?.username} (Admin)</p>
        </div>
        <div className="admin-header-actions">
          <motion.button
            onClick={() => navigate('/app')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="admin-btn admin-btn-primary"
          >
            ← Về trang xếp lịch
          </motion.button>
          <motion.button
            onClick={logout}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="admin-btn admin-btn-danger"
          >
            Đăng xuất
          </motion.button>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.6 }}
        className="admin-content"
      >
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="admin-section"
        >
          <h2>📤 1. Upload danh sách môn học</h2>
          <p>
            Chấp nhận định dạng: <strong>PDF, XLS, XLSX, CSV</strong>. Vui lòng đảm bảo file có cột <em>Mã môn</em>, <em>Tên môn</em>, <em>Tín chỉ</em>.
            {' '}Tải file CSV mẫu tại{' '}
            <a href="/samples/courses_sample.csv" style={{ color: '#667eea', fontWeight: '600' }} download>
              đây
            </a>.
          </p>
          
          <div className="admin-form-grid">
            <div className="admin-form-group">
              <label className="admin-form-label">Chuyên ngành (Tuỳ chọn)</label>
              <input
                type="text"
                value={major}
                onChange={(e) => setMajor(e.target.value)}
                placeholder="VD: KTPM"
                className="admin-form-input"
              />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-label">Học kỳ *</label>
              <input
                type="text"
                value={semester}
                onChange={(e) => setSemester(e.target.value)}
                className="admin-form-input"
              />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-label">Bộ môn / Khoa (Tuỳ chọn)</label>
              <input
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                placeholder="VD: CNTT"
                className="admin-form-input"
              />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-label">Tệp môn học *</label>
              <input
                type="file"
                accept=".csv,.xls,.xlsx,.pdf"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="admin-form-input"
              />
            </div>
          </div>

          <motion.button
            onClick={handleUpload}
            disabled={isUploading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="admin-submit-btn"
          >
            {isUploading ? 'Đang upload...' : 'Tải lên & ghi đè học kỳ'}
          </motion.button>

          {uploadInfo && (
            <div className="admin-upload-info">
              <p>✅ Đã import <strong>{uploadInfo.inserted}</strong> môn học cho học kỳ <strong>{uploadInfo.semester}</strong>.</p>
              {uploadInfo.sample?.length > 0 && (
                <div style={{ marginTop: '10px' }}>
                  <p style={{ marginBottom: '5px', color: '#047857', fontWeight: '600' }}>Một vài môn mẫu:</p>
                  <ul>
                    {uploadInfo.sample.map((course) => (
                      <li key={course.code}>{course.code} - {course.name} ({course.credits} tín chỉ)</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </motion.section>

        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="admin-section"
        >
          <h2>➕ 2. Thêm nhanh 1 môn học</h2>
          <p>Dùng khi cần bổ sung lẻ tẻ mà không cần upload lại toàn bộ file.</p>
          <div className="admin-form-grid-5">
            <div className="admin-form-group">
              <label className="admin-form-label">Mã môn *</label>
              <input
                type="text"
                value={manualCourse.code}
                onChange={(e) => setManualCourse({ ...manualCourse, code: e.target.value })}
                placeholder="VD: INT2201"
                className="admin-form-input"
              />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-label">Tên môn *</label>
              <input
                type="text"
                value={manualCourse.name}
                onChange={(e) => setManualCourse({ ...manualCourse, name: e.target.value })}
                placeholder="VD: Cấu trúc dữ liệu"
                className="admin-form-input"
              />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-label">Tín chỉ</label>
              <input
                type="number"
                min="0"
                value={manualCourse.credits}
                onChange={(e) => setManualCourse({ ...manualCourse, credits: e.target.value })}
                placeholder="VD: 3"
                className="admin-form-input"
              />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-label">Bộ môn (tuỳ chọn)</label>
              <input
                type="text"
                value={manualCourse.department}
                onChange={(e) => setManualCourse({ ...manualCourse, department: e.target.value })}
                placeholder="VD: Khoa CNTT"
                className="admin-form-input"
              />
            </div>
            <div className="admin-form-group">
              <label className="admin-form-label">Chuyên ngành (tuỳ chọn)</label>
              <input
                type="text"
                value={manualCourse.major}
                onChange={(e) => setManualCourse({ ...manualCourse, major: e.target.value })}
                placeholder="VD: Kỹ thuật phần mềm"
                className="admin-form-input"
              />
            </div>
          </div>
          <motion.button
            onClick={handleManualSubmit}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="admin-submit-btn admin-submit-btn-success"
          >
            Thêm / cập nhật môn
          </motion.button>
          {manualMessage && (
            <div className={`admin-message ${manualMessage.type === 'success' ? 'admin-message-success' : 'admin-message-error'}`}>
              {manualMessage.text}
            </div>
          )}
        </motion.section>

        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="admin-section"
        >
          <div className="admin-section-header">
            <div>
              <h2>📚 3. Môn học trong học kỳ {semester}</h2>
              <p>Danh sách này sẽ xuất hiện cho sinh viên khi chọn môn.</p>
            </div>
            <motion.button
              onClick={fetchCourses}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="admin-refresh-btn"
            >
              🔄 Làm mới
            </motion.button>
          </div>

          {error && <p style={{ color: '#ef4444', fontWeight: '600' }}>{error}</p>}
          {isLoadingCourses ? (
            <p style={{ color: '#64748b', textAlign: 'center', padding: '40px' }}>Đang tải danh sách môn học...</p>
          ) : (
            <div className="admin-table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Mã môn</th>
                    <th>Tên môn</th>
                    <th>Tín chỉ</th>
                    <th>Bộ môn</th>
                  </tr>
                </thead>
                <tbody>
                  {courses.length === 0 ? (
                    <tr>
                      <td colSpan="4" className="admin-table-empty">Chưa có môn học nào cho học kỳ này.</td>
                    </tr>
                  ) : (
                    courses.map((course) => (
                      <tr key={`${course.code}-${course.name}`}>
                        <td><strong>{course.code}</strong></td>
                        <td>{course.name}</td>
                        <td>{course.credits}</td>
                        <td>{course.department || '-'}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </motion.section>

        {/* Section 4: Quản lý Người dùng */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
          className="admin-section"
        >
          <div className="admin-section-header">
            <div>
              <h2>👥 4. Quản lý Người dùng</h2>
              <p>Xem danh sách tất cả người dùng đã đăng ký trong hệ thống.</p>
            </div>
            <motion.button
              onClick={fetchUsers}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="admin-refresh-btn"
            >
              🔄 Làm mới
            </motion.button>
          </div>

          {usersError && <p style={{ color: '#ef4444', fontWeight: '600' }}>{usersError}</p>}
          {isLoadingUsers ? (
            <p style={{ color: '#64748b', textAlign: 'center', padding: '40px' }}>Đang tải danh sách người dùng...</p>
          ) : (
            <div className="admin-table-container">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>STT</th>
                    <th>Họ và Tên</th>
                    <th>Tên đăng nhập</th>
                    <th>Email</th>
                    <th>Số điện thoại</th>
                    <th>Quyền</th>
                    <th>Ngày tạo</th>
                    <th>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {users.length === 0 ? (
                    <tr>
                      <td colSpan="8" className="admin-table-empty">Chưa có người dùng nào trong hệ thống.</td>
                    </tr>
                  ) : (
                    users.map((userItem, index) => {
                      const isCurrentUser = userItem.id === user?.id?.toString();
                      return (
                      <tr key={userItem.id}>
                        <td>{index + 1}</td>
                        <td>
                          <strong>{userItem.full_name || '-'}</strong>
                          {isCurrentUser && <span style={{ color: '#22d3ee', marginLeft: '8px' }}>(Bạn)</span>}
                        </td>
                        <td>
                          <strong>{userItem.username}</strong>
                        </td>
                        <td>{userItem.email || '-'}</td>
                        <td>{userItem.phone || '-'}</td>
                        <td>
                          <span className={`admin-badge ${userItem.is_admin ? 'admin-badge-admin' : 'admin-badge-user'}`}>
                            {userItem.is_admin ? '👑 Admin' : '👤 User'}
                          </span>
                        </td>
                        <td>
                          {userItem.created_at 
                            ? new Date(userItem.created_at).toLocaleDateString('vi-VN')
                            : '-'}
                        </td>
                        <td>
                          <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                            <motion.button
                              onClick={() => handleToggleAdmin(userItem.id, userItem.username, userItem.is_admin)}
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              className="admin-action-btn"
                              style={{
                                background: userItem.is_admin 
                                  ? 'linear-gradient(135deg, #f59e0b, #d97706)' 
                                  : 'linear-gradient(135deg, #10b981, #059669)',
                                color: '#fff',
                                padding: '6px 12px',
                                fontSize: '12px',
                                border: 'none',
                                borderRadius: '6px',
                                cursor: 'pointer'
                              }}
                              disabled={isCurrentUser}
                            >
                              {userItem.is_admin ? '🔓 Thu hồi Admin' : '🔐 Cấp Admin'}
                            </motion.button>
                            <motion.button
                              onClick={() => handleDeleteUser(userItem.id, userItem.username)}
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              className="admin-action-btn"
                              style={{
                                background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                                color: '#fff',
                                padding: '6px 12px',
                                fontSize: '12px',
                                border: 'none',
                                borderRadius: '6px',
                                cursor: 'pointer'
                              }}
                              disabled={isCurrentUser}
                            >
                              🗑️ Xóa
                            </motion.button>
                          </div>
                        </td>
                      </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
              {users.length > 0 && (
                <p style={{ marginTop: '15px', color: '#64748b', textAlign: 'center', fontSize: '14px' }}>
                  Tổng số người dùng: <strong>{users.length}</strong>
                </p>
              )}
            </div>
          )}
        </motion.section>
      </motion.div>
    </div>
  );
}

export default AdminPage;

