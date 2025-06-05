from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import sqlite3
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtCore import QDate

class TeknikServisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teknik Servis Arıza Kayıt Paneli")
        self.setGeometry(100, 100, 1000, 700)
        
        # Logo ekleme
        self.setWindowIcon(QIcon('logo.png'))
        
        # Logo label'ı oluşturma
        self.logo_label = QLabel()
        logo_pixmap = QPixmap('logo.png')
        scaled_logo = logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(scaled_logo)
        self.logo_label.setAlignment(Qt.AlignCenter)
        
        self.init_ui()
        self.create_database()
        self.apply_styles()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Logo'yu layout'a ekleme
        layout.addWidget(self.logo_label)

        # Form alanları
        form_group = QGroupBox("Arıza Kaydı")
        form_layout = QFormLayout()

        # Birim bilgileri
        self.birim_adi = QLineEdit()
        self.cihaz_turu = QLineEdit()
        self.ariza_tanimi = QTextEdit()

        # Form elemanlarını yerleştirme
        form_layout.addRow("Birim:", self.birim_adi)
        form_layout.addRow("Cihaz Türü:", self.cihaz_turu)
        form_layout.addRow("Arıza Tanımı:", self.ariza_tanimi)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Butonlar
        button_layout = QHBoxLayout()

        kaydet_btn = QPushButton("Kaydet")
        kaydet_btn.clicked.connect(self.kayit_ekle)
        kaydet_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))

        listele_btn = QPushButton("Listele")
        listele_btn.clicked.connect(self.kayitlari_listele)
        listele_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))

        duzenle_btn = QPushButton("Düzenle")
        duzenle_btn.clicked.connect(self.kayit_duzenle)
        duzenle_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogStart))

        sil_btn = QPushButton("Sil")
        sil_btn.clicked.connect(self.kayit_sil)
        sil_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))

        yazdir_btn = QPushButton("Yazdır")
        yazdir_btn.clicked.connect(self.kayit_yazdir)
        yazdir_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))

        button_layout.addWidget(kaydet_btn)
        button_layout.addWidget(listele_btn)
        button_layout.addWidget(duzenle_btn)
        button_layout.addWidget(sil_btn)
        button_layout.addWidget(yazdir_btn)
        layout.addLayout(button_layout)

        # Arama alanı
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ara...")
        self.search_input.textChanged.connect(self.search_records)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Tablo
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["ID", "Birim", "Cihaz Türü", "Arıza Tanımı"])
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows)
        self.tablo.setSelectionMode(QTableWidget.SingleSelection)
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.verticalHeader().setVisible(False)
        layout.addWidget(self.tablo)

    def kayitlari_listele(self):
        conn = sqlite3.connect('teknik_servis.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM arizalar')
        kayitlar = cursor.fetchall()
        conn.close()

        self.tablo.setRowCount(len(kayitlar))
        for row, kayit in enumerate(kayitlar):
            for col, veri in enumerate(kayit):
                self.tablo.setItem(row, col, QTableWidgetItem(str(veri)))

    def search_records(self):
        search_text = self.search_input.text().lower()
        for row in range(self.tablo.rowCount()):
            match_found = False
            for col in range(self.tablo.columnCount()):
                item = self.tablo.item(row, col)
                if item and search_text in item.text().lower():
                    match_found = True
                    break
            self.tablo.setRowHidden(row, not match_found)

    def kayit_sil(self):
        selected_row = self.tablo.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek kaydı seçin!")
            return

        reply = QMessageBox.question(self, "Silme Onayı", 
                                   "Bu kaydı silmek istediğinizden emin misiniz?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            kayit_id = self.tablo.item(selected_row, 0).text()
            conn = sqlite3.connect('teknik_servis.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM arizalar WHERE id=?', (kayit_id,))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Başarılı", "Kayıt başarıyla silindi!")
            self.kayitlari_listele()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 1ex;
                font-weight: bold;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit, QTextEdit, QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                border: 1px solid #ddd;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
                border: 1px solid #2c3e50;
            }
        """)

    def kayit_ekle(self):
        birim = self.birim_adi.text()
        cihaz_turu = self.cihaz_turu.text()
        ariza_tanimi = self.ariza_tanimi.toPlainText()

        if not birim or not cihaz_turu or not ariza_tanimi:
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
            return

        conn = sqlite3.connect('teknik_servis.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO arizalar (birim, cihaz_turu, ariza_tanimi)
        VALUES (?, ?, ?)
        ''', (birim, cihaz_turu, ariza_tanimi))
        conn.commit()
        conn.close()

        self.birim_adi.clear()
        self.cihaz_turu.clear()
        self.ariza_tanimi.clear()
        
        QMessageBox.information(self, "Başarılı", "Kayıt başarıyla eklendi!")
        self.kayitlari_listele()

    def kayit_duzenle(self):
        selected_row = self.tablo.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlenecek kaydı seçin!")
            return

        kayit_id = self.tablo.item(selected_row, 0).text()
        birim = self.birim_adi.text()
        cihaz_turu = self.cihaz_turu.text()
        ariza_tanimi = self.ariza_tanimi.toPlainText()

        conn = sqlite3.connect('teknik_servis.db')
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE arizalar 
        SET birim=?, cihaz_turu=?, ariza_tanimi=?
        WHERE id=?
        ''', (birim, cihaz_turu, ariza_tanimi, kayit_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Başarılı", "Kayıt başarıyla güncellendi!")
        self.kayitlari_listele()

    def create_database(self):
        conn = sqlite3.connect('teknik_servis.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS arizalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            birim TEXT NOT NULL,
            cihaz_turu TEXT NOT NULL,
            ariza_tanimi TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

    def kayit_yazdir(self):
        selected_row = self.tablo.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen yazdırılacak kaydı seçin!")
            return
    
        printer = QPrinter(QPrinter.HighResolution)
        # Varsayılan kağıt boyutunu ayarla (60mm x 30mm)
        printer.setPageSize(QPrinter.Custom)
        printer.setPaperSize(QSizeF(60, 30), QPrinter.Millimeter)
        
        dialog = QPrintDialog(printer, self)

        if dialog.exec_() == QPrintDialog.Accepted:
            # Seçili satırın verilerini al
            kayit_id = self.tablo.item(selected_row, 0).text()
            birim = self.tablo.item(selected_row, 1).text()
            cihaz_turu = self.tablo.item(selected_row, 2).text()
            ariza_tanimi = self.tablo.item(selected_row, 3).text()

            # Yazdırma için HTML içeriği oluştur
            html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ text-align: center; margin-bottom: 30px; }}
                        .content {{ margin: 20px 0; }}
                        .field {{ margin: 10px 0; }}
                        .label {{ font-weight: bold; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h2>Teknik Servis Arıza Kaydı</h2>
                    </div>
                    <div class="content">
                        <div class="field">
                            <span class="label">Kayıt No:</span> {kayit_id}
                        </div>
                        <div class="field">
                            <span class="label">Birim:</span> {birim}
                        </div>
                        <div class="field">
                            <span class="label">Cihaz Türü:</span> {cihaz_turu}
                        </div>
                        <div class="field">
                            <span class="label">Arıza Tanımı:</span> {ariza_tanimi}
                        </div>
                    </div>
                    <div style='margin-top: 30px; text-align: right;'>
                        <p>Tarih: {QDate.currentDate().toString("dd.MM.yyyy")}</p>
                    </div>
                </body>
                </html>
            """
            
            # HTML içeriğini yazdır
            document = QTextDocument()
            document.setHtml(html_content)
            document.print_(printer)
            
            QMessageBox.information(self, "Başarılı", "Yazdırma işlemi tamamlandı!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TeknikServisApp()
    window.show()
    sys.exit(app.exec_())