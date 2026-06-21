HEAD:

- tham chiếu tới branch ở 1 thời điểm
- "active" hoặc "current" branch, tương đương branch highlight khi `git branch`
- kiểm tra HEAD `cat .git/HEAD`

Detached HEAD (HEAD tách rời):

- không tham chiếu tới branch
- tham chiếu tới 1 SHA-1 version khi checkout commit, tag,...

How `git checkout works?`:

- nhảy sang 1 nhánh khác
- khôi phục những thay đổi đó vào repo hiện tại

Vấn đề với `detached HEAD`

- HEAD trỏ tới trạng thái làm việc hiện tại (thường là 1 nhánh cụ thể)
- Khi checkout sang 1 nhánh khác, git di chuyển con trỏ HEAD tới nhánh đó
- HEAD luôn trỏ tới commit mới nhất, cả khi tạo commit

- Khi checkout với commit hash, HEAD lúc này sẽ là detached HEAD
- Khi tạo commit thì những thay đổi đó không đại diện cho bất kỳ nhánh nào

Khi nào `detached HEAD` xuất hiện

- Khi checkout tới 1 commit hash, tag,...
- Trong quá trình `rebase` cũng xuất hiện tạm thời `detached HEAD` 

Khi nào `detached HEAD` không xuất hiện

- Tạo mới nhánh dựa trên commit hash, sau khi làm xong thì xóa bỏ nhánh đó