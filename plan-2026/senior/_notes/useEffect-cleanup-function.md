Nếu đứng ở góc nhìn của một Senior Frontend thì mình sẽ không bắt đầu từ `useEffect`, mà bắt đầu từ **triết lý của React**.

## 1. React chỉ làm 1 việc: Đồng bộ UI với State

React hoạt động theo vòng đời như sau:

```text
State thay đổi
      │
      ▼
Render (tính toán Virtual DOM)
      │
      ▼
Commit (update DOM)
      │
      ▼
Chạy Effect (đồng bộ với thế giới bên ngoài)
```

Điểm quan trọng:

> **Effect KHÔNG phải là một phần của Render.**

Render chỉ tính UI.

Effect dùng để đồng bộ với những thứ bên ngoài React:

- Event Listener
- Timer
- WebSocket
- API
- LocalStorage
- Animation
- ...

---

# 2. Effect thực chất là "Setup"

Ví dụ:

```jsx
useEffect(() => {
  window.addEventListener('resize', handleResize);
}, []);
```

Bản chất React hiểu là:

```text
Setup:

Đăng ký resize listener
```

Nếu đã có Setup...

thì phải có...

```text
Teardown (Cleanup)

Remove resize listener
```

Giống như:

```text
Mở file
↓

Đọc file

↓

Đóng file
```

Hay

```text
Connect Database

↓

Query

↓

Disconnect
```

Cleanup đơn giản là bước **Undo** những gì Effect đã Setup.

---

# 3. Tại sao phải Cleanup?

Ví dụ:

```jsx
useEffect(() => {
  window.addEventListener('resize', handleResize);
}, [theme]);
```

Giả sử:

```text
theme = light

↓

theme = dark

↓

theme = blue
```

Nếu React KHÔNG cleanup thì:

```text
Render 1

+ resize listener #1

Render 2

+ resize listener #2

Render 3

+ resize listener #3
```

Kết quả:

```text
Resize một lần

↓

listener #1 chạy

listener #2 chạy

listener #3 chạy
```

=> Bug.

---

Có Cleanup:

```text
Render 1

+ Listener #1

↓

Render 2

- Remove Listener #1

+ Add Listener #2

↓

Render 3

- Remove Listener #2

+ Add Listener #3
```

Luôn chỉ có **1 listener**.

---

# 4. Tại sao Cleanup chạy TRƯỚC Effect mới?

Đây là câu hỏi hay nhất.

Giả sử React làm thế này:

```text
Effect mới

↓

Cleanup cũ
```

Thì sẽ có khoảng thời gian:

```text
Listener cũ

+

Listener mới
```

Đều đang tồn tại.

Ví dụ:

```text
Old WebSocket

+

New WebSocket
```

Hay

```text
Old Interval

+

New Interval
```

Hay

```text
Old Subscription

+

New Subscription
```

=> Có overlap.

React không muốn điều đó.

Nó đảm bảo:

```text
Old Effect

↓

Cleanup hoàn toàn

↓

New Effect
```

Không bao giờ có hai Effect cùng sống.

---

# 5. React coi mỗi Render là một thế giới riêng

Đây là tư duy quan trọng nhất.

Developer thường nghĩ:

```text
Có một Effect

↓

Effect được update
```

React KHÔNG nghĩ vậy.

React nghĩ:

```text
Render #1

↓

Effect #1
```

Sau đó:

```text
Render #2

↓

Effect #2
```

Hai Effect hoàn toàn khác nhau.

Ví dụ:

```jsx
useEffect(() => {
  console.log(count);

  return () => {
    console.log('cleanup', count);
  };
}, [count]);
```

Nếu:

```text
count = 1

↓

count = 2

↓

count = 3
```

React làm:

```text
Effect(count=1)

↓

Cleanup(count=1)

↓

Effect(count=2)

↓

Cleanup(count=2)

↓

Effect(count=3)
```

Lưu ý:

Cleanup luôn "nhớ" đúng giá trị của render đã tạo ra nó.

---

# 6. Vì sao React thiết kế như vậy?

Bởi vì Closure.

Ví dụ:

```jsx
useEffect(() => {
  console.log(count);
}, [count]);
```

Render đầu tiên:

```text
count = 1
```

Effect nhận được:

```text
count = 1
```

Render tiếp:

```text
count = 2
```

Effect mới nhận:

```text
count = 2
```

Hai Effect không share dữ liệu.

```text
Render 1
──────────────
count = 1
Effect #1

Render 2
──────────────
count = 2
Effect #2
```

Điều này giúp tránh rất nhiều bug liên quan đến giá trị cũ (stale closure).

---

# 7. Có thể xem Effect như một Resource

Đây là cách mình hay giải thích cho Junior.

Mỗi Effect tạo ra một Resource.

Ví dụ:

```text
EventListener
Timer
Socket
Fetch
Subscription
Observer
Animation
```

Resource luôn có vòng đời:

```text
Create

↓

Use

↓

Destroy
```

React chỉ đang tự động quản lý vòng đời đó.

```text
          Dependency thay đổi
                 │
                 ▼
        Cleanup Resource cũ
                 │
                 ▼
        Tạo Resource mới
```

---

# 8. Sơ đồ tổng kết

```text
          Render #1
               │
               ▼
        Commit DOM
               │
               ▼
      Setup Effect #1
               │
               │
        State thay đổi
               │
               ▼
          Render #2
               │
               ▼
        Commit DOM
               │
               ▼
     Cleanup Effect #1
               │
               ▼
      Setup Effect #2
               │
               │
        State thay đổi
               │
               ▼
          Render #3
               │
               ▼
        Commit DOM
               │
               ▼
     Cleanup Effect #2
               │
               ▼
      Setup Effect #3
```

## Góc nhìn của Senior

Mình thường không xem `useEffect` là "chạy sau render", mà xem nó như một **Resource Manager**.

- **Render** chỉ có nhiệm vụ mô tả UI.
- **Effect** có nhiệm vụ thiết lập (setup) kết nối với thế giới bên ngoài.
- **Cleanup** có nhiệm vụ tháo gỡ (teardown) mọi thứ mà effect trước đã thiết lập.
- Mỗi lần dependencies thay đổi, React **không cập nhật effect cũ**, mà **hủy effect cũ rồi tạo effect mới**.

Tư duy này giải thích được gần như toàn bộ hành vi của `useEffect`: vì sao cần cleanup, vì sao cleanup chạy trước effect mới, vì sao mỗi effect "nhớ" đúng state của lần render đã tạo ra nó, và vì sao React tránh được các lỗi như listener bị đăng ký nhiều lần, timer chạy trùng, hoặc subscription bị chồng chéo.
