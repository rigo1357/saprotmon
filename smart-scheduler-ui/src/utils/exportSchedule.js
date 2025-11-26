// Utility functions để export schedule
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';

// Export to PDF
export const exportToPDF = (schedule, title = 'Thời khóa biểu') => {
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(18);
  doc.text(title, 14, 15);
  
  // Table data với đầy đủ thông tin
  const tableData = schedule.map(item => [
    item.subject || item.name || '',
    item.time || '',
    item.instructor || '-',
    item.sessions || '',
    item.start_date ? `${item.start_date} - ${item.end_date || ''}` : '-',
    item.priority ? `${item.priority}/10` : '-'
  ]);
  
  doc.autoTable({
    head: [['Môn học', 'Thời gian', 'Giảng viên', 'Số buổi', 'Thời gian học', 'Ưu tiên']],
    body: tableData,
    startY: 25,
    styles: { fontSize: 9 },
    headStyles: { fillColor: [76, 175, 80] },
    columnStyles: {
      0: { cellWidth: 40 },
      1: { cellWidth: 50 },
      2: { cellWidth: 35 },
      3: { cellWidth: 20 },
      4: { cellWidth: 40 },
      5: { cellWidth: 20 }
    }
  });
  
  doc.save(`${title.replace(/\s/g, '_')}.pdf`);
};

// Export to Excel
export const exportToExcel = (schedule, title = 'Thời khóa biểu') => {
  const worksheetData = [
    ['Môn học', 'Thời gian', 'Giảng viên', 'Số buổi', 'Thời gian bắt đầu', 'Thời gian kết thúc', 'Ngày bắt đầu', 'Ngày kết thúc', 'Ưu tiên']
  ];
  
  schedule.forEach(item => {
    worksheetData.push([
      item.subject || item.name || '',
      item.time || '',
      item.instructor || '-',
      item.sessions || '',
      item.start_time || '-',
      item.end_time || '-',
      item.start_date || '-',
      item.end_date || '-',
      item.priority ? `${item.priority}/10` : '-'
    ]);
  });
  
  const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
  
  // Set column widths
  worksheet['!cols'] = [
    { wch: 20 }, // Môn học
    { wch: 30 }, // Thời gian
    { wch: 20 }, // Giảng viên
    { wch: 10 }, // Số buổi
    { wch: 15 }, // Thời gian bắt đầu
    { wch: 15 }, // Thời gian kết thúc
    { wch: 15 }, // Ngày bắt đầu
    { wch: 15 }, // Ngày kết thúc
    { wch: 10 }  // Ưu tiên
  ];
  
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Thời khóa biểu');
  
  // XLSX files are binary format, UTF-8 is handled internally
  XLSX.writeFile(workbook, `${title.replace(/\s/g, '_')}.xlsx`);
};

