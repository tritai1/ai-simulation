AI-Simulation

## **Tổng Quan**
- **Mô tả**: Dự án `ai-simulation` là một khung (framework) để xây dựng, mô phỏng và triển khai hệ thống tác nhân AI phối hợp (agents) với khả năng RAG (Retrieval-Augmented Generation), orchestration và API cho frontend. Mục tiêu là cung cấp luồng dữ liệu từ thu thập → tiền xử lý → embedding → truy vấn vector → kết hợp mô hình sinh câu trả lời.

## **Cấu trúc thư mục chính**
- **app**: Mã nguồn chính của ứng dụng (khởi tạo app, agents, API, core, services, orchestration, RAG).
- **app/main.py**: Entrypoint để chạy server/ứng dụng.
- **app/api**: Endpoints REST hoặc Web API để tương tác với frontend/khách.
- **app/agents**: Các định nghĩa tác nhân (agent) — logic ra quyết định, luồng làm việc, task handlers.
- **app/core**: Thành phần lõi xử lý luồng dữ liệu và tích hợp mô hình.
- **app/RAG**: Mã xử lý lưu trữ vector, indexing (FAISS), truy vấn ngữ nghĩa, và tích hợp embedding.
- **app/services**: Kết nối tới external services (ví dụ: mô hình LLM, DB, external APIs).
- **app/orchestration**: Luồng phối hợp nhiều agents, quản lý workflow, retry, timeout.
- **data**: Scripts và mẫu dữ liệu dùng cho demo và thử nghiệm.
- **faiss_index**: (nếu tồn tại) lưu các index FAISS đã xây sẵn.
- **gucci_env / rag_env**: virtualenv/venv mẫu (không commit code môi trường).

## **Luồng xử lý tổng quát (How it works)**
1. **Thu thập dữ liệu**: dùng các script trong `data/` hoặc crawlers (nếu có) để gom văn bản.
2. **Tiền xử lý**: chuẩn hoá văn bản, tách câu, loại bỏ ký tự thừa, tokenization tùy mục đích.
3. **Tạo embedding**: chạy embedding model (local hoặc cloud) trên đoạn văn/đoạn tài liệu, lưu vector cùng metadata.
4. **Xây index vector**: dùng FAISS (thư mục `faiss_index`) để xây index cho tìm kiếm gần kề (k-NN).
5. **Truy vấn RAG**: khi nhận truy vấn, hệ thống:
   - truy vấn index để lấy các đoạn ngữ cảnh liên quan,
   - ghép ngữ cảnh này vào prompt,
   - gọi LLM để sinh câu trả lời (có thể kèm chuỗi thao tác của agent).
6. **Orchestration & Agents**: nếu câu trả lời cần nhiều bước (multi-step), `orchestration` sẽ phân nhiệm cho các `agents` (ví dụ: fetcher, reasoner, verifier), kết hợp kết quả, xử lý lỗi và trả về response.

## **Chi tiết per-module (cách xử lý từng phần)**
- **`app/agents`**: mỗi agent có 3 phần chính: nhận input → xử lý (có thể gọi service/LLM/index) → trả output. Agents có thể là synchronous hoặc asynchronous. Các agents quan trọng:
  - **RetrieverAgent**: gọi `app/RAG` để lấy văn bản liên quan.
  - **ReasonerAgent**: gọi LLM với prompt template, dùng context từ Retriever.
  - **ExecutorAgent**: thực thi tác vụ ngoài (gọi API, DB) nếu cần.
- **`app/RAG`**: chứa adapter đến hệ embedding và index. Chức năng:
  - biên dịch/cập nhật index từ nguồn dữ liệu,
  - hỗ trợ thêm/loại bỏ document, rebuild index,
  - trả về top-k documents với điểm tương đồng.
- **`app/services`**: adapter tới các mô hình/third-party. Ví dụ:
  - `llm_service.py`: bao wrapper gọi LLM (OpenAI, local LLM), hỗ trợ retries, rate-limit handling,
  - `embedding_service.py`: wrapper gọi model embedding,
  - `storage_service.py`: wrapper tới DB/kiến trúc lưu trữ metadata.
- **`app/orchestration`**: quản lý workflow, gồm scheduler/worker (nếu có), step chaining, timeouts và error handling. Orchestration quyết định thứ tự gọi agents và gom kết quả.
- **`app/api`**: định nghĩa endpoint (ví dụ `/query`, `/admin/index`, `/agents/run`). Mỗi endpoint: validate input → trigger orchestration hoặc agent → trả JSON.

## **Thiết lập môi trường (Quick Start)**
1. Tạo virtual environment (Python 3.10+ khuyến nghị):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Cài dependencies:

```powershell
pip install -r requirements.txt
```

3. Thiết lập biến môi trường (ví dụ keys cho LLM):

```powershell
$env:OPENAI_API_KEY="your_key_here"
# hoặc tạo .env và load trước khi chạy
```

4. Chạy ứng dụng (local):

```powershell
python app\main.py
```

Gợi ý: nếu `app/main.py` triển khai Flask/FastAPI, dùng `uvicorn` hoặc `flask run` theo file cấu hình.

## **Chạy ví dụ truy vấn (curl)**

```bash
curl -X POST "http://127.0.0.1:8000/query" -H "Content-Type: application/json" -d '{"question":"Tóm tắt tài liệu X"}'
```

## **Cách debug & kiểm thử**
- Bật logging ở mức DEBUG trong `app/core` để theo dõi luồng dữ liệu.
- Kiểm tra index FAISS bằng script nhỏ: load index và gọi truy vấn mẫu.
- Để debug agent: viết unit test cho mỗi agent (mocks cho LLM và RAG).

## **Gợi ý triển khai và nâng cấp**
- Dùng batching khi tạo embedding cho tập lớn để tăng hiệu suất.
- Với dữ liệu lớn, lưu index ra disk và dùng clustering/HNSW để tăng tốc.
- Cân nhắc caching kết quả truy vấn phổ biến.

## **Contributing**
- Mô tả issue → fork → PR. Giữ tests xanh trước khi nộp PR.

## **Tài liệu tham khảo nhanh**
- File entrypoint: [app/main.py](app/main.py)
- Thư mục agents: [app/agents](app/agents)
- RAG: [app/RAG](app/RAG)

---

Nếu bạn muốn tôi mở rộng phần nào (ví dụ: mẫu prompt, ví dụ cụ thể cho từng agent, hoặc script build index), cho biết phần cần mở rộng và tôi sẽ thêm.
