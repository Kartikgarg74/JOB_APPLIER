'use client';

import { Button } from '@tremor/react';
import type { JobApplication } from '@/app/dashboard/page';
import { Parser } from '@json2csv/plainjs';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

interface ExportDataButtonProps {
  data: JobApplication[];
}

export default function ExportDataButton({ data }: ExportDataButtonProps) {
  const exportToCSV = () => {
    try {
      const parser = new Parser();
      const csv = parser.parse(data);
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'job_applications.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (err) {
      console.error('Error exporting to CSV:', err);
      alert('Failed to export to CSV. Check console for details.');
    }
  };

  const exportToPDF = () => {
    try {
      const doc = new jsPDF();
      const tableColumn = ["ID", "Job Title", "Company", "Status", "Match Score", "ATS Score", "Last Updated"];
      const tableRows: any[] = [];

      data.forEach(app => {
        const applicationData = [
          app.id,
          app.job_title,
          app.company,
          app.application_status,
          `${app.job_match_score.toFixed(1)}%`,
          `${app.ats_score.toFixed(1)}%`,
          new Date(app.last_updated).toLocaleDateString(),
        ];
        tableRows.push(applicationData);
      });

      (doc as any).autoTable({
        head: [tableColumn],
        body: tableRows,
        startY: 20,
        headStyles: { fillColor: [100, 100, 100] },
        footStyles: { fillColor: [100, 100, 100] },
        bodyStyles: { fillColor: [240, 240, 240] },
        alternateRowStyles: { fillColor: [250, 250, 250] },
      });

      doc.save('job_applications.pdf');

    } catch (err) {
      console.error('Error exporting to PDF:', err);
      alert('Failed to export to PDF. Check console for details.');
    }
  };

  return (
    <div className="flex space-x-4">
      <Button onClick={exportToCSV} variant="secondary">Export to CSV</Button>
      <Button onClick={exportToPDF} variant="secondary">Export to PDF</Button>
    </div>
  );
}