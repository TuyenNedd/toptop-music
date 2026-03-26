# TikTok Music Web -- Technical Plan

## 1. Mục tiêu & Phạm vi

Xây dựng web nghe nhạc dựa trên sound TikTok, ưu tiên: - Phát đúng audio
TikTok đã encode để cảm giác nghe ≈ trong app. - Tập trung vào top
trending sounds, stream nhanh.

**Hình thức:** - Web tự host, có whitelist (chỉ người quen có
key/account mới dùng). - Phi thương mại, phục vụ trải nghiệm cá
nhân/nhóm nhỏ.

**Ý tưởng chính:** - Pre-cache audio cho top trending. - Các bài khác:
chỉ cache metadata, khi user nghe mới download/stream on-demand.

> ⚠️ Lưu ý: Về mặt ToS và bản quyền, mọi giải pháp đều nằm ở vùng
> non-official, cần tự chịu rủi ro.

------------------------------------------------------------------------

## 2. Kiến trúc tổng thể

### 2.1 Thành phần

**Backend:** - Service A -- Trending Fetcher - Service B -- Audio
Downloader / Cache - Service C -- Main API

**Database:** Postgres / MySQL / MongoDB\
**Storage:** Local (`sounds/`) hoặc S3\
**Frontend:** Next.js / React

------------------------------------------------------------------------

## 3. Data Model & DB Schema

### 3.1 Bảng `sounds`

``` sql
CREATE TABLE sounds (
  id UUID PRIMARY KEY,
  tiktok_sound_id VARCHAR(255) UNIQUE NOT NULL,
  title VARCHAR(512),
  artist VARCHAR(512),
  cover_url TEXT,
  duration_seconds INT,
  usage_count BIGINT,
  trend_rank INT,
  cached BOOLEAN DEFAULT FALSE,
  file_path TEXT,
  last_trending_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3.2 Bảng `whitelist_tokens`

``` sql
CREATE TABLE whitelist_tokens (
  id UUID PRIMARY KEY,
  token VARCHAR(255) UNIQUE NOT NULL,
  label VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  revoked BOOLEAN DEFAULT FALSE
);
```

------------------------------------------------------------------------

## 4. Services & Flow

### 4.1 Trending Fetcher

-   Cron job (30--60 phút)
-   Fetch trending sounds
-   Upsert vào DB

``` ts
for (const s of trendingFromTikTok) {
  upsertSound({
    tiktok_sound_id: s.id,
    title: s.title,
    artist: s.artist,
    cover_url: s.cover,
    duration_seconds: s.duration,
    usage_count: s.usageCount,
    trend_rank: s.rank,
    last_trending_at: now()
  });
}
```

------------------------------------------------------------------------

### 4.2 Audio Downloader / Cache

#### Pre-cache top trending

``` ts
const targets = getTopUncachedSounds(N, M);
for (const sound of targets) {
  const audioUrl = await getAudioUrlFromTikTok(sound.tiktok_sound_id);
  const filePath = await downloadToLocal(audioUrl, `sounds/${sound.tiktok_sound_id}.m4a`);

  updateSound(sound.id, {
    cached: true,
    file_path: filePath
  });
}
```

#### On-demand

-   Mode A: cache rồi stream
-   Mode B: proxy stream (không lưu file)

------------------------------------------------------------------------

### 4.3 Main API

#### Auth

-   Header: `x-api-key`
-   Check whitelist

#### Endpoint: `/api/trending`

``` json
[
  {
    "title": "Sound A",
    "trend_rank": 1,
    "cached": true
  }
]
```

#### Endpoint: `/api/stream/:soundId`

-   Nếu cached → stream file
-   Nếu chưa → download hoặc proxy

------------------------------------------------------------------------

## 5. Frontend

### Trending Page

-   Hiển thị list sound
-   Icon cached / chưa cached
-   Play qua `<audio>`

### Search Page

-   Query theo title/artist
-   Stream như trên

------------------------------------------------------------------------

## 6. Rủi ro

### 6.1 Rủi ro

-   Vi phạm TikTok ToS
-   Bản quyền âm nhạc

### 6.2 Giảm thiểu

-   Chỉ dùng nội bộ
-   Không public
-   Rate limit
-   Không cho download trực tiếp

------------------------------------------------------------------------

## 7. Hướng triển khai

1.  Thiết kế DB chi tiết
2.  Viết backend (Node.js/NestJS)
3.  Test TikTok API
4.  Build UI Next.js
