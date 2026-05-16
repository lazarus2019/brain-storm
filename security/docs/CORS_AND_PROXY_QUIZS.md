# 🧠 CORS & PROXY — Quiz & Practice

> **Author**: Special thanks to [anIcedAntFA](https://github.com/anIcedAntFA)\
> **Mục đích**: File câu hỏi này giúp kiểm tra và củng cố kiến thức về CORS và PROXY từ cơ bản đến nâng cao. Bao gồm nhiều dạng câu hỏi: trắc nghiệm, đúng/sai, phân tích tình huống, và tự luận.

> 📖 **Tham khảo**: [CORS & Proxy Deep Dive](./cors-and-proxy-deep-dive.md) | [Infrastructure & App Flow](./infrastructure-and-app-flow.md)

---

## 📚 Mục lục

1. [Cấp độ 1 — Cơ bản (Easy)](#cấp-độ-1--cơ-bản-easy)
2. [Cấp độ 2 — Trung bình (Medium)](#cấp-độ-2--trung-bình-medium)
3. [Cấp độ 3 — Nâng cao (Hard)](#cấp-độ-3--nâng-cao-hard)
4. [Cấp độ 4 — Scenario-based (Expert)](#cấp-độ-4--scenario-based-expert)
5. [Đáp án chi tiết](#đáp-án-chi-tiết)

---

## Cấp độ 1 — Cơ bản (Easy)

### Câu 1 — Trắc nghiệm

**CORS là viết tắt của gì?**

- A. Cross-Origin Resource Sharing
- B. Cross-Origin Request Security
- C. Client-Origin Resource Sharing
- D. Cross-Origin Response Service

---

### Câu 2 — Đúng/Sai

**"CORS là cơ chế bảo mật được thực thi bởi server."**

- ⬜ Đúng
- ⬜ Sai

---

### Câu 3 — Trắc nghiệm

**Hai URL sau có cùng "origin" không?**

```
URL 1: https://www.feelfree.com/about
URL 2: https://www.feelfree.com/api/v1/data
```

- A. Không, vì path khác nhau
- B. Có, vì cùng protocol + domain + port
- C. Không, vì một cái là trang web, một cái là API
- D. Phụ thuộc vào CORS headers

---

### Câu 4 — Trắc nghiệm

**Tại sao Postman KHÔNG bị lỗi CORS?**

- A. Vì Postman có license đặc biệt
- B. Vì Postman tự thêm CORS headers
- C. Vì Postman không phải browser, không áp dụng Same-Origin Policy
- D. Vì Postman bypass firewall

---

### Câu 5 — Đúng/Sai

**"Proxy trong Vite chỉ hoạt động ở môi trường development, không có tác dụng khi build production."**

- ⬜ Đúng
- ⬜ Sai

---

## Cấp độ 2 — Trung bình (Medium)

### Câu 6 — Trắc nghiệm (Chọn nhiều đáp án)

**Những trường hợp nào sau đây là "cross-origin"?**

- ⬜ A. `https://feelfree.com` → `https://api.feelfree.com`
- ⬜ B. `https://feelfree.com/about` → `https://feelfree.com/api`
- ⬜ C. `http://feelfree.com` → `https://feelfree.com`
- ⬜ D. `https://feelfree.com` → `https://feelfree.com:8080`
- ⬜ E. `https://feelfree.com` → `https://public.api.feelfree.com`

---

### Câu 7 — Phân tích Code

**Đoạn Vite proxy config sau có vấn đề gì?**

```typescript
export default defineConfig({
	server: {
		proxy: {
			'/api': {
				target: 'https://api.example.com',
				changeOrigin: false,
				secure: true,
			},
		},
	},
});
```

- A. `changeOrigin` nên là `true` khi proxy đến domain khác
- B. `secure` nên là `false`
- C. Thiếu `rewrite` option
- D. Config hoàn toàn đúng, không có vấn đề

---

### Câu 8 — Trắc nghiệm

**Preflight request là gì?**

- A. Request đầu tiên khi mở trang web
- B. HTTP OPTIONS request browser tự gửi trước cross-origin non-simple request để kiểm tra server có cho phép không
- C. Request kiểm tra SSL certificate
- D. Request kiểm tra server có online không

---

### Câu 9 — Điền vào chỗ trống

**Hoàn thành header để cho phép origin `https://www.feelfree.com` truy cập API, cache preflight 24 giờ, và cho phép gửi custom header `x-inface-api-key`:**

```
Access-Control-Allow-Origin: _______________
Access-Control-Max-Age: _______________
Access-Control-Allow-Headers: _______________
Access-Control-Allow-Methods: _______________
```

---

### Câu 10 — Đúng/Sai

**"Khi server trả về status 200 nhưng browser hiển thị CORS error, có nghĩa là server đã xử lý request thành công nhưng browser chặn response vì thiếu CORS headers."**

- ⬜ Đúng
- ⬜ Sai

---

## Cấp độ 3 — Nâng cao (Hard)

### Câu 11 — Phân tích

**Giải thích tại sao cấu hình sau KHÔNG hoạt động:**

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

→ Viết lại cấu hình đúng nếu bạn cần cho phép credentials từ `https://www.feelfree.com`.

---

### Câu 12 — Trắc nghiệm

**Trong kiến trúc Feel Free Frontend, tại sao Internal API (`/api/v1/*`) KHÔNG gặp vấn đề CORS?**

- A. Vì server cấu hình `Access-Control-Allow-Origin: *`
- B. Vì CloudFront route cả frontend và API dưới cùng domain (`www.feelfree.com`) → same-origin
- C. Vì browser tắt CORS cho `.com` domains
- D. Vì request đi qua WAF nên bypass CORS

---

### Câu 13 — Phân tích tình huống

**Bạn có SPA tại `https://app.example.com` gọi API tại `https://api.example.com`. Mỗi khi load page, app gửi 30 API calls, mỗi call có header `Authorization: Bearer xxx`.**

**Câu hỏi:**

1. Mỗi API call có trigger preflight không? Tại sao?
2. Nếu không cache preflight, tổng cộng bao nhiêu HTTP requests?
3. Nếu set `Access-Control-Max-Age: 3600`, tổng requests giảm bao nhiêu?
4. Chrome thực tế cap max-age ở bao nhiêu?

---

### Câu 14 — So sánh

**So sánh 3 cách giải quyết CORS sau. Phân tích ưu/nhược điểm và khi nào nên dùng:**

| Giải pháp                               | Ưu điểm | Nhược điểm | Khi nào dùng? |
| --------------------------------------- | ------- | ---------- | ------------- |
| Vite Proxy                              | ?       | ?          | ?             |
| Server-side CORS headers                | ?       | ?          | ?             |
| Same-origin deploy (CloudFront routing) | ?       | ?          | ?             |

---

### Câu 15 — Debug

**Developer report: "API hoạt động bình thường trên Postman nhưng browser báo CORS error."**

**Network tab cho thấy:**

```
Request URL: https://api.feelfree.com/articles
Request Method: OPTIONS
Status Code: 405 Method Not Allowed
```

**Câu hỏi:**

1. Lỗi ở đâu? (Browser, server, hay network?)
2. Nguyên nhân cụ thể là gì?
3. Cách fix?

---

## Cấp độ 4 — Scenario-based (Expert)

### Câu 16 — Thiết kế hệ thống

**Bạn được giao thiết kế API Gateway cho hệ thống microservices gồm 5 services. Frontend SPA được deploy trên 3 domains khác nhau (dev, staging, production). Mobile app cũng sử dụng cùng API.**

**Yêu cầu:**

1. Thiết kế CORS policy cho API Gateway
2. Giải thích cách handle dynamic origins (dev/staging/prod)
3. Vẽ diagram flow (mô tả bằng text) cho request từ browser qua Gateway đến service
4. Làm sao đảm bảo mobile app không bị ảnh hưởng bởi CORS config?

---

### Câu 17 — Performance Optimization

**Scenario**: E-commerce SPA có 100k+ users đồng thời. Mỗi page load gọi 20 cross-origin API calls. Không có preflight caching.

**Câu hỏi:**

1. Tính tổng số HTTP requests/second nếu mỗi user refresh page 1 lần/phút
2. Đề xuất 3 cách giảm tải CORS-related requests
3. Ước tính % giảm requests sau khi áp dụng tối ưu
4. Ngoài reduce requests, còn cách nào giảm "resource waste" ở server side?

---

### Câu 18 — Security Analysis

**Một developer đề xuất giải pháp: "Thêm `Access-Control-Allow-Origin: *` cho tất cả API endpoints để hết CORS error."**

**Câu hỏi:**

1. Phân tích 3 rủi ro bảo mật của approach này
2. Đề xuất cách cấu hình CORS an toàn hơn
3. Liệt kê 3 trường hợp mà `*` thực sự OK (acceptable)
4. Tại sao `*` + `credentials: true` không hoạt động? (giải thích theo spec)

---

### Câu 19 — Reverse Proxy Deep Dive

**Trong kiến trúc Feel Free Frontend:**

```
Browser → CloudFront → WAF → ALB → EKS (Backend)
Browser → CloudFront → WAF → S3 (Frontend)
Browser → Inface Gateway → QuickBoard API
```

**Câu hỏi:**

1. CloudFront đóng vai trò proxy nào? (Forward proxy hay Reverse proxy?)
2. Inface Gateway đóng vai trò gì trong CORS flow?
3. Nếu WAF block request vì IP không hợp lệ, browser nhận HTTP status code gì?
4. Tại sao QuickBoard API call cần đi trực tiếp từ browser (thay vì qua CloudFront)?

---

### Câu 20 — Tự build Proxy

**Bạn cần build một CORS proxy server bằng Go/Node.js cho mục đích development. Proxy này nhận request từ `localhost:3000`, forward đến `https://api.feelfree.com`, và thêm CORS headers vào response.**

**Câu hỏi:**

1. Viết pseudo-code cho middleware chain: Logging → CORS → Rate Limit → Proxy
2. Giải thích tại sao proxy server không bị CORS (gợi ý: server-to-server)
3. CORS proxy có nên dùng trong production không? Tại sao?
4. Nêu 3 security concerns khi deploy open CORS proxy

---

## Đáp án chi tiết

### Câu 1 — **A. Cross-Origin Resource Sharing**

CORS = **C**ross-**O**rigin **R**esource **S**haring. Đây là cơ chế cho phép server chỉ định origins nào được phép truy cập resources. Được định nghĩa trong [WHATWG Fetch Standard](https://fetch.spec.whatwg.org/#http-cors-protocol).

---

### Câu 2 — **Sai** ❌

CORS được **thực thi bởi browser**, không phải server. Server chỉ trả về CORS headers trong response, browser đọc headers đó và quyết định cho phép hay chặn. Server vẫn xử lý request và trả response bình thường — browser là nơi enforce policy.

---

### Câu 3 — **B. Có, vì cùng protocol + domain + port**

Origin = `protocol` + `hostname` + `port`. Cả hai URL đều có:

- Protocol: `https`
- Hostname: `www.feelfree.com`
- Port: `443` (default HTTPS)

**Path không ảnh hưởng đến origin.** `/about` và `/api/v1/data` cùng origin.

---

### Câu 4 — **C. Vì Postman không phải browser, không áp dụng Same-Origin Policy**

Same-Origin Policy (SOP) chỉ tồn tại trong browser environment. Postman là HTTP client thuần — nó gửi request và nhận response trực tiếp, không có concept "origin" hay security sandbox. Tương tự cho `curl`, server-to-server calls, và mobile native HTTP clients.

---

### Câu 5 — **Đúng** ✅

Vite proxy chỉ hoạt động với `vite dev` (development server). Khi `vite build`, output là static files (HTML/JS/CSS) — không có server nào chạy proxy. Production cần giải pháp khác: server-side CORS headers, reverse proxy (CloudFront, Nginx), hoặc same-origin deploy.

---

### Câu 6 — **A, C, D, E** (tất cả trừ B)

Origin = **protocol + hostname + port**. Path KHÔNG ảnh hưởng.

| Case | Origin 1                   | Origin 2                        | Cross-origin? | Lý do                          |
| ---- | -------------------------- | ------------------------------- | ------------- | ------------------------------ |
| A    | `https://feelfree.com` | `https://api.feelfree.com`  | ✅ **Có**     | Subdomain khác = hostname khác |
| B    | `https://feelfree.com` | `https://feelfree.com`      | ❌ **Không**  | Cùng origin, chỉ khác path     |
| C    | `http://feelfree.com`  | `https://feelfree.com`      | ✅ **Có**     | Protocol khác                  |
| D    | `https://feelfree.com` | `https://feelfree.com:8080` | ✅ **Có**     | Port khác                      |
| E    | `https://feelfree.com` | `https://public.api.feelfree.com`  | ✅ **Có**     | Hostname hoàn toàn khác        |

---

### Câu 7 — **A. `changeOrigin` nên là `true`**

Khi proxy đến domain khác (`api.example.com`), `changeOrigin: true` thay đổi `Host` header trong request thành target domain. Với `changeOrigin: false`, Host header vẫn là `localhost:5173` — nhiều server sẽ reject vì Host header không match.

```typescript
// ✅ Correct config
proxy: {
  '/api': {
    target: 'https://api.example.com',
    changeOrigin: true,  // Host header = api.example.com
    secure: true,        // OK vì target dùng valid SSL
  }
}
```

---

### Câu 8 — **B. HTTP OPTIONS request browser tự gửi trước cross-origin non-simple request**

Preflight xảy ra khi cross-origin request không phải "simple request":

- Method không phải GET/HEAD/POST
- Có custom headers (Authorization, x-inface-api-key, ...)
- Content-Type không phải `text/plain`, `multipart/form-data`, `application/x-www-form-urlencoded`

Browser gửi OPTIONS trước → server trả CORS headers → browser quyết định gửi actual request hay không.

---

### Câu 9 — Đáp án:

```
Access-Control-Allow-Origin: https://www.feelfree.com
Access-Control-Max-Age: 86400
Access-Control-Allow-Headers: Content-Type, x-inface-api-key
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
```

**Lưu ý**: Không dùng `*` cho Allow-Origin nếu cần credentials. Max-Age `86400` = 24 giờ (nhưng Chrome thực tế cap ở 7200 = 2 giờ).

---

### Câu 10 — **Đúng** ✅

Đây chính là vấn đề "CORS Resource Waste". Server nhận request, xử lý đầy đủ (business logic, DB query, ...), trả response với status 200 — nhưng nếu response thiếu `Access-Control-Allow-Origin` header, browser sẽ:

1. Nhận response
2. Kiểm tra CORS headers
3. Thấy thiếu → **block response**
4. Throw TypeError cho JavaScript

→ Tất cả server processing đều lãng phí.

---

### Câu 11 — Đáp án:

**Tại sao không hoạt động?**

Theo CORS specification, khi `Access-Control-Allow-Credentials: true`, `Access-Control-Allow-Origin` **KHÔNG được** là `*` (wildcard). Lý do bảo mật: wildcard + credentials = bất kỳ website nào đều có thể gửi authenticated request đến server → nguy hiểm.

**Cách fix:**

```
Access-Control-Allow-Origin: https://www.feelfree.com
Access-Control-Allow-Credentials: true
```

Server phải **đọc `Origin` header** từ request và set **exact origin** (sau khi validate) vào response. Dynamic origin matching:

```javascript
const allowedOrigins = [
	'https://www.feelfree.com',
	'https://dev.feelfree.com',
];
const origin = req.headers.origin;
if (allowedOrigins.includes(origin)) {
	res.header('Access-Control-Allow-Origin', origin);
	res.header('Access-Control-Allow-Credentials', 'true');
}
```

---

### Câu 12 — **B. CloudFront route cả frontend và API dưới cùng domain → same-origin**

```
https://www.feelfree.com/        → S3 (frontend static files)
https://www.feelfree.com/api/*   → ALB → EKS (backend)
```

Cả hai cùng domain `www.feelfree.com`, cùng protocol `https`, cùng port `443` → **same origin!** Browser không trigger CORS cho same-origin requests.

Đây là giải pháp "Same-origin deployment" — triệt để loại bỏ CORS bằng reverse proxy routing.

---

### Câu 13 — Đáp án:

**1.** Có, mỗi call trigger preflight vì header `Authorization` là custom header → request không phải "simple request".

**2.** Không cache: 30 API calls × 2 = **60 HTTP requests** (30 OPTIONS + 30 actual)

**3.** Với Max-Age 3600: 30 + 1 = **31 requests** (1 OPTIONS lần đầu, cache 1 giờ, + 30 actual). Giảm **48%** (29 requests).

**4.** Chrome cap max-age ở **7200 giây (2 giờ)**, bất kể server set bao nhiêu. Firefox cho phép tối đa 86400 giây.

---

### Câu 14 — Đáp án:

| Giải pháp                    | Ưu điểm                                                             | Nhược điểm                                                                    | Khi nào dùng?                          |
| ---------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------- |
| **Vite Proxy**               | Setup đơn giản (vài dòng config), bypass CORS hoàn toàn, hot reload | Chỉ dùng dev, behavior khác production, phải test lại CORS trên staging       | Dev environment, prototyping nhanh     |
| **Server-side CORS headers** | Chuẩn spec, hoạt động mọi nơi, linh hoạt (per-route config)         | Cần config đúng (dễ sai), preflight overhead, phải handle OPTIONS             | Production API mà FE ở domain khác     |
| **Same-origin deploy**       | Triệt tiêu CORS, performance tốt nhất, đơn giản nhất                | Cần reverse proxy (CloudFront/Nginx), infra phức tạp hơn, couple FE+BE domain | Khi control cả FE và BE infrastructure |

---

### Câu 15 — Đáp án:

**1.** Lỗi ở **server** — server không handle OPTIONS method.

**2.** Browser gửi preflight OPTIONS request, nhưng server trả **405 Method Not Allowed** → server không hỗ trợ OPTIONS method cho endpoint này.

**3.** Fix server để handle OPTIONS:

```javascript
// Express.js
app.options('/articles', cors()); // Enable preflight for this route
// Hoặc global:
app.options('*', cors()); // Enable preflight for all routes
```

```nginx
# Nginx
if ($request_method = 'OPTIONS') {
    add_header 'Access-Control-Allow-Origin' '$http_origin';
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
    add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type';
    add_header 'Access-Control-Max-Age' '86400';
    return 204;
}
```

---

### Câu 16 — Đáp án:

**1. CORS Policy cho API Gateway:**

```yaml
cors:
  allowed_origins:
    - https://dev.example.com
    - https://staging.example.com
    - https://www.example.com
  allowed_methods: [GET, POST, PUT, DELETE, PATCH, OPTIONS]
  allowed_headers: [Authorization, Content-Type, X-Request-ID]
  allow_credentials: true
  max_age: 7200 # Chrome max
```

**2. Dynamic origins:** Gateway đọc `Origin` header, check against allowlist, nếu match thì set `Access-Control-Allow-Origin` = request origin. KHÔNG dùng `*` vì cần credentials.

```
if request.Origin in allowed_origins:
    response.headers["Access-Control-Allow-Origin"] = request.Origin
```

**3. Request flow:**

```
Browser → DNS → API Gateway:443
  → WAF check (IP, rate limit)
  → CORS middleware (check origin, handle OPTIONS)
  → Auth middleware (validate JWT)
  → Route to Service A/B/C/D/E
  → Response + CORS headers
→ Browser receives response
```

**4. Mobile app:** Mobile native HTTP clients không có Same-Origin Policy, nên CORS headers được **bỏ qua** (ignored). CORS config trên Gateway không ảnh hưởng mobile. Nhưng vẫn cần authentication (JWT/API key) cho cả mobile và web.

---

### Câu 17 — Đáp án:

**1.** 100k users × 20 calls × 2 (preflight) = **4,000,000 requests/minute** = **~66,667 requests/second**. Trong đó 50% là OPTIONS preflight = **~33,333 wasted requests/second**.

**2.** Ba cách giảm tải:

- **Preflight caching**: `Access-Control-Max-Age: 7200` → giảm ~95%+ preflight
- **Simple requests khi có thể**: Dùng `GET` + query params thay vì POST + JSON body cho read operations (tránh trigger preflight)
- **Batch API calls**: Gom nhiều requests nhỏ thành 1 request lớn (GraphQL hoặc custom batch endpoint)

**3.** Sau khi preflight cache: ~100k × 21 requests = **2,100,000 requests/minute** (giảm ~47%). Nếu kết hợp batching (20 calls → 5 calls): ~100k × 6 = **600,000 requests/minute** (giảm ~85%).

**4.** Server-side: Middleware kiểm tra origin ở đầu pipeline → reject sớm trước khi chạy business logic. CDN cache responses → giảm origin hits. Connection pooling → reduce DB connection overhead.

---

### Câu 18 — Đáp án:

**1. Ba rủi ro bảo mật:**

- **CSRF potential**: Bất kỳ website nào đều có thể gửi request đến API. Nếu API rely on cookies → CSRF attack vector mở rộng.
- **Data exposure**: Sensitive API endpoints (user data, admin endpoints) accessible từ bất kỳ origin → information leakage.
- **Phishing amplification**: Attacker tạo website giả, gọi API `*` → lấy real data → tăng tính thuyết phục của phishing.

**2. Cấu hình an toàn hơn:**

```javascript
const ALLOWED_ORIGINS = [
	'https://www.feelfree.com',
	'https://dev.feelfree.com',
	'https://test.feelfree.com',
];

app.use((req, res, next) => {
	const origin = req.headers.origin;
	if (ALLOWED_ORIGINS.includes(origin)) {
		res.header('Access-Control-Allow-Origin', origin);
		res.header('Vary', 'Origin'); // QUAN TRỌNG: cho CDN cache đúng
	}
	next();
});
```

**3. Ba trường hợp `*` OK:**

- **Public API** không yêu cầu auth (ví dụ: weather API, public dataset)
- **Static assets** CDN (fonts, images, CSS từ CDN)
- **Development/staging** environment (không có production data)

**4.** Theo [Fetch Standard](https://fetch.spec.whatwg.org/#cors-protocol-and-credentials): Khi `credentials: "include"`, nếu `Access-Control-Allow-Origin` là `*`, browser **PHẢI** reject response. Lý do: `*` + credentials = bất kỳ site nào gửi authenticated request → credential theft vector. Spec yêu cầu **explicit origin** khi có credentials.

---

### Câu 19 — Đáp án:

**1.** CloudFront là **Reverse Proxy**. User không biết request đang đi đến S3 hay ALB — CloudFront ẩn backend infrastructure. Forward proxy ẩn identity của client, Reverse proxy ẩn identity của server.

**2.** Inface Gateway xử lý CORS cho QuickBoard/Portfolio API calls từ browser. Gateway set `Access-Control-Allow-Origin` header → browser cho phép cross-origin response. Ngoài ra, Gateway handle authentication (API key verification) và rate limiting.

**3.** Browser nhận **403 Forbidden** từ WAF. CloudFront forward WAF response về browser. Developer sẽ thấy 403 trong Network tab — cần check IP allowlist trong WAF console.

**4.** QuickBoard API ở domain `api.feelfree.com`, thuộc **feelfree Infra** (không nằm trong Feel Free VPC). CloudFront của Feel Free chỉ route đến S3 và ALB trong cùng AWS account. Để proxy QuickBoard qua CloudFront, cần thêm custom origin — nhưng hiện tại Inface Gateway đã handle CORS, nên direct call là giải pháp đơn giản hơn.

---

### Câu 20 — Đáp án:

**1. Pseudo-code middleware chain:**

```
handleRequest(req, res):
    // 1. Logging
    log(req.method, req.url, req.headers.origin)
    startTime = now()

    // 2. CORS
    if req.headers.origin:
        res.headers["Access-Control-Allow-Origin"] = req.headers.origin
        res.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        res.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    if req.method == "OPTIONS":
        return res.status(204).end()

    // 3. Rate Limit
    clientIP = req.remoteAddr
    if rateLimiter.isExceeded(clientIP):
        return res.status(429).json({ error: "Too many requests" })

    // 4. Proxy
    targetURL = "https://api.feelfree.com" + req.path
    proxyRes = httpClient.forward(req, targetURL)
    res.status(proxyRes.status).body(proxyRes.body)

    // Logging (end)
    log("completed", now() - startTime)
```

**2.** Proxy server gửi request đến API server bằng **server-to-server HTTP call** (giống Postman/curl). Không có browser context → không có Same-Origin Policy → CORS không áp dụng. Proxy nhận response, thêm CORS headers, rồi trả về browser.

**3.** **KHÔNG nên** dùng CORS proxy trong production vì:

- Thêm một layer (latency + single point of failure)
- Security risk (proxy có thể bị abuse)
- Đúng cách là fix CORS ở source (API server hoặc API Gateway)
- Maintainability: thêm infra cần maintain

**4. Ba security concerns:**

- **Open relay**: Nếu proxy không restrict target URLs, attacker dùng proxy làm relay → SSRF (Server-Side Request Forgery) → truy cập internal services
- **Data sniffing**: Proxy thấy all request/response data (headers, body) → exposure risk nếu proxy bị compromise
- **Abuse**: Free CORS proxy bị dùng cho DDoS, spam, hoặc bypass content restrictions

---

## 📊 Scoring Guide

| Cấp độ         | Số câu | Điểm/câu | Tổng    | Pass threshold |
| -------------- | ------ | -------- | ------- | -------------- |
| Easy (1-5)     | 5      | 10       | 50      | ≥ 40           |
| Medium (6-10)  | 5      | 15       | 75      | ≥ 50           |
| Hard (11-15)   | 5      | 20       | 100     | ≥ 60           |
| Expert (16-20) | 5      | 25       | 125     | ≥ 75           |
| **Tổng**       | **20** | —        | **350** | **≥ 225**      |

### Đánh giá:

| Điểm    | Level               | Nhận xét                                                           |
| ------- | ------------------- | ------------------------------------------------------------------ |
| 300-350 | 🏆 **Expert**       | Nắm vững CORS/Proxy, sẵn sàng thiết kế hệ thống distributed        |
| 225-299 | ✅ **Proficient**   | Kiến thức solid, cần strengthen edge cases                         |
| 150-224 | 📚 **Intermediate** | Hiểu cơ bản, cần research thêm production patterns                 |
| < 150   | 🔰 **Beginner**     | Review lại [CORS & Proxy Deep Dive](./cors-and-proxy-deep-dive.md) |

---

> 📝 **Note**: Quiz này được thiết kế dựa trên kiến trúc thực tế của Feel Free Frontend (feelfree) và CORS/Proxy documentation. Các câu hỏi expert level yêu cầu hiểu sâu về both browser behavior và server infrastructure.