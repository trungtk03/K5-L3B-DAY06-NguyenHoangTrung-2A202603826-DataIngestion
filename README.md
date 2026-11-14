# Day 06 · Data Ingestion Engineering

**Học viên:** Nguyễn Hoàng Trung  
**MSSV:** 2A202603826  
**Lớp:** L3B  
**Chủ đề:** Sổ tay Sinh viên & Quy chế Đào tạo Đại học 2024–2025  
**Repo:** [K5-L3B-DAY06-NguyenHoangTrung-2A202603826-DataIngestion](https://github.com/trungtk03/K5-L3B-DAY06-NguyenHoangTrung-2A202603826-DataIngestion.git)

---

## 📌 Tổng quan bài làm

Dự án hiện thực trọn vẹn pipeline **Data Ingestion Engineering** cho hệ thống tri thức AI Agent / RAG, so sánh có kiểm soát giữa 3 chiến lược tiền xử lý dữ liệu và đánh giá toàn diện theo 5 khía cạnh cốt lõi (Retrieval Accuracy, Chunk Coherence, Metadata Usefulness, Grounding Quality, Data Strategy Impact).

| 📄 Dữ liệu | 🧩 Chiến lược | 🎯 Benchmark | 💰 Chi phí |
|---|---|---|---|
| **32 trang nội dung** chuẩn hóa (56.075 ký tự, ≥1.500 ký tự/trang) | **3 cấu hình (A, B, C)** với so sánh có kiểm soát B–C | **20 câu hỏi** (15 Dev / 5 Test, có 3 câu kiểm tra metadata filter) | **$0.00** (Local Embedding + ChromaDB) |

---

## 🛠️ Công nghệ sử dụng

- **Ngôn ngữ:** Python 3.12
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (Sentence Transformers v6.3.0, PyTorch 2.15.0) — Chạy local 100%, 384 dimensions, cosine similarity.
- **Vector Store:** `ChromaDB` (v1.5.9) — Persistent disk storage (`./chroma_db`), hỗ trợ metadata filtering linh hoạt và idempotent upsert.
- **Tiền xử lý & Chuẩn hóa:** Unicode NFC (`unicodedata`), trích xuất cấu trúc văn bản.

---

## 📂 Cấu trúc mã nguồn

```text
├── data/
│   ├── manifest.json              # Khai báo bản quyền, 32 trang, quy tắc đếm và metadata
│   ├── so_tay_sinh_vien_2024.json # 32 trang nội dung sổ tay sinh viên chuẩn hóa
│   └── generate_corpus.py         # Script tạo và kiểm chứng độ dài từng trang (>=1500 chars)
├── benchmark/
│   └── benchmark_questions.json   # 20 câu hỏi có gold evidence (15 Dev / 5 Test)
├── src/                           # Pipeline chính (đồng bộ tại root và starter/src/)
│   ├── __init__.py
│   ├── models.py                  # Dataclass DocumentPage, Chunk
│   ├── ingestion.py               # Chuẩn hóa Unicode NFC và đọc corpus
│   ├── chunking.py                # Chiến lược Fixed-size (A) và By-paragraph (B/C)
│   ├── embeddings.py              # Sentence Transformers embedder protocol
│   ├── store.py                   # ChromaDB persistent store + cosine search + filter
│   ├── evaluation.py              # Đánh giá Hit@1, Hit@3 và vết truy xuất
│   └── run.py                     # Orchestrator toàn bộ pipeline thí nghiệm
├── artifacts/
│   └── experiment_log.csv         # Bảng tham số, giả thuyết và kết quả A/B/C
├── results/
│   ├── traces_strategy_A.json     # Traces top-3 chi tiết Strategy A
│   ├── traces_strategy_B.json     # Traces top-3 chi tiết Strategy B
│   ├── traces_strategy_C.json     # Traces top-3 chi tiết Strategy C
│   ├── benchmark_summary.json     # Thống kê Hit@1/Hit@3 Dev & Test
│   └── manual_evaluation.json     # Nhãn kiểm toán thủ công Coherence, Metadata, Grounding
├── report/individual/
│   ├── 2A202603826_NguyenHoangTrung.md # Báo cáo cá nhân chi tiết
│   └── MSSV_HoTen.md              # Bản sao báo cáo theo mẫu
├── STUDENT.md                     # Thông tin học viên và repo
└── SUBMISSION.md                  # Checklist nộp bài
```

---

## 🚀 Hướng dẫn cài đặt và chạy

### 1. Cài đặt môi trường

```bash
# Cài đặt các thư viện cần thiết
pip install chromadb sentence-transformers pypdf python-dotenv
```

### 2. Chạy pipeline tự động

```bash
# Chạy pipeline Day 06 từ thư mục gốc
python -m src.run
```

Pipeline sẽ tự động thực hiện:
1. Đọc và kiểm chứng 32 trang tài liệu tại `data/so_tay_sinh_vien_2024.json`.
2. Tạo chunks cho Chiến lược A (137 chunks) và Chiến lược B (117 chunks).
3. Tạo embedding vector và lưu bền vững vào `chroma_db`.
4. Chạy truy vấn benchmark 20 câu hỏi (15 Dev, 5 Test) cho cả 3 chiến lược.
5. Xuất các file trace, tóm tắt chỉ số định lượng và kiểm toán thủ công vào `results/`.
6. Cập nhật nhật ký thí nghiệm tại `artifacts/experiment_log.csv`.

---

## 📊 Tóm tắt kết quả Benchmark

### 1. Chỉ số định lượng truy xuất

| Chiến lược | Phân đoạn | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Số Chunk | Thời gian Ingest | Chi phí |
|---|---|---|---|---|---|---|
| **Strategy A** (Fixed 500/50, No filter) | Dev | 4/15 (26.67%) | 10/15 (66.67%) | 137 | 4.02s | $0.00 |
| **Strategy A** (Fixed 500/50, No filter) | Test | 0/5 (0.00%) | 2/5 (40.00%) | 137 | — | $0.00 |
| **Strategy B** (Paragraph 800, No filter) | Dev | 3/15 (20.00%) | 7/15 (46.67%) | 117 | 3.41s | $0.00 |
| **Strategy B** (Paragraph 800, No filter) | Test | 0/5 (0.00%) | 3/5 (60.00%) | 117 | — | $0.00 |
| **Strategy C** (Paragraph 800 + Metadata Filter) | Dev | 3/15 (20.00%) | 7/15 (46.67%) | 117 | 0.22s | $0.00 |
| **Strategy C** (Paragraph 800 + Metadata Filter) | Test | 0/5 (0.00%) | 3/5 (60.00%) | 117 | — | $0.00 |

### 2. Kiểm toán thủ công 5 khía cạnh chất lượng

- **Chunk Coherence (n=10 mẫu):** Strategy A đạt **1.00 / 2.0** (cửa sổ cố định làm đứt câu/mất chủ ngữ); Strategy B/C đạt **2.00 / 2.0** (bảo toàn trọn vẹn ngữ nghĩa từng điều khoản).
- **Metadata Usefulness (n=15 bản ghi Test):** 100% bản ghi có metadata `source`, `page`, `category`, `section` chính xác và đầy đủ.
- **Filter Compliance:** Câu `q17` (Test) có filter `category = "nghien_cuu_khoa_hoc"` đạt tỷ lệ tuân thủ **100% (1/1)**, triệt tiêu hoàn toàn nhiễu từ các chương khác và đẩy bằng chứng đúng lên Rank 2.
- **Grounding Quality (n=5 câu Test):** Strategy A đạt **1.40 / 2.0**; Strategy B và C đạt **1.60 / 2.0**.

---

## 📝 Báo cáo chi tiết

Toàn bộ phân tích so sánh A–B, B–C, phân tích 2 ví dụ lỗi, đánh đổi kiến trúc và hướng phát triển được trình bày chi tiết tại:
👉 [report/individual/2A202603826_NguyenHoangTrung.md](report/individual/2A202603826_NguyenHoangTrung.md)
