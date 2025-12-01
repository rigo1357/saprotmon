// src/pages/SchedulerPage.js
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { exportToPDF, exportToExcel } from '../utils/exportSchedule';
import './SchedulerPage.css';

const defaultStudyInfo = {
  semester: '',
  major: '',
  maxCredits: '',
  minCredits: '',
};

const defaultFreeTime = {
  T2: { morning: false, afternoon: false, evening: false },
  T3: { morning: false, afternoon: false, evening: false },
  T4: { morning: false, afternoon: false, evening: false },
  T5: { morning: false, afternoon: false, evening: false },
  T6: { morning: false, afternoon: false, evening: false },
  T7: { morning: false, afternoon: false, evening: false },
  CN: { morning: false, afternoon: false, evening: false },
};

const dayTitle = {
  T2: 'Thứ 2', T3: 'Thứ 3', T4: 'Thứ 4',
  T5: 'Thứ 5', T6: 'Thứ 6', T7: 'Thứ 7', CN: 'Chủ nhật',
};

function ChatbotPage() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      content: 'Xin chào! Tôi là trợ lý Smart Scheduler. Tôi có thể giúp bạn về việc xếp lịch học, tư vấn môn học, và giải đáp các thắc mắc. Hãy hỏi tôi bất kỳ điều gì! 😊'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load lịch sử chat khi component mount
  useEffect(() => {
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const response = await api.get('/api/chat/history', { params: { limit: 20 } });
      setChatHistory(response.data || []);
    } catch (error) {
      console.error('Lỗi tải lịch sử chat:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    try {
      const response = await api.get('/api/chat/search', { params: { q: searchQuery, limit: 10 } });
      setSearchResults(response.data.sessions || []);
    } catch (error) {
      console.error('Lỗi tìm kiếm:', error);
    }
  };

  const loadSession = async (sessionIdToLoad) => {
    try {
      const response = await api.get('/api/chat/history', { params: { session_id: sessionIdToLoad } });
      if (response.data && response.data.length > 0) {
        const session = response.data[0];
        setMessages(session.messages || []);
        setSessionId(sessionIdToLoad);
        setShowHistory(false);
      }
    } catch (error) {
      console.error('Lỗi tải phiên chat:', error);
    }
  };

  const deleteSession = async (sessionIdToDelete) => {
    try {
      await api.delete(`/api/chat/history/${sessionIdToDelete}`);
      loadChatHistory();
      if (sessionId === sessionIdToDelete) {
        setMessages([{
          role: 'bot',
          content: 'Xin chào! Tôi là trợ lý Smart Scheduler. Tôi có thể giúp bạn về việc xếp lịch học, tư vấn môn học, và giải đáp các thắc mắc. Hãy hỏi tôi bất kỳ điều gì! 😊'
        }]);
        setSessionId(null);
      }
    } catch (error) {
      console.error('Lỗi xóa phiên chat:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    setIsLoading(true);
    const userMessage = input.trim();
    const newMessages = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    setInput('');

    try {
      const response = await api.post('/api/chat', {
        message: userMessage,
        session_id: sessionId
      });

      // Backend luôn trả về 200 với reply (kể cả khi có lỗi, reply sẽ chứa message lỗi)
      const botReply = response.data.reply || 'Xin lỗi, không nhận được phản hồi từ chatbot.';
      setMessages([...newMessages, { role: 'bot', content: botReply }]);

      if (response.data.session_id) {
        setSessionId(response.data.session_id);
      }

      // Reload lịch sử sau khi gửi tin nhắn
      loadChatHistory();
    } catch (error) {
      console.error('Lỗi chatbot:', error);

      // Xử lý các loại lỗi khác nhau
      let errorMessage = 'Có lỗi xảy ra khi kết nối với chatbot';

      if (error.response) {
        // Server trả về lỗi (4xx, 5xx)
        errorMessage = error.response.data?.detail || error.response.data?.reply || errorMessage;
      } else if (error.request) {
        // Request được gửi nhưng không nhận được response
        errorMessage = 'Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.';
      } else {
        // Lỗi khi setup request
        errorMessage = error.message || errorMessage;
      }

      setMessages([...newMessages, { role: 'bot', content: 'Xin lỗi, tôi đang gặp sự cố: ' + errorMessage }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([
      {
        role: 'bot',
        content: 'Xin chào! Tôi là trợ lý Smart Scheduler. Tôi có thể giúp bạn về việc xếp lịch học, tư vấn môn học, và giải đáp các thắc mắc. Hãy hỏi tôi bất kỳ điều gì! 😊'
      }
    ]);
    setSessionId(null);
  };

  return (
    <div className="chatbot-page-container" style={{ display: 'flex', gap: '20px' }}>
      {/* Sidebar lịch sử chat */}
      <div className={`chatbot-sidebar ${showHistory ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h3 style={{ margin: 0, color: '#22d3ee' }}>Lịch sử chat</h3>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="sidebar-toggle"
            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '20px' }}
          >
            {showHistory ? '✕' : '☰'}
          </button>
        </div>

        {showHistory && (
          <>
            <div className="sidebar-search">
              <input
                type="text"
                placeholder="Tìm kiếm..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="chatbot-input"
                style={{ marginBottom: '10px' }}
              />
              <button onClick={handleSearch} className="btn-rounded btn-cyan" style={{ width: '100%' }}>
                Tìm kiếm
              </button>
            </div>

            <div className="sidebar-content">
              {(searchQuery ? searchResults : chatHistory).map((session) => (
                <div key={session.session_id} className="history-item">
                  <div
                    className="history-item-content"
                    onClick={() => loadSession(session.session_id)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div style={{ fontWeight: 'bold', color: '#e2e8f0', marginBottom: '4px' }}>
                      {session.messages[0]?.content?.substring(0, 50) || 'Cuộc trò chuyện mới'}...
                    </div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                      {new Date(session.created_at).toLocaleString('vi-VN')}
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(session.session_id);
                    }}
                    className="delete-btn"
                    style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer' }}
                  >
                    🗑️
                  </button>
                </div>
              ))}
              {chatHistory.length === 0 && !searchQuery && (
                <p style={{ color: '#94a3b8', textAlign: 'center', padding: '20px' }}>
                  Chưa có lịch sử chat
                </p>
              )}
            </div>
          </>
        )}
      </div>

      {/* Main chat area */}
      <div className="chatbot-main-card" style={{ flex: 1 }}>
        <div className="chatbot-header">
          <div>
            <h2 style={{ margin: 0, color: '#22d3ee' }}>🤖 Trợ lý Smart Scheduler</h2>
            <p style={{ margin: '5px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
              Hỏi tôi về xếp lịch học, môn học, hoặc bất kỳ thắc mắc nào!
            </p>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button onClick={() => setShowHistory(!showHistory)} className="btn-rounded btn-cyan" style={{ fontSize: '14px', padding: '8px 16px' }}>
              {showHistory ? 'Ẩn' : 'Hiện'} lịch sử
            </button>
            <button onClick={handleClear} className="btn-rounded btn-cyan" style={{ fontSize: '14px', padding: '8px 16px' }}>
              Cuộc trò chuyện mới
            </button>
          </div>
        </div>

        <div className="chatbot-messages">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`chatbot-message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`}
            >
              <div className="message-avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">{msg.content}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="chatbot-message bot-message">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="message-text">
                  <span className="typing-indicator">Đang suy nghĩ</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chatbot-input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="Nhập câu hỏi của bạn..."
            className="chatbot-input"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="chatbot-send-btn"
          >
            {isLoading ? '⏳' : '➤'}
          </button>
        </div>
      </div>
    </div>
  );
}

function SectionDivider({ title }) {
  return (
    <div className="section-divider" style={{ margin: '40px 0 24px', position: 'relative' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{
          height: '3px',
          flex: 1,
          background: 'linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.3), transparent)',
          borderRadius: '2px'
        }}></div>
        <h3 style={{
          fontSize: '1.5rem',
          fontWeight: 700,
          margin: 0,
          color: '#0c4a6e',
          letterSpacing: '-0.02em',
          whiteSpace: 'nowrap'
        }}>{title}</h3>
        <div style={{
          height: '3px',
          flex: 1,
          background: 'linear-gradient(90deg, transparent, rgba(14, 165, 233, 0.3), transparent)',
          borderRadius: '2px'
        }}></div>
      </div>
    </div>
  );
}

function ConstraintToggle({ label, checked, onChange }) {
  return (
    <label className="constraint-toggle">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span>{label}</span>
    </label>
  );
}

function SchedulerForm({ onGenerate }) {
  const [studyInfo, setStudyInfo] = useState(defaultStudyInfo);
  const [freeTime, setFreeTime] = useState(defaultFreeTime);
  const [constraints, setConstraints] = useState({
    avoidConsecutive: true, balanceDays: true, preferMorning: false, allowSaturday: false,
  });
  const [selectedTab, setSelectedTab] = useState('current');
  const [selectedSubjects, setSelectedSubjects] = useState([]);
  const [availableSubjects, setAvailableSubjects] = useState([]);
  const [isLoadingCourses, setIsLoadingCourses] = useState(false);
  const [coursesError, setCoursesError] = useState(null);
  const [searchText, setSearchText] = useState('');

  const [availableSemesters, setAvailableSemesters] = useState([]);
  const [availableMajors, setAvailableMajors] = useState([]);
  const [isLoadingMetadata, setIsLoadingMetadata] = useState(true);
  const [metadataError, setMetadataError] = useState(null);

  useEffect(() => {
    const fetchMetadata = async () => {
      setIsLoadingMetadata(true);
      setMetadataError(null);
      try {
        console.log('Đang tải metadata từ API...');
        const [semRes, majRes] = await Promise.all([
          api.get('/api/metadata/semesters'),
          api.get('/api/metadata/majors')
        ]);

        const semesters = semRes.data?.semesters || [];
        const majors = majRes.data?.majors || [];

        console.log('Đã tải metadata:', { semesters, majors });

        setAvailableSemesters(semesters);
        setAvailableMajors(majors);

        if (semesters.length === 0) {
          console.warn('⚠️ Không có dữ liệu học kỳ trong database. Hãy chạy script add_sample_courses.py để thêm dữ liệu mẫu.');
        }
        if (majors.length === 0) {
          console.warn('⚠️ Không có dữ liệu chuyên ngành trong database.');
        }
      } catch (err) {
        console.error('❌ Lỗi tải metadata:', err);
        setMetadataError(err.response?.data?.detail || err.message || 'Không thể tải dữ liệu từ server');
      } finally {
        setIsLoadingMetadata(false);
      }
    };
    fetchMetadata();
  }, []);

  useEffect(() => {
    let isMounted = true;
    const loadCourses = async () => {
      // Chỉ load khi có học kỳ
      if (!studyInfo.semester) {
        setAvailableSubjects([]);
        return;
      }

      setIsLoadingCourses(true);
      try {
        const params = { semester: studyInfo.semester };
        // Thêm filter theo chuyên ngành nếu có
        if (studyInfo.major && studyInfo.major.trim()) {
          params.major = studyInfo.major.trim();
        }

        const response = await api.get('/api/courses', { params });
        if (!isMounted) return;
        setAvailableSubjects(response.data?.items || []);
        setCoursesError(null);
      } catch (error) {
        console.error('Lỗi tải môn học:', error);
        if (isMounted) setCoursesError('Không thể tải danh sách môn học.');
      } finally {
        if (isMounted) setIsLoadingCourses(false);
      }
    };
    loadCourses();
    return () => { isMounted = false; };
  }, [studyInfo.semester, studyInfo.major]);

  const handleStudyFieldChange = (field, value) => setStudyInfo(prev => ({ ...prev, [field]: value }));

  const handleMaxCreditsChange = (value) => {
    if (value === '') {
      setStudyInfo(prev => ({ ...prev, maxCredits: '', minCredits: '' }));
      return;
    }
    const numeric = parseInt(value, 10);
    if (Number.isNaN(numeric) || numeric < 0) return;
    setStudyInfo(prev => ({ ...prev, maxCredits: numeric, minCredits: Math.floor((numeric * 2) / 3) }));
  };

  const calculatePriority = (subject, index) => {
    const base = Math.max(1, 10 - index);
    return Math.min(10, base + (subject.is_retake ? 2 : 0));
  };

  const moveSubject = (index, direction) => {
    setSelectedSubjects(prev => {
      const newList = [...prev];
      const targetIndex = index + direction;
      if (targetIndex < 0 || targetIndex >= newList.length) return prev;
      const [removed] = newList.splice(index, 1);
      newList.splice(targetIndex, 0, removed);
      return newList;
    });
  };

  const handleFreeTimeChange = (day, period) => {
    setFreeTime(prev => ({ ...prev, [day]: { ...prev[day], [period]: !prev[day][period] } }));
  };

  const buildSubjectPayload = (course, sessionData = null) => {
    // Nếu có sessionData (từ API), dùng dữ liệu từ đó
    if (sessionData) {
      return {
        code: sessionData.code,
        displayName: sessionData.name,
        name: `${sessionData.code} - ${sessionData.name}`,
        credits: sessionData.credits || 3,
        instructor: sessionData.department || '',
        start_time: sessionData.start_time || '07:00',
        end_time: sessionData.end_time || '11:30',
        start_date: sessionData.start_date || new Date().toISOString().split('T')[0],
        end_date: sessionData.end_date || new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        day: sessionData.day || course?.metadata?.day || null,
        subject_type: 'Lý thuyết',
      };
    }

    // Fallback: tạo từ course thông thường
    const today = new Date();
    const endDate = new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000);
    return {
      code: course.code,
      displayName: course.name,
      name: `${course.code} - ${course.name}`,
      credits: course.credits || 3,
      instructor: course.department || '',
      start_time: '07:00',
      end_time: '11:30',
      start_date: today.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
      day: course.metadata?.day || null,
      subject_type: 'Lý thuyết',
    };
  };

  const handleSubjectToggle = async (course) => {
    // Lấy original_code (nếu là session có -G thì lấy phần trước -G)
    const originalCode = course.metadata?.original_code ||
      (course.code.includes('-G') ? course.code.split('-G')[0] : course.code);

    // Kiểm tra xem đã có môn học này chưa (so sánh theo original_code hoặc code trực tiếp)
    const existing = selectedSubjects.find(item => {
      const itemOriginalCode = item.code.includes('-G') ? item.code.split('-G')[0] : item.code;
      // So sánh cả originalCode và code trực tiếp để đảm bảo tìm được
      return itemOriginalCode === originalCode || item.code === course.code || item.code === originalCode;
    });

    if (existing) {
      // Xóa môn học này (so sánh theo originalCode hoặc code trực tiếp)
      setSelectedSubjects(prev => prev.filter(item => {
        const itemOriginalCode = item.code.includes('-G') ? item.code.split('-G')[0] : item.code;
        // Giữ lại những môn không khớp với originalCode hoặc course.code
        return itemOriginalCode !== originalCode && item.code !== course.code && item.code !== originalCode;
      }));
      return;
    }

    // Lấy chỉ session đầu tiên từ API
    try {
      const response = await api.get(`/api/courses/${originalCode}/sessions`, {
        params: { semester: studyInfo.semester }
      });

      const sessions = response.data?.sessions || [];
      const isRetake = selectedTab === 'retake';

      if (sessions.length > 0) {
        // Chỉ lấy session đầu tiên
        const firstSession = sessions[0];
        setSelectedSubjects(prev => [...prev, {
          ...buildSubjectPayload(course, firstSession),
          is_retake: isRetake,
        }]);
      } else {
        // Nếu không có sessions, thêm môn học thông thường
        setSelectedSubjects(prev => [...prev, {
          ...buildSubjectPayload(course),
          is_retake: isRetake
        }]);
      }
    } catch (error) {
      console.error('Lỗi lấy sessions:', error);
      // Fallback: chỉ thêm môn học hiện tại
      const isRetake = selectedTab === 'retake';
      setSelectedSubjects(prev => [...prev, {
        ...buildSubjectPayload(course),
        is_retake: isRetake
      }]);
    }
  };

  // Tạo danh sách các originalCode đã được chọn để kiểm tra
  const selectedOriginalCodes = selectedSubjects.map(s => {
    const code = s.code.includes('-G') ? s.code.split('-G')[0] : s.code;
    return code;
  });

  const filteredSubjects = availableSubjects.filter(c => {
    if (!searchText) return true;
    return `${c.code} ${c.name}`.toLowerCase().includes(searchText.toLowerCase());
  });

  const handleGenerate = () => {
    if (selectedSubjects.length === 0) {
      alert('Vui lòng chọn ít nhất một môn học!');
      return;
    }
    const availableSlots = [];
    const slotMap = { morning: 'Sáng', afternoon: 'Chiều', evening: 'Tối' };
    Object.keys(freeTime).forEach(day => {
      Object.entries(slotMap).forEach(([key, label]) => {
        if (freeTime[day]?.[key]) availableSlots.push(`${day}_${label}`);
      });
    });

    const subjectsWithPriority = selectedSubjects.map((subject, index) => ({
      ...subject, priority: calculatePriority(subject, index),
    }));

    onGenerate({
      studyInfo, subjects: subjectsWithPriority, availableSlots,
      constraints: {}, additionalConstraints: constraints,
    });
  };

  return (
    <div className="scheduler-main-card">
      <h2 style={{ marginTop: 0, marginBottom: '32px' }}>Thông tin học tập</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(250px,1fr))', gap: '24px', marginBottom: '16px' }}>
        <div className="form-field-wrapper">
          <label>Học kỳ *</label>
          {isLoadingMetadata ? (
            <div className="form-input" style={{ color: '#94a3b8', fontStyle: 'italic', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="loading-spinner" style={{ width: '16px', height: '16px', border: '2px solid rgba(148, 163, 184, 0.3)', borderTopColor: '#22d3ee', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }}></span>
              Đang tải...
            </div>
          ) : metadataError ? (
            <div className="form-input" style={{ color: '#f87171', borderColor: '#f87171', background: 'rgba(248, 113, 113, 0.1)' }}>
              ⚠️ Lỗi: {metadataError}
            </div>
          ) : (
            <select
              className="form-input"
              value={studyInfo.semester}
              onChange={(e) => handleStudyFieldChange('semester', e.target.value)}
              required
            >
              <option value="">-- Chọn học kỳ --</option>
              {availableSemesters.length === 0 ? (
                <option value="" disabled>Không có dữ liệu</option>
              ) : (
                availableSemesters.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))
              )}
            </select>
          )}
          {availableSemesters.length === 0 && !isLoadingMetadata && !metadataError && (
            <div style={{ fontSize: '12px', color: '#fbbf24', marginTop: '8px', padding: '8px 12px', background: 'rgba(251, 191, 36, 0.1)', borderRadius: '8px', border: '1px solid rgba(251, 191, 36, 0.2)' }}>
              ⚠️ Chưa có dữ liệu. Vui lòng upload môn học hoặc chạy script add_sample_courses.py
            </div>
          )}
        </div>
        <div className="form-field-wrapper">
          <label>Chuyên ngành (tuỳ chọn)</label>
          {isLoadingMetadata ? (
            <div className="form-input" style={{ color: '#94a3b8', fontStyle: 'italic' }}>
              Đang tải...
            </div>
          ) : metadataError ? (
            <div className="form-input" style={{ color: '#f87171', borderColor: '#f87171' }}>
              Lỗi: {metadataError}
            </div>
          ) : (
            <select
              className="form-input"
              value={studyInfo.major}
              onChange={(e) => handleStudyFieldChange('major', e.target.value)}
            >
              <option value="">-- Chọn chuyên ngành --</option>
              {availableMajors.length === 0 ? (
                <option value="" disabled>Không có dữ liệu</option>
              ) : (
                availableMajors.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))
              )}
            </select>
          )}
          {availableMajors.length === 0 && !isLoadingMetadata && !metadataError && (
            <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '8px', padding: '8px 12px', background: 'rgba(148, 163, 184, 0.1)', borderRadius: '8px', border: '1px solid rgba(148, 163, 184, 0.15)' }}>
              Chưa có dữ liệu chuyên ngành
            </div>
          )}
        </div>
        <div className="form-field-wrapper">
          <label>Tín chỉ tối đa *</label>
          <input
            type="number" min="0" className="form-input" placeholder="18"
            value={studyInfo.maxCredits} onChange={(e) => handleMaxCreditsChange(e.target.value)}
          />
        </div>
        <div className="form-field-wrapper">
          <label>Tín chỉ tối thiểu</label>
          <input
            type="number" className="form-input input-readonly" readOnly placeholder="Tự động tính"
            value={studyInfo.minCredits}
          />
        </div>
      </div >

      <SectionDivider title="Thời gian rảnh" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))', gap: '16px' }}>
        {Object.keys(freeTime).map((day) => (
          <div key={day} className="time-card">
            <h4>{dayTitle[day]}</h4>
            <label className="checkbox-label">
              <input type="checkbox" checked={freeTime[day].morning} onChange={() => handleFreeTimeChange(day, 'morning')} />
              <span>Sáng (7:30 - 11:15)</span>
            </label>
            <label className="checkbox-label">
              <input type="checkbox" checked={freeTime[day].afternoon} onChange={() => handleFreeTimeChange(day, 'afternoon')} />
              <span>Chiều (12:30 - 16:15)</span>
            </label>
            <label className="checkbox-label">
              <input type="checkbox" checked={freeTime[day].evening} onChange={() => handleFreeTimeChange(day, 'evening')} />
              <span>Tối (17:30 - 21:15)</span>
            </label>
          </div>
        ))}
      </div>

      <SectionDivider title="Chọn môn học" />
      <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
        <button onClick={() => setSelectedTab('current')} className={`tab-button ${selectedTab === 'current' ? 'active' : 'inactive'}`}>
          Môn học hiện tại
        </button>
        <button onClick={() => setSelectedTab('retake')} className={`tab-button ${selectedTab === 'retake' ? 'active' : 'inactive'}`}>
          Môn học Lại
        </button>
      </div>

      <div style={{ marginBottom: '10px' }}>
        <input
          type="text" value={searchText} onChange={(e) => setSearchText(e.target.value)}
          placeholder="Tìm kiếm mã hoặc tên môn..."
          className="form-input" style={{ borderRadius: '999px' }}
        />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '25px' }}>
        <div className="subject-list-container">
          {isLoadingCourses ? <p>Đang tải danh sách môn học...</p> :
            coursesError ? <p style={{ color: '#f87171' }}>{coursesError}</p> :
              filteredSubjects.length === 0 ? <p style={{ color: '#94a3b8' }}>Không tìm thấy môn học.</p> :
                filteredSubjects.map((course) => {
                  // Kiểm tra xem môn này đã được chọn chưa (so sánh theo originalCode)
                  const courseOriginalCode = course.metadata?.original_code ||
                    (course.code.includes('-G') ? course.code.split('-G')[0] : course.code);
                  const selected = selectedOriginalCodes.includes(courseOriginalCode) ||
                    selectedSubjects.some(s => s.code === course.code);
                  return (
                    <label key={course.code} className={`subject-item-modern ${selected ? 'selected' : 'default'}`}>
                      <div className="subject-info">
                        <div className="subject-code-badge">{course.code}</div>
                        <div className="subject-details">
                          <strong className="subject-name">{course.name}</strong>
                          <div className="subject-meta">
                            <span className="credit-badge">📚 {course.credits || 0} TC</span>
                            {course.department && <span className="dept-badge">🏛️ {course.department}</span>}
                          </div>
                        </div>
                      </div>
                      {selectedTab === 'current' ? (
                        <input type="checkbox" checked={selected} onChange={() => handleSubjectToggle(course)} className="custom-checkbox" />
                      ) : <span className="viewing-badge">👁️ Đang xem</span>}
                    </label>
                  );
                })}
        </div>
        <div style={{ border: '2px solid #e2e8f0', borderRadius: '16px', padding: '20px', backgroundColor: '#ffffff', boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)' }}>
          <h4 style={{ marginTop: 0, color: '#0c4a6e', fontSize: '1.1rem', fontWeight: 700 }}>Môn đã chọn ({selectedSubjects.length})</h4>
          {(() => {
            const totalCredits = selectedSubjects.reduce((sum, s) => sum + (s.credits || 0), 0);
            const minCredits = studyInfo.minCredits || 0;
            const maxCredits = studyInfo.maxCredits || 0;
            const percentage = minCredits > 0 ? Math.min((totalCredits / minCredits) * 100, 100) : 0;
            const isLow = totalCredits < minCredits;
            const isHigh = maxCredits > 0 && totalCredits > maxCredits;

            return (
              <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: isLow ? '#fef2f2' : isHigh ? '#fefce8' : '#f0f9ff', borderRadius: '8px', border: `1px solid ${isLow ? '#fecaca' : isHigh ? '#fef08a' : '#bae6fd'}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '14px', fontWeight: 600, color: isLow ? '#991b1b' : isHigh ? '#854d0e' : '#075985' }}>
                    Tổng tín chỉ: {totalCredits} TC
                  </span>
                  {minCredits > 0 && (
                    <span style={{ fontSize: '12px', color: '#64748b' }}>
                      Tối thiểu: {minCredits} TC {maxCredits > 0 && `• Tối đa: ${maxCredits} TC`}
                    </span>
                  )}
                </div>
                {minCredits > 0 && (
                  <div style={{ width: '100%', height: '8px', backgroundColor: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{
                      width: `${percentage}%`,
                      height: '100%',
                      backgroundColor: isLow ? '#f87171' : isHigh ? '#fbbf24' : '#22d3ee',
                      transition: 'width 0.3s ease, background-color 0.3s ease'
                    }} />
                  </div>
                )}
                {isLow && minCredits > 0 && (
                  <div style={{ marginTop: '8px', fontSize: '12px', color: '#dc2626', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    ⚠️ Chưa đủ tín chỉ tối thiểu (thiếu {minCredits - totalCredits} TC)
                  </div>
                )}
                {isHigh && (
                  <div style={{ marginTop: '8px', fontSize: '12px', color: '#ca8a04', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    ⚠️ Vượt quá tín chỉ tối đa ({totalCredits - maxCredits} TC)
                  </div>
                )}
              </div>
            );
          })()}
          {selectedSubjects.length === 0 ? <p style={{ color: '#64748b', marginTop: '16px' }}>Chưa chọn môn nào.</p> :
            selectedSubjects.map((subject, index) => (
              <div key={subject.code} style={{ padding: '12px 0', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <strong style={{ color: '#1e293b' }}>{subject.name}</strong>
                  <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
                    {subject.credits} TC • Ưu tiên {calculatePriority(subject, index)}/10
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <button onClick={() => moveSubject(index, -1)} disabled={index === 0} className="priority-btn up">↑</button>
                  <button onClick={() => moveSubject(index, 1)} disabled={index === selectedSubjects.length - 1} className="priority-btn down">↓</button>
                </div>
              </div>
            ))}
        </div>
      </div>

      <SectionDivider title="Ràng buộc bổ sung" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))', gap: '15px' }}>
        <ConstraintToggle label="Tránh xếp các môn học liên tiếp" checked={constraints.avoidConsecutive} onChange={(c) => setConstraints({ ...constraints, avoidConsecutive: c })} />
        <ConstraintToggle label="Cân bằng số môn học giữa các ngày" checked={constraints.balanceDays} onChange={(c) => setConstraints({ ...constraints, balanceDays: c })} />
        <ConstraintToggle label="Ưu tiên học buổi sáng" checked={constraints.preferMorning} onChange={(c) => setConstraints({ ...constraints, preferMorning: c })} />
        <ConstraintToggle label="Cho phép học thứ 7" checked={constraints.allowSaturday} onChange={(c) => setConstraints({ ...constraints, allowSaturday: c })} />
      </div>

      <div style={{ marginTop: '25px', textAlign: 'center' }}>
        <button
          onClick={handleGenerate} disabled={selectedSubjects.length === 0}
          className={`btn-rounded ${selectedSubjects.length === 0 ? 'btn-disabled' : 'btn-primary-gradient'}`}
        >
          Tạo thời khóa biểu
        </button>
      </div>
    </div >
  );
}

function ScheduleTable({ schedule }) {
  if (!schedule || !schedule.schedule) return null;
  const days = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'];
  const sessions = ['Sáng', 'Chiều', 'Tối'];
  const sessionTimes = {
    Sáng: ['07:30', '08:15', '09:00', '09:45', '10:30', '11:15'],
    Chiều: ['12:30', '13:15', '14:00', '14:45', '15:30', '16:15'],
    Tối: ['17:30', '18:15', '19:00', '19:45', '20:30', '21:15'],
  };

  const scheduleMap = {};
  schedule.schedule.forEach((item) => {
    if (!scheduleMap[item.time]) scheduleMap[item.time] = [];
    scheduleMap[item.time].push(item);
  });

  return (
    <div style={{ marginTop: '20px', overflowX: 'auto' }}>
      <table className="schedule-table">
        <thead>
          <tr>
            <th className="schedule-th">Buổi</th>
            {days.map(day => <th key={day} className="schedule-th">{dayTitle[day]}</th>)}
            <th className="schedule-th">Khung giờ (45' / tiết)</th>
          </tr>
        </thead>
        <tbody>
          {sessions.map(session => (
            <tr key={session}>
              <td className="session-label">{session}</td>
              {days.map(day => {
                const key = `${day}_${session}`;
                const items = scheduleMap[key] || [];
                return (
                  <td key={key} className="schedule-td">
                    {items.length === 0 ? <span style={{ color: '#475569', fontStyle: 'italic' }}>Trống</span> :
                      items.map((item, idx) => (
                        <div key={idx} style={{ backgroundColor: item.is_retake ? 'rgba(251,113,133,0.2)' : 'rgba(59,130,246,0.2)', borderLeft: `4px solid ${item.is_retake ? '#fb7185' : '#38bdf8'}`, borderRadius: '10px', padding: '8px', marginBottom: '8px' }}>
                          <strong>{item.subject}</strong>
                          <div style={{ fontSize: '12px', color: '#94a3b8' }}>GV: {item.instructor || 'Chưa cập nhật'}</div>
                          <div style={{ fontSize: '12px', color: '#94a3b8' }}>{item.start_time} - {item.end_time}</div>
                          {item.is_retake && <div style={{ fontSize: '11px', color: '#fda4af' }}>Môn học lại</div>}
                        </div>
                      ))}
                  </td>
                );
              })}
              <td style={{ padding: '12px', border: '1px solid rgba(148,163,184,0.15)', color: '#a5b4fc' }}>{sessionTimes[session].join(' → ')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Scheduler() {
  const [schedule, setSchedule] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [conflicts, setConflicts] = useState([]);
  const [generationContext, setGenerationContext] = useState(null);

  const handleGenerate = async (formData) => {
    setIsLoading(true);
    setGenerationContext({
      studyInfo: formData.studyInfo,
      subjects: formData.subjects
    });

    try {
      const payloadSubjects = formData.subjects.map((subject) => ({
        ...subject, is_retake: subject.is_retake || false,
      }));
      const response = await api.post('/api/schedule', {
        subjects: payloadSubjects,
        available_time_slots: formData.availableSlots,
        constraints: formData.constraints,
        additionalConstraints: formData.additionalConstraints,
      });
      setSchedule(response.data);
      setConflicts(response.data.removed_conflicts || []);
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Có lỗi xảy ra';
      alert('Lỗi: ' + errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <SchedulerForm onGenerate={handleGenerate} />
      {isLoading && <div style={{ textAlign: 'center', padding: '20px', color: '#22d3ee' }}><h3>Đang chạy giải thuật di truyền...</h3></div>}
      {conflicts.length > 0 && (
        <div style={{ marginTop: '20px', padding: '15px', borderRadius: '12px', backgroundColor: '#2f1f2f', border: '1px solid rgba(248,113,113,0.4)', color: '#fecaca' }}>
          <strong>Các môn đã bị loại bỏ do trùng thời gian:</strong>
          <ul style={{ marginTop: '8px', paddingLeft: '18px' }}>
            {conflicts.map((item, idx) => <li key={idx}>{item.subject} ({item.reason})</li>)}
          </ul>
        </div>
      )}
      {schedule && !isLoading && (
        <div className="schedule-result-container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0 }}>Thời khóa biểu đề xuất (Cost: {schedule.cost})</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button onClick={() => exportToPDF(schedule.schedule, 'Thoi_khoa_bieu')} className="btn-rounded btn-cyan">📄 PDF</button>
              <button onClick={() => exportToExcel(schedule.schedule, 'Thoi_khoa_bieu')} className="btn-rounded btn-cyan">📊 Excel</button>
            </div>
          </div>

          {/* Cảnh báo tín chỉ tối thiểu */}
          {(() => {
            if (!generationContext) return null;
            const { studyInfo, subjects } = generationContext;
            const scheduledSubjects = subjects.filter(s => !conflicts.some(c => c.subject === s.name));
            const totalCredits = scheduledSubjects.reduce((sum, s) => sum + (s.credits || 0), 0);
            const minCredits = studyInfo.minCredits || 0;

            if (minCredits > 0 && totalCredits < minCredits) {
              return (
                <div style={{
                  marginTop: '16px',
                  padding: '12px 16px',
                  backgroundColor: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: '8px',
                  color: '#b91c1c',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span style={{ fontSize: '20px' }}>⚠️</span>
                  <div>
                    <strong>Cảnh báo: Không đủ tín chỉ tối thiểu!</strong>
                    <div style={{ fontSize: '14px', marginTop: '2px' }}>
                      Thời khóa biểu này chỉ có <strong>{totalCredits}</strong> tín chỉ (Yêu cầu tối thiểu: <strong>{minCredits}</strong> tín chỉ).
                    </div>
                  </div>
                </div>
              );
            }
            return null;
          })()}

          <ScheduleTable schedule={schedule} />
        </div>
      )}
    </>
  );
}

function SchedulerPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('scheduler');

  return (
    <div className="scheduler-page-container">
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="scheduler-header"
      >
        <div>
          <h1 className="header-title">🎓 Smart Scheduler</h1>
          <p className="header-subtitle">Xin chào, {user?.username || 'Bạn'} 👋</p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {user?.is_admin && (
            <motion.button
              onClick={() => navigate('/admin')}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-rounded btn-pink"
            >
              ⚙️ Quản trị môn học
            </motion.button>
          )}
          <motion.button
            onClick={logout}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-rounded btn-cyan"
          >
            Đăng xuất
          </motion.button>
        </div>
      </motion.header>

      <div className="page-tabs">
        <button
          onClick={() => setActiveTab('scheduler')}
          className={`page-tab ${activeTab === 'scheduler' ? 'active' : ''}`}
        >
          📅 Xếp lịch học
        </button>
        <button
          onClick={() => setActiveTab('chatbot')}
          className={`page-tab ${activeTab === 'chatbot' ? 'active' : ''}`}
        >
          💬 Trợ lý AI
        </button>
      </div>

      {activeTab === 'scheduler' ? <Scheduler /> : <ChatbotPage />}
    </div>
  );
}

export default SchedulerPage;