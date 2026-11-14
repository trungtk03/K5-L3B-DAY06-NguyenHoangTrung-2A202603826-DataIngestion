# Báo cáo cá nhân — Day 06: Data Ingestion Engineering

**Học viên:** Nguyễn Hoàng Trung  
**MSSV:** 2A202603826  
**Lớp:** L3B  
**Chủ đề:** Sổ tay Sinh viên & Quy chế Đào tạo Đại học 2024-2025 (University Academic Handbook & Student Regulations)  
**Kho mã nguồn bài nộp:** https://github.com/trungtk03/K5-L3B-DAY06-NguyenHoangTrung-2A202603826-DataIngestion.git  

---

## 1. Dữ liệu và pipeline

- **Chủ đề, nguồn/quyền, số trang và quy tắc tính trang:**
  - *Chủ đề:* Sổ tay Học vụ, Khảo thí, Công tác Sinh viên, Ký túc xá & Nghiên cứu Khoa học năm học 2024–2025.
  - *Nguồn và quyền sử dụng:* Tài liệu học vụ công khai nội bộ nhà trường (Open Campus Educational Resource / MIT Educational Use). Dữ liệu được lưu trữ trực tiếp tại `data/so_tay_sinh_vien_2024.json` và được khai báo chi tiết trong manifest tại `data/manifest.json`.
  - *Số trang và quy tắc tính trang:* Toàn bộ tài liệu gồm **32 trang nội dung chuẩn hóa** (vượt yêu cầu tối thiểu ≥30 trang). Mỗi trang tương ứng với một chương/đơn vị nội dung hoàn chỉnh và chứa tối thiểu **1.500 ký tự chuẩn hóa Unicode NFC** (không tính trang bìa, mục lục hay trang trống). Tổng dung lượng văn bản đạt **56.075 ký tự**, trang ngắn nhất đạt 1.536 ký tự và trang dài nhất đạt 2.455 ký tự.

- **Chuẩn hóa, lỗi và giới hạn:**
  - *Chuẩn hóa Unicode:* Áp dụng `unicodedata.normalize("NFC", text)` để chuẩn hóa bảng mã tiếng Việt có dấu, triệt tiêu lỗi tách rời nguyên âm và dấu thanh (NFD vs NFC).
  - *Xử lý khoảng trắng:* Loại bỏ các ký tự xuống dòng thừa (`\r\n` thành `\n`), chuẩn hóa khoảng trắng giữa các từ nhưng bảo toàn nghiêm ngặt phân cách đoạn văn (`\n\n`) nhằm hỗ trợ chiến lược chia chunk cấu trúc.
  - *Xử lý lỗi và giới hạn trích xuất:* Loại bỏ các ký tự điều khiển ẩn không in được; phát hiện và cảnh báo các đoạn văn rỗng. Giới hạn: văn bản dạng bảng phức hợp hoặc ký hiệu toán học đặc biệt được chuyển đổi sang định dạng văn bản có cấu trúc gạch đầu dòng để duy trì tính toàn vẹn ngữ nghĩa.

- **Embedding model/provider/version/số chiều, vector store/version, metric, lệnh chạy và chi phí:**
  - *Embedding model:* `sentence-transformers/all-MiniLM-L6-v2` (Sentence Transformers v6.3.0, PyTorch 2.15.0). Mô hình chạy local 100%, tạo ra vector biểu diễn dày đặc (dense embeddings) chuẩn hóa `normalize_embeddings=True`.
  - *Số chiều (Dimensions):* 384 chiều.
  - *Vector Store:* `ChromaDB` (v1.5.9), triển khai ở chế độ lưu trữ bền vững trên ổ đĩa cục bộ (`chromadb.PersistentClient(path="./chroma_db")`).
  - *Similarity Metric:* Cosine Similarity (`hnsw:space = "cosine"`), điểm tương đồng tính toán qua công thức `Similarity = 1.0 - Cosine_Distance`.
  - *Lệnh chạy tái lập:* 
    ```bash
    python -m src.run
    ```
  - *Chi phí (Cost):* **$0.00** (Hoàn toàn miễn phí nhờ sử dụng mô hình mã nguồn mở chạy local và vector database lưu trữ tệp cục bộ, không phát sinh chi phí gọi API thương mại).

- **Metadata bắt buộc, trường lọc bổ sung, nguồn giá trị và lý do chọn:**
  - *Metadata bắt buộc:* `document_id` (`handbook_2024`), `source` (`data/so_tay_sinh_vien_2024.json`), `page` (từ 1 đến 32). Giúp truy vết chính xác nguồn gốc vật lý của từng bằng chứng và hỗ trợ trích dẫn.
  - *Trường lọc bổ sung:*
    - `category`: Phân loại 5 lĩnh vực nghiệp vụ rõ ràng: `quy_che_dao_tao` (trang 1–10), `khao_thi_dam_bao_chat_luong` (trang 11–16), `cong_tac_sinh_vien` (trang 17–22), `ky_tuc_xa_noi_tru` (trang 23–27), `nghien_cuu_khoa_hoc` (trang 28–32).
    - `section`: Tên chương và chủ đề điều khoản cụ thể.
    - `year`: 2024 (năm ban hành quy chế).
    - `audience`: `sinh_vien_dai_hoc`.
  - *Lý do chọn:* Trường `category` là thuộc tính phân vùng nghiệp vụ tự nhiên, phản ánh chính xác ngữ cảnh câu hỏi của người dùng (ví dụ: câu hỏi về kỷ luật phòng thi thuộc `khao_thi_dam_bao_chat_luong`, câu hỏi về đề tài sinh viên thuộc `nghien_cuu_khoa_hoc`). Việc lọc theo `category` giúp triệt tiêu hoàn toàn các phân mảnh nhiễu (distractors) từ các chương khác có từ khóa tương đồng (như "kỷ luật", "kinh phí", "điểm số").

---

## 2. Cấu hình và benchmark

- **A / B / C (tham số cụ thể, khác biệt duy nhất B–C):**
  - **Cấu hình A (Fixed-size Window):** Chunking kích thước cố định `chunk_size = 500` ký tự, bước nhảy chồng lấn `overlap = 50` ký tự. Metadata gồm `document_id`, `source`, `page`. Không áp dụng lọc metadata khi truy vấn. Tổng sinh ra **137 chunks**.
  - **Cấu hình B (Structure-Aware / By Paragraph):** Chunking theo ranh giới cấu trúc văn bản (`\n\n`, các điều khoản/khoản luật), gom nhóm đoạn văn với giới hạn `max_size = 800` ký tự. Lưu cùng hệ thống metadata với A và bổ sung `category`, `section`. Không áp dụng lọc khi truy vấn. Tổng sinh ra **117 chunks**.
  - **Cấu hình C (Structure-Aware + Metadata Filter):** Sử dụng **chính xác tập chunk và vector của Cấu hình B** (117 chunks, cùng độ dài và nội dung). Khi truy vấn, nếu câu hỏi có điều kiện lọc ngữ cảnh, hệ thống kích hoạt bộ lọc `where={"category": {"$eq": filter_val}}` trong ChromaDB. **Khác biệt duy nhất giữa B và C là việc áp dụng bộ lọc metadata trong truy xuất**, đảm bảo nguyên tắc so sánh có kiểm soát (controlled experiment).

- **≥20 câu: phân chia ≥15 dev / ≥5 test, câu metadata filter và cách kiểm chứng evidence:**
  - *Tổng số câu hỏi:* **20 câu hỏi**, được lưu trữ độc lập tại `benchmark/benchmark_questions.json`.
  - *Phân chia split:* **15 câu Dev** (`q01` đến `q15`) và **5 câu Test** (`q16` đến `q20`). Việc phân chia được cố định trước khi thực nghiệm chạy pipeline.
  - *Độ đa dạng dạng câu hỏi:*
    - Câu trực tiếp (`truc_tiep`): `q01`, `q04`, `q05`, `q08`, `q13`, `q15`, `q16` (hỏi chính xác ngưỡng số liệu, điều kiện).
    - Câu diễn đạt lại (`dien_dat_lai`): `q02`, `q12`, `q19` (dùng từ đồng nghĩa, cấu trúc câu biến đổi so với văn bản gốc).
    - Câu điều kiện/ngoại lệ (`dieu_kien_ngoai_le`): `q03`, `q06`, `q07`, `q10`, `q14`, `q18`, `q20` (hỏi về điều kiện cấm thi, trường hợp ngoại lệ, chế tài nặng).
    - Câu kiểm tra metadata filter (`metadata_filter`): Gồm **3 câu** (`q09`, `q11` thuộc Dev; `q17` thuộc Test). Giá trị lọc được giả định cung cấp trước bởi ngữ cảnh người dùng:
      - `q09`: `filter = {"category": "khao_thi_dam_bao_chat_luong"}`
      - `q11`: `filter = {"category": "cong_tac_sinh_vien"}`
      - `q17`: `filter = {"category": "nghien_cuu_khoa_hoc"}` (nằm trong tập Test)
  - *Cách kiểm chứng evidence:* Mỗi câu hỏi đều được gán `expected_answer`, `gold_source_id`, `gold_page` và đoạn trích dẫn nguyên văn `evidence_quote`. Trước khi chạy thử nghiệm, từng đoạn bằng chứng đã được rà soát trực tiếp trong corpus để đảm bảo bằng chứng tồn tại thực tế và đủ thông tin để trả lời trọn vẹn câu hỏi.

- **Tiêu chí chọn chiến lược đã chốt trước khi xem test:**
  - *Quy tắc ưu tiên:*
    1. **Tính mạch lạc của Chunk (Coherence Score /2):** Phải đảm bảo ý tứ nguyên vẹn để mô hình sinh câu trả lời không bị ảo giác (hallucination) do mất ngữ cảnh.
    2. **Độ phủ bằng chứng truy xuất (Evidence Hit@3):** Khả năng tìm thấy bằng chứng hợp lệ trong top-3 kết quả trả về.
    3. **Chất lượng Grounding thủ công (/2) trên tập Test:** Đo lường mức độ đầy đủ của ngữ cảnh để người dùng hoặc LLM có thể trả lời và đối soát nguồn gốc.
    4. **Hiệu năng tài nguyên:** Ưu tiên chiến lược có số lượng chunk gọn gàng và thời gian xử lý nhanh.

---

## 3. Kết quả

### Bảng 1: Chỉ số định lượng truy xuất (Retrieval Accuracy & Resources)

| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian Ingest | Chi phí |
|---|---|---|---|---|---|---|
| **Strategy A** (Fixed 500/50) | Dev | 4/15 (26.67%) | 10/15 (66.67%) | 137 | 4.02s | $0.00 |
| **Strategy A** (Fixed 500/50) | Test | 0/5 (0.00%) | 2/5 (40.00%) | 137 | — | $0.00 |
| **Strategy B** (Paragraph 800) | Dev | 3/15 (20.00%) | 7/15 (46.67%) | 117 | 3.41s | $0.00 |
| **Strategy B** (Paragraph 800) | Test | 0/5 (0.00%) | 3/5 (60.00%) | 117 | — | $0.00 |
| **Strategy C** (Paragraph + Filter) | Dev | 3/15 (20.00%) | 7/15 (46.67%) | 117 | 0.22s | $0.00 |
| **Strategy C** (Paragraph + Filter) | Test | 0/5 (0.00%) | 3/5 (60.00%) | 117 | — | $0.00 |

### Bảng 2: Đánh giá chất lượng và kiểm toán thủ công (Manual Audit & Quality Dimensions)

| Strategy | Coherence trung bình /2 (n=10) | Metadata đủ và đúng (n/N) | Filter tuân thủ (n/N hoặc N/A) | Grounding 0/1/2 (số câu) và trung bình /2 (n=5) |
|---|---|---|---|---|
| **Strategy A** | 1.00 / 2.0 (10) | 15/15 (100%) | N/A (Không dùng filter) | 0: 0 câu \| 1: 3 câu \| 2: 2 câu → **1.40 / 2.0** |
| **Strategy B** | 2.00 / 2.0 (10) | 15/15 (100%) | N/A (Không kích hoạt filter) | 0: 0 câu \| 1: 2 câu \| 2: 3 câu → **1.60 / 2.0** |
| **Strategy C** | 2.00 / 2.0 (10) | 15/15 (100%) | **1/1 (100%)** (Câu q17 filter khớp 100%) | 0: 0 câu \| 1: 2 câu \| 2: 3 câu → **1.60 / 2.0** |

- **Đường dẫn trace, nhãn thủ công và cách chọn mẫu:**
  - File traces đầy đủ:
    - [results/traces_strategy_A.json](file:///c:/Users/Admin/Documents/GitHub_NguyenHoangTrung/K5-L3B-DAY06-NguyenHoangTrung-2A202603826-DataIngestion/results/traces_strategy_A.json)
    - [results/traces_strategy_B.json](file:///c:/Users/Admin/Documents/GitHub_NguyenHoangTrung/K5-L3B-DAY06-NguyenHoangTrung-2A202603826-DataIngestion/results/traces_strategy_B.json)
    - [results/traces_strategy_C.json](file:///c:/Users/Admin/Documents/GitHub_NguyenHoangTrung/K5-L3B-DAY06-NguyenHoangTrung-2A202603826-DataIngestion/results/traces_strategy_C.json)
  - File tóm tắt chỉ số: [results/benchmark_summary.json](file:///c:/Users/Admin/Documents/GitHub_NguyenHoangTrung/K5-L3B-DAY06-NguyenHoangTrung-2A202603826-DataIngestion/results/benchmark_summary.json)
  - File kiểm toán thủ công chi tiết: [results/manual_evaluation.json](file:///c:/Users/Admin/Documents/GitHub_NguyenHoangTrung/K5-L3B-DAY06-NguyenHoangTrung-2A202603826-DataIngestion/results/manual_evaluation.json)
  - Nhật ký thí nghiệm: [artifacts/experiment_log.csv](file:///c:/Users/Admin/Documents/GitHub_NguyenHoangTrung/K5-L3B-DAY06-NguyenHoangTrung-2A202603826-DataIngestion/artifacts/experiment_log.csv)
  - *Cách chọn mẫu kiểm toán:*
    - **Chunk Coherence:** Cố định 10 vị trí đầu tiên của tài liệu nguồn tương ứng với 10 trang đầu (Trang 1 đến Trang 10) trước khi xem điểm số. Chấm điểm chunk đại diện ở thang 0 (cắt đứt ý), 1 (hiểu một phần), 2 (hoàn chỉnh, tự giải thích).
    - **Metadata Usefulness:** Kiểm tra toàn bộ 5 câu hỏi Test × top-3 kết quả = 15 bản ghi chunk cho từng chiến lược đối soát với tài liệu nguồn gốc.
    - **Grounding Quality:** Đọc độc lập 5 câu hỏi Test (`q16`–`q20`) cho từng cấu hình để chấm mức độ cung cấp ngữ cảnh đầy đủ.

---

## 4. Phân tích và kết luận

### So sánh có kiểm soát A–B và B–C

1. **So sánh A–B (Fixed-size 500 ký tự vs Structure-aware 800 ký tự):**
   - *Tính mạch lạc (Coherence):* Cấu hình B vượt trội hoàn toàn với điểm trung bình **2.00/2.0** so với **1.00/2.0** của Cấu hình A. Ở Cấu hình A, cửa sổ cố định 500 ký tự cắt ngang giữa các điều khoản luật (ví dụ: cắt đứt giữa câu quy định về nghĩa vụ sinh viên ở Trang 1 và 2), khiến câu văn cụt lủn và mất chủ ngữ. Trong khi đó, Cấu hình B gom trọn vẹn từng Điều/Khoản nên giữ nguyên tiêu đề và điều kiện thi hành.
   - *Hiệu năng và kích thước lưu trữ:* Cấu hình B chỉ tạo ra **117 chunks**, giảm **14.6% số lượng chunk** so với Cấu hình A (137 chunks). Thời gian tạo embedding và indexing của B nhanh hơn (3.41s so với 4.02s của A).
   - *Truy xuất trên tập Test:* Trên tập Test, Cấu hình B đạt Hit@3 là **3/5 (60%)**, cao hơn Cấu hình A đạt **2/5 (40%)**. Nguyên nhân do các chunk đoạn văn hoàn chỉnh chứa đầy đủ ngữ cảnh của câu hỏi, giúp mô hình embedding so khớp ngữ nghĩa chính xác hơn các mẩu cắt vụn của A.

2. **So sánh B–C (Ảnh hưởng độc lập của Metadata Filter):**
   - Giữa B và C, cấu trúc chunk và vector embedding hoàn toàn giống hệt nhau 100%. Điểm khác biệt duy nhất là Cấu hình C sử dụng metadata filter khi câu hỏi có yêu cầu lọc.
   - *Minh chứng tác động loại trừ nhiễu (Deduplication / Distractor Removal):*
     - Xem xét câu **q17** (Test set): *"Theo danh mục quy định nghiên cứu khoa học, mức kinh phí hỗ trợ tối đa cho đề tài NCKH sinh viên cấp trường nghiệm thu đạt loại A là bao nhiêu?"*
       - Ở **Cấu hình B** (không lọc): Kết quả Rank 1 là chunk `p1_para_03` thuộc lĩnh vực `quy_che_dao_tao` (nhiễu từ vựng về số tiết/giờ nghiên cứu). Chunk đáp án đúng `p29_para_01` bị đẩy xuống tận **Rank 3**.
       - Ở **Cấu hình C** (lọc `category = "nghien_cuu_khoa_hoc"`): Toàn bộ các chunk ngoài lĩnh vực NCKH bị loại bỏ ngay từ tầng database. Chunk `p29_para_01` (Gold Evidence) ngay lập tức **tăng hạng lên Rank 2**, và 100% top-3 kết quả đều thuộc phạm vi nghiên cứu khoa học.
     - Xem xét câu **q09** (Dev set): Hỏi về mức trừ điểm bài thi do nhìn bài (`khao_thi_dam_bao_chat_luong`). Ở Cấu hình B, Rank 2 bị lẫn chunk `p25` thuộc Ký túc xá. Ở Cấu hình C, kết quả chỉ chứa các quy định thi cử, đưa thêm một chunk đúng khác của `p12` vào top-3.

### Hai ví dụ sai cụ thể (Error Analysis)

1. **Ví dụ 1: Câu `q20` (Test set) — Lỗi từ vựng trừu tượng và ranh giới phân mảnh:**
   - *Câu hỏi:* *"Những trường hợp cụ thể nào theo quy chế đào tạo sẽ khiến sinh viên bị áp dụng hình thức kỷ luật buộc thôi học?"*
   - *Gold Source:* `handbook_2024`, Trang 5 (`gold_page: 5`), đoạn trích dẫn: *"Sinh viên sẽ bị buộc thôi học nếu thuộc một trong các trường hợp: bị cảnh báo học tập 03 lần liên tiếp, hoặc vượt quá thời gian tối đa được phép học tập tại trường."*
   - *Kết quả thực tế ở cả 3 chiến lược:* Hit@1 = False, Hit@3 = False. Top-3 trả về gồm các chunk từ Trang 22 (Điều 49 về Kỷ luật sinh viên chung) và Trang 31 (Xử lý vi phạm liêm chính khoa học).
   - *Nguyên nhân thất bại:* Cụm từ "buộc thôi học" xuất hiện ở cả Điều 13 (Xử lý học vụ, Trang 5) và Điều 49 (Kỷ luật vi phạm pháp luật/tệ nạn, Trang 22). Mô hình embedding `all-MiniLM-L6-v2` chấm điểm tương đồng cosine cho đoạn văn về kỷ luật hình sự/pháp luật ở Trang 22 cao hơn (0.83) so với đoạn cảnh báo học vụ học tập ở Trang 5 (0.78). Điều này cho thấy với các thuật ngữ xuất hiện ở nhiều bối cảnh khác nhau, nếu không có câu hỏi lọc chuyên biệt (`section = "hoc_vu"`), bộ tìm kiếm ngữ nghĩa đơn thuần dễ bị thiên lệch sang các đoạn có mật độ từ khóa kỷ luật cao hơn.

2. **Ví dụ 2: Câu `q11` (Dev set) — Lỗi tương đồng ngữ nghĩa mờ nhạt (Semantic Drift):**
   - *Câu hỏi:* *"Trong công tác sinh viên, mức điểm rèn luyện bao nhiêu điểm thì sinh viên được xếp loại rèn luyện Tốt?"*
   - *Gold Source:* `handbook_2024`, Trang 17, đoạn: *"Xếp loại rèn luyện Tốt áp dụng cho điểm rèn luyện đạt từ 80 đến 89 điểm."*
   - *Kết quả thực tế ở Cấu hình B:* Top-1 trả về `p9_para_03` (Thực tập tốt nghiệp), Top-2 trả về `p23_para_03` (Ký túc xá). Hit@3 = False.
   - *Nguyên nhân thất bại:* Từ "Tốt" trong tiếng Việt vừa là tính từ chung, vừa là danh từ xếp loại (Xuất sắc / Tốt / Khá / Trung bình). Câu hỏi ngắn khiến mô hình embedding tiếng Anh/đa ngữ nhẹ không bắt được trọng tâm thang điểm mà tập trung vào các từ "sinh viên", "mức điểm". Khi sang Cấu hình C, nhờ bộ lọc `category = "cong_tac_sinh_vien"`, kết quả đã thu hẹp về Trang 17 và Trang 22, tuy nhiên chunk cụ thể về khung điểm xếp ở Rank 4 (sát top-3), dẫn tới việc vẫn hụt Hit@3.

### Chiến lược chọn, đánh đổi và điều kiện áp dụng

- **Chiến lược được lựa chọn:** **Cấu hình C (Structure-aware Chunking kết hợp Metadata Filtering khi có điều kiện lọc)** là chiến lược tối ưu nhất cho bài toán tri thức có cấu trúc này.
- **Các đánh đổi (Trade-offs):**
  - *Độ phức tạp tiền xử lý:* Chiến lược B/C đòi hỏi phải viết parser nhận diện ranh giới đoạn văn và phân loại metadata `category` trong lúc trích xuất, phức tạp hơn việc cắt độ dài cố định của A.
  - *Độ phụ thuộc vào truy vấn:* Cấu hình C chỉ phát huy tối đa sức mạnh khi người dùng (hoặc giao diện ứng dụng) chỉ định rõ phân vùng tìm kiếm. Nếu người dùng không cung cấp metadata lọc, Cấu hình C quay về tương đương Cấu hình B.
  - *Bảo toàn thông tin vs Dung lượng chunk:* Chunk theo đoạn văn (max 800 ký tự) có kích thước trung bình lớn hơn chunk 500 ký tự, nhưng bù lại mang lại điểm Coherence hoàn hảo (2.0/2.0), triệt tiêu hiện tượng câu văn mất ngữ nghĩa.

### Hạn chế và Hướng cải tiến

- **Hạn chế của nghiên cứu:**
  - Kích thước tập Test gồm 5 câu là tương đối nhỏ, mang tính chất kiểm tra điểm (spot check) và kiểm toán định tính chứ chưa đủ lớn để đo lường thống kê mang tính khái quát hóa cao.
  - Mô hình embedding `all-MiniLM-L6-v2` là mô hình gọn nhẹ (384 chiều) được tối ưu cho tiếng Anh; khi xử lý tiếng Việt pháp lý/học vụ chuyên sâu, một số thuật ngữ đa nghĩa (như "buộc thôi học", "Tốt") chưa đạt độ phân tách tối ưu so với các mô hình chuyên biệt tiếng Việt lớn hơn (như `bge-m3` hoặc `vietnamese-bi-encoder`).
- **Hướng cải tiến nếu mở rộng:**
  - *Hybrid Retrieval (Dense + BM25):* Kết hợp giữa tìm kiếm ngữ nghĩa vector và tìm kiếm từ khóa chính xác BM25 (Reciprocal Rank Fusion). Điều này sẽ giải quyết triệt để các câu hỏi chứa con số định lượng chính xác (như "14 tín chỉ", "1000W", "20%").
  - *Hierarchical / Parent-Document Retrieval:* Lưu trữ các chunk nhỏ (200-300 ký tự) để tìm kiếm vector đạt độ nhạy cao, nhưng khi trả về cho LLM hoặc người dùng thì truy xuất toàn bộ đoạn văn cha (Parent Chunk) để bảo toàn tối đa tính mạch lạc.
